"""Amadeus TEST only: authentication and direct one-way flight offers.

This adapter cannot reach production, make bookings or return live-labelled prices.
"""
import json
import os
import time
from datetime import date
from decimal import Decimal, InvalidOperation
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, build_opener, HTTPRedirectHandler

BASE_URL = 'https://test.api.amadeus.com'
DEFAULT_ORIGINS = ('SCQ', 'LCG', 'VGO', 'OPO', 'MAD')


class ProviderError(Exception):
    pass


class MissingCredentials(ProviderError):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def transport(method, url, headers, body):
    req = Request(url, data=body, headers=headers, method=method)
    try:
        with build_opener(NoRedirect).open(req, timeout=15) as response:
            return json.load(response)
    except HTTPError as exc:
        messages = {401: 'Credenciales de prueba rechazadas.',
                    403: 'Acceso de prueba no autorizado.',
                    429: 'Cuota o límite de pruebas alcanzado; no se reintenta.'}
        raise ProviderError(messages.get(exc.code, 'La API de pruebas no pudo completar la consulta.')) from None
    except (URLError, TimeoutError, ValueError):
        raise ProviderError('No se pudo obtener una respuesta válida de la API de pruebas.') from None


class AmadeusTest:
    def __init__(self, key, secret, request_limit=20, request_transport=transport, clock=time.monotonic):
        if not key or not secret:
            raise MissingCredentials('Faltan AMADEUS_TEST_API_KEY y AMADEUS_TEST_API_SECRET en el entorno del backend.')
        if type(request_limit) is not int or request_limit < 1:
            raise ValueError('Límite de consultas no válido.')
        self._key, self._secret = key, secret
        self._transport, self._clock = request_transport, clock
        self._token, self._expires = None, 0
        self.request_limit, self.requests_used = request_limit, 0

    @classmethod
    def from_environment(cls, **kwargs):
        return cls(os.environ.get('AMADEUS_TEST_API_KEY'), os.environ.get('AMADEUS_TEST_API_SECRET'), **kwargs)

    def _request(self, method, path, headers, body=None):
        if self.requests_used >= self.request_limit:
            raise ProviderError('Límite local de consultas alcanzado; no se han enviado más peticiones.')
        self.requests_used += 1
        return self._transport(method, BASE_URL + path, headers, body)

    def _access_token(self):
        if self._token and self._clock() < self._expires:
            return self._token
        body = urlencode({'grant_type': 'client_credentials', 'client_id': self._key,
                          'client_secret': self._secret}).encode()
        data = self._request('POST', '/v1/security/oauth2/token',
                             {'Content-Type': 'application/x-www-form-urlencoded'}, body)
        try:
            token, lifetime = data['access_token'], int(data['expires_in'])
            if not isinstance(token, str) or not token or lifetime <= 0:
                raise ValueError()
        except (KeyError, TypeError, ValueError):
            raise ProviderError('La autenticación de prueba devolvió una respuesta incompleta.') from None
        self._token = token
        self._expires = self._clock() + max(0, lifetime - 30)
        return token

    def search_direct(self, origin, destination, departure_date, party, max_results=20):
        from optimizer import airport
        airport(origin); airport(destination)
        try:
            if date.fromisoformat(departure_date).isoformat() != departure_date:
                raise ValueError()
        except (TypeError, ValueError):
            raise ValueError('Fecha de salida no válida.') from None
        if origin == destination or type(max_results) is not int or not 1 <= max_results <= 50:
            raise ValueError('Ruta o número de ofertas no válido.')
        adults = party.adults + sum(age >= 12 for age in party.child_ages)
        children = sum(2 <= age < 12 for age in party.child_ages)
        infants = sum(age < 2 for age in party.child_ages)
        if infants > party.adults:
            raise ValueError('Esta primera integración requiere un adulto acompañante por bebé.')
        params = {'originLocationCode': origin, 'destinationLocationCode': destination,
                  'departureDate': departure_date, 'adults': adults, 'children': children,
                  'infants': infants, 'nonStop': 'true', 'currencyCode': 'EUR', 'max': max_results}
        token = self._access_token()
        raw = self._request('GET', '/v2/shopping/flight-offers?' + urlencode(params),
                            {'Authorization': 'Bearer ' + token})
        if not isinstance(raw, dict) or not isinstance(raw.get('data'), list):
            raise ProviderError('El proveedor no devolvió una lista válida de ofertas de prueba.')
        offers = []
        for item in raw['data']:
            offer = normalize(item, origin, destination, party)
            if offer:
                offers.append(offer)
        return {'status': 'test', 'source': 'Amadeus TEST', 'origin': origin,
                'destination': destination, 'offers': offers,
                'notice': 'Datos de prueba: no confirman precios ni plazas reales. No incluyen cobertura completa de low cost.'}


def normalize(item, origin, destination, party):
    """Keep full-party test totals; never split a through fare into made-up leg prices."""
    try:
        itineraries = item['itineraries']
        if len(itineraries) != 1 or len(itineraries[0]['segments']) != 1:
            return None
        segment = itineraries[0]['segments'][0]
        if segment['departure']['iataCode'] != origin or segment['arrival']['iataCode'] != destination:
            return None
        pricing = item['travelerPricings']
        if len(pricing) != party.size or len({p['travelerId'] for p in pricing}) != party.size:
            return None
        expected = {'ADULT': party.adults + sum(a >= 12 for a in party.child_ages),
                    'CHILD': sum(2 <= a < 12 for a in party.child_ages),
                    'HELD_INFANT': sum(a < 2 for a in party.child_ages)}
        actual = {kind: sum(p['travelerType'] == kind for p in pricing) for kind in expected}
        if actual != expected or item['price']['currency'] != 'EUR':
            return None
        total = Decimal(item['price'].get('grandTotal', item['price']['total']))
        cents = total * 100
        if not total.is_finite() or total <= 0 or cents != cents.to_integral_value():
            return None
        bags = [p.get('fareDetailsBySegment', [{}])[0].get('includedCheckedBags') for p in pricing]
        return {'id': item['id'], 'status': 'test', 'source': 'Amadeus TEST',
                'currency': 'EUR', 'totalMinor': int(cents),
                'party': {'adults': party.adults, 'childAges': list(party.child_ages)},
                'baggage': {'includedCheckedBagsByTraveler': bags, 'supplementsKnown': False},
                'legs': [{'origin': origin, 'destination': destination,
                          'departureLocal': segment['departure']['at'],
                          'arrivalLocal': segment['arrival']['at'],
                          'carrier': segment['carrierCode'], 'flightNumber': segment['number']}],
                'eligibleForLiveRanking': False,
                'scheduleNotice': 'Horas locales: requieren resolver la zona horaria antes de cruzar conexiones.'}
    except (KeyError, TypeError, IndexError, InvalidOperation, ValueError):
        return None
