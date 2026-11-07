import assert from 'node:assert/strict';
import worker, {validate, normalize} from './worker.mjs';

export async function runTests() {
  let assertions = 0;
  const equal = (a,b) => {assert.deepEqual(a,b); assertions++;};
  const throws = fn => {assert.throws(fn); assertions++;};
  const query = {origins:['SCQ','MAD'],destination:'BBB',outboundDate:'2027-02-15',returnDate:'2027-02-20',party:{adults:2,children:3,infantsOnLap:0,infantsInSeat:0}};
  const env = {SERPAPI_API_KEY:'synthetic-private-key',FAMILY_ACCESS_CODE:'synthetic-family-code'};
  const headers = {'Content-Type':'application/json',Authorization:'Bearer '+env.FAMILY_ACCESS_CODE,Origin:'https://albertogarabato.github.io'};
  const post = (body=query, customHeaders=headers, secrets=env) => worker.fetch(new Request('https://service.test/search',{method:'POST',headers:customHeaders,body:JSON.stringify(body)}),secrets);
  equal(validate(query).origins,['MAD','SCQ']);
  throws(() => validate({...query,origins:['XXX']}));
  throws(() => validate({...query,origins:['SCQ','SCQ']}));
  throws(() => validate({...query,returnDate:'2027-02-30'}));
  throws(() => validate({...query,returnDate:query.outboundDate}));
  throws(() => validate({...query,party:{...query.party,adults:0}}));
  throws(() => validate({...query,party:{...query.party,infantsOnLap:3}}));
  throws(() => validate({...query,party:{...query.party,children:9}}));
  const originalFetch = globalThis.fetch;
  let calls = [];
  globalThis.fetch = async (url) => {
    const u = new URL(url); calls.push(u);
    if(u.pathname === '/account.json') return Response.json({account_status:'Active',plan_monthly_price:0,plan_searches_left:100});
    const p = Object.fromEntries(u.searchParams);
    const origin = p.departure_id.split(',')[0], destination = p.arrival_id.split(',')[0];
    return Response.json({search_metadata:{status:'Success'},search_parameters:p,best_flights:[{price:42,total_duration:100,flights:[{departure_airport:{id:origin,time:p.outbound_date+' 10:00'},arrival_airport:{id:destination,time:p.outbound_date+' 11:40'},airline:'Synthetic Air'}]}]});
  };
  try {
    equal((await post(query,{'Content-Type':'application/json'})).status,401);
    equal((await post(query,{...headers,Origin:'https://other.test'})).status,403);
    equal((await post(query,headers,{})).status,503);
    equal((await post({...query,returnDate:'broken'})).status,400);
    equal(calls.length,0);
    const response = await post();
    equal(response.status,200);
    const data = await response.json();
    equal(data.status,'observed'); equal(data.outbound.offers.length,1); equal(data.inbound.offers.length,1);
    equal(data.outbound.offers[0].displayedPriceMinor,4200);
    equal(data.outbound.offers[0].eligibleForVerifiedRanking,false);
    equal(JSON.stringify(data).includes(env.SERPAPI_API_KEY),false);
    equal(calls.filter(u=>u.pathname==='/search.json').length,2);
    equal(calls.filter(u=>u.pathname==='/search.json').every(u=>u.searchParams.get('children')==='3'),true);
    globalThis.fetch = async () => Response.json({account_status:'Active',plan_monthly_price:5,plan_searches_left:100});
    equal((await post()).status,429);
    globalThis.fetch = async () => {throw Error('https://provider.test?api_key='+env.SERPAPI_API_KEY);};
    const failure = await post(); equal(failure.status,502); equal((await failure.text()).includes(env.SERPAPI_API_KEY),false);
    const flight = (a,b) => ({departure_airport:{id:a,time:'2027-02-15 10:00'},arrival_airport:{id:b,time:'2027-02-15 12:00'}});
    equal(normalize({best_flights:[{price:1,flights:[flight('SCQ','AAA'),flight('CCC','BBB')]}]},['SCQ'],['BBB'],'2027-02-15').length,0);
    equal(normalize({best_flights:[{price:-1,flights:[flight('SCQ','BBB')]}]},['SCQ'],['BBB'],'2027-02-15').length,0);
    equal(normalize({best_flights:[{price:1,flights:[flight('SCQ','BBB')]}]},['SCQ'],['BBB'],'2027-02-16').length,0);
  } finally {globalThis.fetch = originalFetch;}
  return {assertions, result:'passed'};
}
