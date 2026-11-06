"""SYNTHETIC UNIT TESTS ONLY. No real routes, availability or fares."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import unittest
from dataclasses import replace
from optimizer import (Party, Flight, discover_paths, search_one_way, highlights,
                       saving_per_extra_hour, round_trips, SearchLimitExceeded)

PARTY = Party(2, (8, 11, 15))
NOW = '2027-01-01T10:00:00Z'


def flight(id, origin, destination, departure, arrival, amount, **kwargs):
    return Flight(id, origin, destination, departure, arrival, amount, 'EUR', PARTY,
                  'SYNTHETIC-TEST-ONLY', NOW, '2027-01-01T11:00:00Z', **kwargs)


def dataset():
    return [
        flight('direct', 'AAA', 'CCC', '2027-02-10T08:00:00Z', '2027-02-10T11:00:00Z', 100000),
        flight('first', 'AAA', 'BBB', '2027-02-10T07:00:00Z', '2027-02-10T08:00:00Z', 10000),
        flight('second', 'BBB', 'CCC', '2027-02-10T11:00:00Z', '2027-02-10T13:00:00Z', 20000),
        flight('tight', 'BBB', 'CCC', '2027-02-10T09:00:00Z', '2027-02-10T11:00:00Z', 1000),
        flight('other-origin', 'DDD', 'CCC', '2027-02-10T08:00:00Z', '2027-02-10T12:00:00Z', 60000),
    ]


def search(flights=None, **kwargs):
    params = dict(origins=['AAA', 'DDD'], destinations=['CCC'],
                  start='2027-02-10T00:00:00Z', end='2027-02-10T23:59:59Z', party=PARTY, now=NOW)
    params.update(kwargs)
    return search_one_way(dataset() if flights is None else flights, **params)


class ConnectionEngineTests(unittest.TestCase):
    def test_discovers_via_intersection_not_a_fixed_destination(self):
        paths = discover_paths([('AAA','BBB'),('BBB','CCC'),('DDD','CCC')], ['AAA','DDD'], ['CCC'])
        self.assertEqual(paths, [('DDD','CCC'),('AAA','BBB','CCC')])

    def test_does_not_invent_reverse_routes(self):
        self.assertEqual(discover_paths([('AAA','BBB')], ['BBB'], ['AAA']), [])

    def test_joins_cheaper_independent_legs(self):
        result = search()
        self.assertEqual(result[0].amount_minor, 30000)
        self.assertEqual([f.id for f in result[0].flights], ['first','second'])
        self.assertEqual(result[0].connection_minutes, (180,))
        self.assertTrue(result[0].independent)

    def test_compares_all_origins(self):
        self.assertIn('DDD', {r.flights[0].origin for r in search()})

    def test_rejects_tight_connections(self):
        self.assertFalse(any(f.id == 'tight' for r in search() for f in r.flights))

    def test_configurable_margin(self):
        self.assertEqual(search(min_connection_minutes=60)[0].amount_minor, 11000)

    def test_compares_utc_not_local_clock(self):
        flights = [flight('a','AAA','BBB','2027-02-10T22:00:00+01:00','2027-02-10T23:00:00+01:00',100),
                   flight('b','BBB','CCC','2027-02-11T04:00:00+02:00','2027-02-11T06:00:00+02:00',100)]
        self.assertEqual(search(flights)[0].connection_minutes, (240,))

    def test_never_multiplies_single_person_quote_into_family_availability(self):
        self.assertEqual(search([replace(dataset()[0], party=Party(1))]), [])

    def test_ages_are_part_of_the_quote(self):
        self.assertEqual(search([replace(dataset()[0], party=Party(2,(7,11,15)))]), [])

    def test_excludes_test_and_cached_prices(self):
        for status in ['test','indicative','historical']:
            self.assertEqual(search([replace(dataset()[0],status=status)]), [])

    def test_excludes_stale_expired_future_checked_quotes(self):
        for now in ['2027-01-01T10:31:00Z','2027-01-01T11:00:00Z','2027-01-01T09:59:00Z']:
            self.assertEqual(search([dataset()[0]],now=now), [])

    def test_no_currency_or_baggage_mixing(self):
        self.assertEqual(search([replace(dataset()[0],currency='USD')]), [])
        self.assertEqual(search([replace(dataset()[0],baggage='checked')]), [])

    def test_pareto_keeps_faster_and_cheaper_tradeoffs(self):
        result = highlights(search())
        self.assertEqual(result['cheapest'].amount_minor,30000)
        self.assertEqual(result['fastest'].amount_minor,100000)
        self.assertEqual(len(result['tradeoffs']),3)
        self.assertAlmostEqual(saving_per_extra_hour(result['cheapest'],result['fastest']),70000/3)

    def test_no_blanket_maximum_journey_duration(self):
        flights=[dataset()[1],replace(dataset()[2],departure='2027-02-12T11:00:00Z',arrival='2027-02-12T13:00:00Z')]
        self.assertEqual(len(search(flights)),1)

    def test_work_limit_does_not_claim_exhaustive_success(self):
        with self.assertRaises(SearchLimitExceeded):search(max_evaluations=1)

    def test_roundtrip_uses_separately_observed_return(self):
        out=search([dataset()[0]])
        backflight=flight('back','CCC','AAA','2027-02-17T08:00:00Z','2027-02-17T11:00:00Z',50000)
        back=search([backflight],origins=['CCC'],destinations=['AAA'],start='2027-02-17T00:00:00Z',end='2027-02-17T23:59:59Z')
        self.assertEqual(round_trips(out,back)[0]['amount_minor'],150000)
        self.assertEqual(round_trips(out,[]),[])

    def test_different_airports_are_not_silently_joined(self):
        flights=[dataset()[1],replace(dataset()[2],origin='EEE')]
        self.assertEqual(search(flights),[])

    def test_duplicate_quotes_rejected(self):
        with self.assertRaises(ValueError):search([dataset()[0],dataset()[0]])

    def test_requires_offsets_and_positive_group_prices(self):
        with self.assertRaises(ValueError):replace(dataset()[0],departure='2027-02-10T08:00:00')
        with self.assertRaises(ValueError):replace(dataset()[0],amount_minor=0)
        with self.assertRaises(ValueError):Party(0)


if __name__ == '__main__':
    unittest.main()
