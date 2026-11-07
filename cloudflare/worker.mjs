// Secrets belong in Cloudflare, never in this module or the public frontend.
const WEB_ORIGIN = 'https://albertogarabato.github.io';
const HOMES = ['SCQ', 'LCG', 'VGO', 'OPO', 'MAD'];
const VERSION = '2026-11-07-source-2';
class SearchError extends Error {
  constructor(message, status = 400) { super(message); this.status = status; }
}
function reply(data, status = 200) {
  return Response.json(data, {status, headers: {
    'Access-Control-Allow-Origin': WEB_ORIGIN,
    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Cache-Control': 'no-store', 'Vary': 'Origin',
    'X-Content-Type-Options': 'nosniff'
  }});
}
async function digest(value) {
  return [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(value)))].map(v => v.toString(16).padStart(2, '0')).join('');
}
function validDate(value) {
  return typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value) && Number.isFinite(Date.parse(value)) && new Date(value).toISOString().slice(0, 10) === value;
}
export function validate(input, now = Date.now()) {
  const {origins, destination, outboundDate, returnDate, party} = input || {};
  if (!Array.isArray(origins) || !origins.length || origins.length > 5 || new Set(origins).size !== origins.length || origins.some(v => !HOMES.includes(v))) throw new SearchError('Selecciona nuestros aeropuertos de salida.');
  if (typeof destination !== 'string' || !/^[A-Z]{3}$/.test(destination) || origins.includes(destination)) throw new SearchError('Indica el código de tres letras del aeropuerto de destino.');
  if (!validDate(outboundDate) || !validDate(returnDate) || outboundDate < new Date(now).toISOString().slice(0, 10) || returnDate <= outboundDate || Date.parse(returnDate) - now > 365 * 86400000) throw new SearchError('Revisa las fechas de ida y vuelta (hasta un año).');
  if (!party || !['adults','children','infantsOnLap','infantsInSeat'].every(k => Number.isInteger(party[k]) && party[k] >= 0) || party.adults < 1 || party.infantsOnLap > party.adults || Object.values(party).some(v => !Number.isInteger(v)) || ['adults','children','infantsOnLap','infantsInSeat'].reduce((sum, k) => sum + party[k], 0) > 9) throw new SearchError('Configura adultos, niños y bebés (máximo nueve personas).');
  return {origins: [...origins].sort(), destination, outboundDate, returnDate,
    party: Object.fromEntries(['adults','children','infantsOnLap','infantsInSeat'].map(k => [k, party[k]]))};
}
export function normalize(raw, origins, destinations, date) {
  const seen = new Set(), offers = [];
  for (const item of [...(raw.best_flights || []), ...(raw.other_flights || [])]) {
    const flights = item.flights;
    if (!Array.isArray(flights) || !flights.length || flights.length > 2 || !Number.isFinite(item.price) || item.price <= 0 || !Number.isInteger(item.price * 100)) continue;
    if (!origins.includes(flights[0]?.departure_airport?.id) || !destinations.includes(flights.at(-1)?.arrival_airport?.id) || !flights[0]?.departure_airport?.time?.startsWith(date)) continue;
    if (flights.some((f, i) => !/^[A-Z]{3}$/.test(f.departure_airport?.id || '') || !/^[A-Z]{3}$/.test(f.arrival_airport?.id || '') || !/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/.test(f.departure_airport?.time || '') || !/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/.test(f.arrival_airport?.time || '') || (i && flights[i - 1].arrival_airport.id !== f.departure_airport.id))) continue;
    const legs = flights.map(f => ({origin: f.departure_airport.id, destination: f.arrival_airport.id, departureLocal: f.departure_airport.time, arrivalLocal: f.arrival_airport.time, airline: String(f.airline || '').slice(0,100), flightNumber: String(f.flight_number || '').slice(0,40)}));
    const identity = JSON.stringify(legs) + item.price;
    if (seen.has(identity)) continue;
    seen.add(identity);
    offers.push({status:'observed', currency:'EUR', displayedPriceMinor: Math.round(item.price * 100), legs,
      durationMinutes: Number.isFinite(item.total_duration) ? item.total_duration : null,
      source:'SerpApi / Google Flights', checkedAt: new Date().toISOString(),
      priceBasis:'unverified', baggageSupplementsKnown:false, connectionProtection:'unverified',
      separateTickets: !!item.separate_tickets, eligibleForVerifiedRanking:false});
  }
  return offers.sort((a,b) => a.displayedPriceMinor - b.displayedPriceMinor).slice(0,60);
}
async function provider(path, params, key) {
  const url = new URL('https://serpapi.com' + path);
  for (const [k,v] of Object.entries({...params, api_key:key})) url.searchParams.set(k,String(v));
  let response;
  try { response = await fetch(url, {redirect:'manual', signal:AbortSignal.timeout(60000)}); }
  catch (error) { throw new SearchError(error?.name === 'TimeoutError' || error?.name === 'AbortError' ? 'La fuente no respondió a tiempo. No se reintenta automáticamente.' : 'No se pudo conectar con la fuente de vuelos. No se reintenta automáticamente.', 502); }
  if (!response.ok) throw new SearchError(response.status === 429 ? 'Se ha alcanzado el límite de consultas de vuelos.' : 'La fuente de vuelos no pudo completar la consulta.', 502);
  try { return await response.json(); }
  catch { throw new SearchError('La fuente no devolvió datos válidos.', 502); }
}
async function oneWay(origins, destinations, date, party, env) {
  const params = {engine:'google_flights', departure_id:origins.join(','), arrival_id:destinations.join(','), outbound_date:date,
    type:2, adults:party.adults, children:party.children, infants_on_lap:party.infantsOnLap, infants_in_seat:party.infantsInSeat,
    currency:'EUR', hl:'es', gl:'es', stops:2, sort_by:2, deep_search:'true'};
  const cacheKey = new Request('https://viajeros-cache.invalid/' + await digest(JSON.stringify(params)));
  const cache = /** @type {any} */ (globalThis).caches?.default;
  let cached;
  try {cached = await cache?.match(cacheKey);} catch { /* Cache failure must not discard results. */ }
  if (cached) return {...await cached.json(), cached:true};
  const account = await provider('/account.json', {}, env.SERPAPI_API_KEY);
  if (account.account_status !== 'Active' || account.plan_monthly_price !== 0 || !Number.isInteger(account.plan_searches_left) || account.plan_searches_left < 1) throw new SearchError('Solo se permiten consultas con la cuenta gratuita activa y cuota disponible.', 429);
  const raw = await provider('/search.json', params, env.SERPAPI_API_KEY);
  if (raw.error || raw.search_metadata?.status !== 'Success') throw new SearchError('La fuente no completó la búsqueda. No se reintenta automáticamente.', 502);
  const echoed = raw.search_parameters || {};
  for (const [name, defaultValue] of [['adults',1],['children',0],['infants_on_lap',0],['infants_in_seat',0]]) if (String(echoed[name] ?? defaultValue) !== String(params[name])) throw new SearchError('La respuesta no corresponde a los viajeros solicitados.', 502);
  if (echoed.currency !== 'EUR' || String(echoed.type) !== '2' || echoed.outbound_date !== date || echoed.departure_id !== params.departure_id || echoed.arrival_id !== params.arrival_id) throw new SearchError('La respuesta no corresponde a esta ruta y fecha.', 502);
  const result = {offers:normalize(raw, origins, destinations, date), cached:false};
  try {if (cache) await cache.put(cacheKey, Response.json(result, {headers:{'Cache-Control':'max-age=900'}}));} catch { /* A cache miss only costs the next query; it must not hide this one. */ }
  return result;
}
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === 'GET' && (url.pathname === '/health' || url.pathname === '/')) return reply({service:'Viajeros Garabato Penido', version:VERSION, status:'ready', searchConfigured:!!(env.SERPAPI_API_KEY && env.FAMILY_ACCESS_CODE), mode:'observed-prices'});
    if (request.headers.get('Origin') && request.headers.get('Origin') !== WEB_ORIGIN) return reply({message:'Origen no permitido.'},403);
    if (request.method === 'OPTIONS') return reply({});
    if (url.pathname !== '/search' || request.method !== 'POST') return reply({message:'Ruta no disponible.'},404);
    try {
      if (!env.SERPAPI_API_KEY || !env.FAMILY_ACCESS_CODE || env.FAMILY_ACCESS_CODE.length < 12) throw new SearchError('Falta configurar el acceso familiar privado.',503);
      const auth = request.headers.get('Authorization') || '';
      if (!auth.startsWith('Bearer ') || auth.length > 256 || await digest(auth.slice(7)) !== await digest(env.FAMILY_ACCESS_CODE)) throw new SearchError('Introduce la clave de acceso familiar.',401);
      if (!request.headers.get('Content-Type')?.startsWith('application/json')) throw new SearchError('Solicitud no válida.');
      // Read incrementally so a forged Content-Length cannot cause unbounded parsing.
      const reader = request.body?.getReader(); let size = 0; const chunks = [];
      if (!reader) throw new SearchError('Falta la búsqueda.');
      while (true) {const {done,value} = await reader.read(); if(done) break; size += value.byteLength; if(size > 12000) {await reader.cancel(); throw new SearchError('Solicitud demasiado grande.',413);} chunks.push(value);}
      const bytes = new Uint8Array(size); let offset = 0; for (const chunk of chunks) {bytes.set(chunk,offset); offset += chunk.length;}
      let input; try {input = JSON.parse(new TextDecoder().decode(bytes));} catch {throw new SearchError('Solicitud no válida.');}
      const query = validate(input);
      const outbound = await oneWay(query.origins, [query.destination], query.outboundDate, query.party, env);
      let inbound, returnError = null;
      try {inbound = await oneWay([query.destination], query.origins, query.returnDate, query.party, env);}
      catch (error) {returnError = error instanceof SearchError ? error.message : 'No se pudo consultar la vuelta.'; inbound = {offers:[]};}
      return reply({status:returnError ? 'partial' : 'observed', query, outbound, inbound, returnError,
        coverage:'Primera fuente: resultados de Google Flights, hasta una escala, fechas exactas. No incluye todas las aerolíneas ni todas las combinaciones.',
        notice:'Precios observados de ida y vuelta por separado. No se ha verificado si cada importe es por persona o para el grupo; no se suman ni se presentan como total familiar. Equipaje, plazas y protección de conexiones pendientes de comprobar.',
        independentSearchAvailable:false, flexibleSearchAvailable:false});
    } catch (error) {
      return reply({message:error instanceof SearchError ? error.message : 'No se pudo completar la búsqueda.'}, error instanceof SearchError ? error.status : 500);
    }
  }
};
