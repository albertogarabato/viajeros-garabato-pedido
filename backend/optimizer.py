"""Generic flight connection engine. No provider calls, prices or credentials embedded."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Tuple
import re


def instant(value):
    d = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if d.tzinfo is None or d.utcoffset() is None:
        raise ValueError('Las horas deben incluir zona horaria.')
    return d


def airport(value):
    if not re.fullmatch('[A-Z]{3}', value):
        raise ValueError('Código de aeropuerto no válido.')
    return value


@dataclass(frozen=True)
class Party:
    adults: int
    child_ages: Tuple[int, ...] = ()

    def __post_init__(self):
        if type(self.adults) is not int or self.adults < 1:
            raise ValueError('Debe viajar al menos un adulto.')
        if any(type(a) is not int or not 0 <= a <= 17 for a in self.child_ages):
            raise ValueError('Edad de menor no válida.')
        object.__setattr__(self, 'child_ages', tuple(sorted(self.child_ages)))
        if not 1 <= self.size <= 9:
            raise ValueError('Entre 1 y 9 viajeros.')

    @property
    def size(self):
        return self.adults + len(self.child_ages)


@dataclass(frozen=True)
class Flight:
    """One directed flight, quoted for the entire exact party, in minor currency units."""
    id: str
    origin: str
    destination: str
    departure: str
    arrival: str
    amount_minor: int
    currency: str
    party: Party
    source: str
    checked_at: str
    expires_at: str
    baggage: str = 'basic'
    status: str = 'live'
    booking_url: str = ''

    def __post_init__(self):
        airport(self.origin)
        airport(self.destination)
        if self.origin == self.destination or not self.id or not self.source:
            raise ValueError('Tramo sin identidad o fuente válida.')
        if instant(self.arrival) <= instant(self.departure):
            raise ValueError('Llegada anterior a salida.')
        if type(self.amount_minor) is not int or self.amount_minor <= 0:
            raise ValueError('El total familiar debe ser un entero positivo en céntimos.')
        if not re.fullmatch('[A-Z]{3}', self.currency):
            raise ValueError('Moneda no válida.')
        if instant(self.expires_at) <= instant(self.checked_at):
            raise ValueError('Vigencia de la tarifa no válida.')


@dataclass(frozen=True)
class Itinerary:
    flights: Tuple[Flight, ...]

    def __post_init__(self):
        if not 1 <= len(self.flights) <= 2:
            raise ValueError('Esta versión admite directo o una conexión.')
        first = self.flights[0]
        for f in self.flights:
            if (f.party, f.currency, f.baggage) != (first.party, first.currency, first.baggage):
                raise ValueError('Los tramos deben tener viajeros, moneda y equipaje comparables.')
        for a, b in zip(self.flights, self.flights[1:]):
            if a.destination != b.origin or instant(b.departure) < instant(a.arrival):
                raise ValueError('Los tramos no enlazan en el mismo aeropuerto y horario.')

    @property
    def amount_minor(self):
        return sum(f.amount_minor for f in self.flights)

    @property
    def duration_minutes(self):
        return int((instant(self.flights[-1].arrival) - instant(self.flights[0].departure)).total_seconds() / 60)

    @property
    def independent(self):
        # Same airline is not evidence that separately quoted tickets are protected.
        return len(self.flights) > 1

    @property
    def connection_minutes(self):
        return tuple(int((instant(b.departure) - instant(a.arrival)).total_seconds() / 60)
                     for a, b in zip(self.flights, self.flights[1:]))


class SearchLimitExceeded(Exception):
    pass


def discover_paths(edges, origins, destinations):
    """Directed route graph: possible paths, never schedules, availability or fares.

    An edge is (origin, destination). Do not manufacture reverse directions.
    """
    graph = {}
    for a, b in edges:
        airport(a); airport(b)
        graph.setdefault(a, set()).add(b)
    targets = set(destinations)
    result = set()
    for start in origins:
        airport(start)
        for first in graph.get(start, set()):
            if first in targets:
                result.add((start, first))
            elif first != start:
                for end in graph.get(first, set()) & targets:
                    if end != start:
                        result.add((start, first, end))
    return sorted(result, key=lambda p: (len(p), p))


def search_one_way(flights, origins, destinations, start, end, party, now,
                   currency='EUR', baggage='basic', min_connection_minutes=180,
                   max_quote_age_minutes=30, max_evaluations=100000):
    """Join live per-leg quotes. start/end are inclusive departure instants.

    min_connection_minutes is a configurable screening margin, NOT an airport MCT
    or a guarantee. No maximum flight/layover duration is imposed.
    Test, historical, expired and incomplete-party quotes are never ranked as live.
    """
    if min_connection_minutes < 0 or max_quote_age_minutes <= 0 or max_evaluations < 1:
        raise ValueError('Límites de búsqueda no válidos.')
    start, end, now = instant(start), instant(end), instant(now)
    if end < start:
        raise ValueError('Intervalo de salida invertido.')
    origins, destinations = set(origins), set(destinations)
    usable, seen = [], set()
    for f in flights:
        key = (f.source, f.id)
        if key in seen:
            raise ValueError('Identificador de oferta duplicado en una fuente.')
        seen.add(key)
        checked = instant(f.checked_at)
        if (f.status == 'live' and f.party == party and f.currency == currency and
                f.baggage == baggage and checked <= now < instant(f.expires_at) and
                now - checked <= timedelta(minutes=max_quote_age_minutes) and
                instant(f.departure) > now):
            usable.append(f)
    adjacency = {}
    for f in usable:
        adjacency.setdefault(f.origin, []).append(f)
    result, evaluations = [], 0
    for origin in sorted(origins):
        for first in adjacency.get(origin, []):
            if not start <= instant(first.departure) <= end:
                continue
            if first.destination in destinations:
                result.append(Itinerary((first,)))
                continue
            for second in adjacency.get(first.destination, []):
                evaluations += 1
                if evaluations > max_evaluations:
                    raise SearchLimitExceeded('Se alcanzó el límite; no se afirma haber encontrado el mínimo global.')
                if second.destination not in destinations or second.destination == first.origin:
                    continue
                gap = instant(second.departure) - instant(first.arrival)
                if gap >= timedelta(minutes=min_connection_minutes):
                    result.append(Itinerary((first, second)))
    return sorted(result, key=lambda r: (r.amount_minor, r.duration_minutes, tuple(f.id for f in r.flights)))


def frontier(itineraries):
    """Keep tradeoffs in family price, elapsed time and independent-ticket risk."""
    def measures(r):
        return (r.amount_minor, r.duration_minutes, int(r.independent))
    return [a for a in itineraries if not any(
        all(x <= y for x, y in zip(measures(b), measures(a))) and
        any(x < y for x, y in zip(measures(b), measures(a)))
        for b in itineraries if b is not a)]


def highlights(itineraries):
    if not itineraries:
        return {'cheapest': None, 'fastest': None, 'tradeoffs': []}
    cheapest = min(itineraries, key=lambda r: (r.amount_minor, r.duration_minutes))
    fastest = min(itineraries, key=lambda r: (r.duration_minutes, r.amount_minor))
    return {'cheapest': cheapest, 'fastest': fastest, 'tradeoffs': frontier(itineraries)}


def saving_per_extra_hour(candidate, baseline):
    """Informational family saving vs a specified faster baseline. Minor units/hour."""
    extra = candidate.duration_minutes - baseline.duration_minutes
    saving = baseline.amount_minor - candidate.amount_minor
    return saving * 60 / extra if extra > 0 and saving > 0 else None


def round_trips(outbound, inbound, max_evaluations=100000):
    """Combine independently searched directions, same home and destination airports.

    Every direction must already be normalized for identical party/currency/baggage.
    No assumption that reverse flight schedules exist. No airport-change transfers.
    """
    result, count = [], 0
    for out in outbound:
        for back in inbound:
            count += 1
            if count > max_evaluations:
                raise SearchLimitExceeded('Demasiadas combinaciones de ida y vuelta.')
            if (out.flights[0].origin == back.flights[-1].destination and
                out.flights[-1].destination == back.flights[0].origin and
                instant(back.flights[0].departure) > instant(out.flights[-1].arrival) and
                out.flights[0].party == back.flights[0].party and
                out.flights[0].currency == back.flights[0].currency and
                out.flights[0].baggage == back.flights[0].baggage):
                result.append({'outbound': out, 'inbound': back,
                               'amount_minor': out.amount_minor + back.amount_minor})
    return sorted(result, key=lambda r: r['amount_minor'])
