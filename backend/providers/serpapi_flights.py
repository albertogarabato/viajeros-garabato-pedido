"""SerpApi Google Flights adapter. Backend only; no reservations or upgrades."""
import json
import time
from datetime import date
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError


class ProviderError(Exception):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def transport(path, params):
    # Never log this URL: SerpApi requires its private key as a query parameter.
    try:
        request = Request('https://serpapi.com' + path + '?' + urlencode(params),
                          headers={'Accept': 'application/json'})
        with build_opener(NoRedirect).open(request, timeout=90) as response:
            return json.load(response)
    except HTTPError as exc:
        raise ProviderError({401: 'Clave de SerpApi rechazada.', 429: 'Cuota o límite de SerpApi alcanzado.'}.get(
            exc.code, 'SerpApi no pudo completar la consulta.')) from None
    except (URLError, TimeoutError, ValueError):
        raise ProviderError('No se recibió una respuesta válida de SerpApi.') from None


class SerpApiFlights:
    def __init__(self, api_key, request_limit=5, request_transport=transport, clock=time.monotonic):
        if not api_key:
            raise ProviderError('Falta la clave privada de SerpApi en el backend.')
        if type(request_limit) is not int or request_limit < 1:
            raise ValueError('Límite de consultas no válido.')
        self._key, self._transport, self._clock = api_key, request_transport, clock
        self._cache = {}
        self.request_limit, self.requests_used = request_limit, 0

    def account_summary(self):
        raw = self._transport('/account.json', {'api_key': self._key})
        fields = ('account_status', 'plan_name', 'plan_monthly_price', 'searches_per_month',
                  'plan_searches_left', 'this_month_usage', 'plan_renewal_date')
        # Do not return account email, API key or raw account response.
        return {key: raw.get(key) for key in fields}

    def one_way(self, origins, destination, departure_date, adults, children=0,
                infants_on_lap=0, infants_in_seat=0, nonstop=True):
        from optimizer import airport
        if not origins or len(origins) > 5 or len(set(origins)) != len(origins):
            raise ValueError('Selecciona entre uno y cinco orígenes distintos.')
        for code in origins: airport(code)
        airport(destination)
        if destination in origins:
            raise ValueError('Destino igual a un origen.')
        try:
            if date.fromisoformat(departure_date).isoformat() != departure_date:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValueError('Fecha de salida no válida.') from None
        counts = (adults, children, infants_on_lap, infants_in_seat)
        if (any(type(n) is not int or n < 0 for n in counts) or adults < 1 or
                sum(counts) > 9 or infants_on_lap > adults):
            raise ValueError('Composición de viajeros no válida.')
        params = {'engine': 'google_flights', 'departure_id': ','.join(origins),
                  'arrival_id': destination, 'outbound_date': departure_date, 'type': 2,
                  'adults': adults, 'children': children, 'infants_on_lap': infants_on_lap,
                  'infants_in_seat': infants_in_seat, 'currency': 'EUR', 'hl': 'es', 'gl': 'es',
                  'stops': 1 if nonstop else 2, 'deep_search': 'true'}
        cache_key = json.dumps(params, sort_keys=True)
        cached = self._cache.get(cache_key)
        if cached and self._clock() - cached[0] < 900:
            return json.loads(cached[1])
        if self.requests_used >= self.request_limit:
            raise ProviderError('Límite local alcanzado; no se han enviado más búsquedas.')
        account = self.account_summary()
        if (account['account_status'] != 'Active' or account['plan_monthly_price'] != 0 or
                not isinstance(account['plan_searches_left'], int) or account['plan_searches_left'] < 1):
            raise ProviderError('La búsqueda está limitada a una cuenta gratuita activa con cuota disponible.')
        self.requests_used += 1
        data = self._transport('/search.json', dict(params, api_key=self._key))
        if data.get('error') or data.get('search_metadata', {}).get('status') != 'Success':
            raise ProviderError('La fuente no completó la búsqueda. No se reintenta automáticamente.')
        echoed = data.get('search_parameters', {})
        for key, default in [('adults', 1), ('children', 0), ('infants_on_lap', 0), ('infants_in_seat', 0)]:
            if str(echoed.get(key, default)) != str(params[key]):
                raise ProviderError('La respuesta no corresponde al grupo solicitado.')
        if echoed.get('currency') != 'EUR' or str(echoed.get('type')) != '2':
            raise ProviderError('Moneda o tipo de viaje inesperados; no se comparan precios.')
        observed_at = data.get('search_metadata', {}).get('created_at')
        offers, seen = [], set()
        for item in data.get('best_flights', []) + data.get('other_flights', []):
            offer = normalize(item, origins, destination, departure_date, nonstop, observed_at)
            if offer:
                identity = json.dumps(offer['legs'], sort_keys=True) + str(offer['displayedPriceMinor'])
                if identity not in seen:
                    seen.add(identity); offers.append(offer)
        result = {'status': 'observed', 'source': 'SerpApi / Google Flights',
                  'requestedPassengers': dict(zip(('adults','children','infantsOnLap','infantsInSeat'), counts)),
                  'offers': sorted(offers, key=lambda o: o['displayedPriceMinor']),
                  'coverage': 'Solo resultados devueltos por Google Flights; no todas las aerolíneas.',
                  'notice': 'Precio observado para la consulta. Plazas, base del precio familiar y suplementos requieren comprobación antes de reservar.'}
        self._cache[cache_key] = (self._clock(), json.dumps(result))
        return result


def normalize(item, origins, destination, departure_date, nonstop, observed_at):
    try:
        flights = item['flights']
        if not flights or (nonstop and len(flights) != 1) or len(flights) > 2:
            return None
        if (flights[0]['departure_airport']['id'] not in origins or
                flights[-1]['arrival_airport']['id'] != destination or
                not flights[0]['departure_airport']['time'].startswith(departure_date)):
            return None
        for a, b in zip(flights, flights[1:]):
            if a['arrival_airport']['id'] != b['departure_airport']['id']:
                return None
        amount = Decimal(str(item['price'])) * 100
        if not amount.is_finite() or amount <= 0 or amount != amount.to_integral_value():
            return None
        legs = [{'origin': f['departure_airport']['id'], 'destination': f['arrival_airport']['id'],
                 'departureLocal': f['departure_airport']['time'], 'arrivalLocal': f['arrival_airport']['time'],
                 'airline': f.get('airline'), 'flightNumber': f.get('flight_number')} for f in flights]
        return {'source': 'SerpApi / Google Flights', 'status': 'observed',
                'currency': 'EUR', 'displayedPriceMinor': int(amount), 'checkedAt': observed_at,
                'durationMinutes': item.get('total_duration'), 'legs': legs,
                'baggageSupplementsKnown': False, 'connectionProtection': 'unverified',
                'eligibleForVerifiedRanking': False}
    except (KeyError, TypeError, InvalidOperation, ValueError):
        return None
