"""Synthetic fixtures. No live requests or real keys."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import unittest
from providers.serpapi_flights import SerpApiFlights,ProviderError,normalize


def fixture():
 return {'flights':[{'departure_airport':{'id':'AAA','time':'2027-04-10 10:00'},
                     'arrival_airport':{'id':'BBB','time':'2027-04-10 11:00'},'airline':'SYNTHETIC'}],
         'price':123,'total_duration':60}


class SerpApiTests(unittest.TestCase):
 def setUp(self):
  self.calls=[];self.plan_price=0;self.remaining=250
  def fake(path,params):
   self.calls.append((path,params))
   if path=='/account.json':return {'account_status':'Active','plan_monthly_price':self.plan_price,'plan_searches_left':self.remaining,'api_key':'SYNTHETIC-SECRET','account_email':'never-return@example.invalid'}
   return {'search_metadata':{'status':'Success','created_at':'2026-11-07 10:00:00 UTC'},'search_parameters':dict(params),'best_flights':[fixture()],'other_flights':[fixture()]}
  self.api=SerpApiFlights('SYNTHETIC-SECRET',request_transport=fake)
 def search(self,**kwargs):return self.api.one_way(['AAA'],'BBB','2027-04-10',1,**kwargs)
 def test_redacts_account_fields(self):
  self.assertNotIn('api_key',self.api.account_summary());self.assertNotIn('account_email',self.api.account_summary())
 def test_paid_plan_blocked_before_search(self):
  self.plan_price=25
  with self.assertRaises(ProviderError):self.search()
  self.assertEqual(len(self.calls),1)
 def test_exhausted_quota_blocked(self):
  self.remaining=0
  with self.assertRaises(ProviderError):self.search()
 def test_cache_deduplication_and_no_secret_in_results(self):
  result=self.search();self.assertEqual(len(result['offers']),1)
  self.assertNotIn('SYNTHETIC-SECRET',str(result));self.search();self.assertEqual(len(self.calls),2)
 def test_limits_and_no_retry(self):
  self.api.request_limit=1;self.search()
  with self.assertRaises(ProviderError):self.api.one_way(['AAA'],'BBB','2027-04-11',1)
  self.assertEqual(len(self.calls),2)
 def test_passenger_request_preserved_and_not_multiplied(self):
  result=self.search(children=2)
  self.assertEqual(result['requestedPassengers']['children'],2)
  self.assertEqual(result['offers'][0]['displayedPriceMinor'],12300)
  self.assertFalse(result['offers'][0]['eligibleForVerifiedRanking'])
 def test_unsupported_airport_change_excluded(self):
  f=fixture();f['flights']*=2
  self.assertIsNone(normalize(f,['AAA'],'BBB','2027-04-10',False,None))
 def test_wrong_route_or_date_excluded(self):
  self.assertIsNone(normalize(fixture(),['CCC'],'BBB','2027-04-10',True,None))
  self.assertIsNone(normalize(fixture(),['AAA'],'BBB','2027-04-11',True,None))
 def test_invalid_input_uses_no_quota(self):
  with self.assertRaises(ValueError):self.search(children=-1)
  self.assertEqual(self.calls,[])


if __name__=='__main__':unittest.main()
