"""Synthetic transport and payloads. Does not contact Amadeus or use real keys."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import unittest
from urllib.parse import urlparse, parse_qs
from optimizer import Party
from providers.amadeus_test import AmadeusTest, MissingCredentials, ProviderError, normalize


def payload():
    return {'id':'test-offer','price':{'currency':'EUR','grandTotal':'120.50','total':'120.50'},
            'travelerPricings':[{'travelerId':'1','travelerType':'ADULT'},
                               {'travelerId':'2','travelerType':'CHILD'}],
            'itineraries':[{'segments':[{'departure':{'iataCode':'AAA','at':'2027-04-10T10:00:00'},
                'arrival':{'iataCode':'BBB','at':'2027-04-10T11:00:00'},
                'carrierCode':'ZZ','number':'001'}]}]}


class AmadeusConnectionTests(unittest.TestCase):
    def setUp(self):
        self.calls=[]
        def fake(method,url,headers,body):
            self.calls.append((method,url,headers,body))
            if '/token' in url:return {'access_token':'SYNTHETIC-TOKEN','expires_in':1800}
            return {'data':[]}
        self.api=AmadeusTest('SYNTHETIC-KEY','SYNTHETIC-SECRET',request_transport=fake)

    def test_retired_service_cannot_read_environment_or_make_real_requests(self):
        with self.assertRaises(ProviderError):AmadeusTest.from_environment()
        api=AmadeusTest('SYNTHETIC-KEY','SYNTHETIC-SECRET')
        with self.assertRaises(ProviderError):api.search_direct('AAA','BBB','2027-04-10',Party(1))

    def test_requires_credentials_before_network(self):
        with self.assertRaises(MissingCredentials):AmadeusTest('', '')

    def test_only_test_host_and_token_cached(self):
        self.api.search_direct('AAA','BBB','2027-04-10',Party(2))
        self.api.search_direct('CCC','BBB','2027-04-10',Party(2))
        self.assertEqual(len(self.calls),3)
        self.assertTrue(all(urlparse(c[1]).netloc=='test.api.amadeus.com' for c in self.calls))
        self.assertEqual(self.calls[0][0],'POST')
        self.assertNotIn('SYNTHETIC-SECRET',self.calls[0][1])
        self.assertNotIn('SYNTHETIC-KEY',self.calls[1][1])

    def test_search_requests_exact_party_categories_and_direct_legs(self):
        self.api.search_direct('AAA','BBB','2027-04-10',Party(2,(1,8,15)))
        q=parse_qs(urlparse(self.calls[-1][1]).query)
        self.assertEqual(q['adults'],['3']);self.assertEqual(q['children'],['1'])
        self.assertEqual(q['infants'],['1']);self.assertEqual(q['nonStop'],['true'])
        self.assertEqual(q['currencyCode'],['EUR'])

    def test_budget_stops_before_extra_network(self):
        self.api.request_limit=1
        with self.assertRaises(ProviderError):self.api.search_direct('AAA','BBB','2027-04-10',Party(1))
        self.assertEqual(len(self.calls),1)

    def test_invalid_query_uses_no_quota(self):
        with self.assertRaises(ValueError):self.api.search_direct('AAA','BBB','2027-02-30',Party(1))
        self.assertEqual(self.calls,[])

    def test_empty_test_dataset_not_live_no_flights_claim(self):
        result=self.api.search_direct('AAA','BBB','2027-04-10',Party(1))
        self.assertEqual(result['status'],'test')
        self.assertEqual(result['offers'],[])
        self.assertIn('no confirman',result['notice'])

    def test_normalized_total_is_family_not_per_person_and_remains_test(self):
        result=normalize(payload(),'AAA','BBB',Party(1,(8,)))
        self.assertEqual(result['totalMinor'],12050)
        self.assertEqual(result['status'],'test')
        self.assertFalse(result['eligibleForLiveRanking'])
        self.assertFalse(result['baggage']['supplementsKnown'])
        self.assertIn('departureLocal',result['legs'][0])

    def test_wrong_group_and_unknown_currency_rejected(self):
        self.assertIsNone(normalize(payload(),'AAA','BBB',Party(2)))
        p=payload();p['price']['currency']='USD'
        self.assertIsNone(normalize(p,'AAA','BBB',Party(1,(8,))))

    def test_never_splits_connecting_total_into_fake_leg_fares(self):
        p=payload();p['itineraries'][0]['segments']*=2
        self.assertIsNone(normalize(p,'AAA','BBB',Party(1,(8,))))

    def test_invalid_amount_rejected(self):
        for value in ['NaN','-1','0','12.345']:
            p=payload();p['price']['grandTotal']=value
            self.assertIsNone(normalize(p,'AAA','BBB',Party(1,(8,))))


if __name__=='__main__':unittest.main()
