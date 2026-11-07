'use strict';
const $=id=>document.getElementById(id);
const today=()=>new Date().toLocaleDateString('sv-SE');
$('departure').min=today();$('return').min=today();
const searchClient=new FlightSearchClient(document.querySelector('meta[name="flight-search-api"]').content);
let activeSearch=null,searchRevision=0;
function showSearchState(title,description){
 const panel=$('search-status');panel.replaceChildren();
 const heading=document.createElement('h3');heading.textContent=title;
 const message=document.createElement('p');message.textContent=description;panel.append(heading,message);
}
function renderResults(data,sort='price'){
 const container=$('flight-results');container.replaceChildren();
 const label=document.createElement('label');label.className='results-sort';label.textContent='Ordenar cada trayecto por ';const order=document.createElement('select');
 for(const [value,text] of [['price','Precio mostrado'],['duration','Duración']]){const option=document.createElement('option');option.value=value;option.textContent=text;order.append(option);}order.value=sort;order.addEventListener('change',()=>renderResults(data,order.value));label.append(order);container.append(label);
 const notice=document.createElement('p');notice.className='notice';notice.textContent=data.notice;container.append(notice);
 for(const [direction,title] of [['outbound','Ida'],['inbound','Vuelta']]){
  const section=document.createElement('section'),heading=document.createElement('h3');heading.textContent=title+' · '+data[direction].offers.length+' opciones';section.append(heading);
  const offers=[...data[direction].offers].sort((a,b)=>sort==='price'?a.displayedPriceMinor-b.displayedPriceMinor:(a.durationMinutes??Infinity)-(b.durationMinutes??Infinity));
  if(!offers.length){const empty=document.createElement('p');empty.textContent=direction==='inbound'&&data.returnError?data.returnError:'Sin resultados en esta fuente. Puede haber otras opciones no cubiertas.';section.append(empty);}
  for(const offer of offers){
   const card=document.createElement('article');card.className='flight-card';
   const route=document.createElement('h4');route.textContent=offer.legs.map(l=>l.origin).concat(offer.legs.at(-1).destination).join(' → ');
   const cost=document.createElement('p');cost.className='observed-price';cost.textContent=new Intl.NumberFormat('es-ES',{style:'currency',currency:'EUR'}).format(offer.displayedPriceMinor/100)+' · precio mostrado por la fuente';
   const detail=document.createElement('p');detail.textContent=(offer.durationMinutes?`${Math.floor(offer.durationMinutes/60)} h ${offer.durationMinutes%60} min · `:'')+(offer.legs.length===1?'Directo':'1 escala');
   card.append(route,cost,detail);
   for(const leg of offer.legs){const flight=document.createElement('p');flight.textContent=`${leg.airline} ${leg.flightNumber} · ${leg.origin} ${leg.departureLocal} → ${leg.destination} ${leg.arrivalLocal} (horas locales)`;card.append(flight);}
   const source=document.createElement('small');source.textContent=`${offer.source} · ${new Date(offer.checkedAt).toLocaleString('es-ES')} · Equipaje y protección de conexión pendientes de comprobar.`;card.append(source);
   if(offer.separateTickets){const risk=document.createElement('p');risk.className='notice';risk.textContent='La fuente indica billetes separados: un retraso puede hacer perder la conexión.';card.append(risk);}
   section.append(card);
  }container.append(section);
 }
}
async function runSearch(request){
 const revision=++searchRevision;activeSearch?.abort();activeSearch=new AbortController();
 $('search-results').hidden=false;$('search-results').setAttribute('aria-busy','true');$('flight-results').replaceChildren();
 showSearchState('Consultando vuelos','Buscando ida y vuelta en nuestra primera fuente. Puede tardar alrededor de un minuto.');
 $('search-results').focus({preventScroll:true});$('search-results').scrollIntoView({behavior:'smooth',block:'start'});
 try{
  const result=await searchClient.search(request,{signal:activeSearch.signal,accessCode:$('family-access').value});if(revision!==searchRevision)return;
  if(result.status==='unavailable')showSearchState('Servicio pendiente de configurar','Todavía no se ha configurado la conexión de vuelos.');
  else {showSearchState(result.status==='partial'?'Resultados parciales':'Resultados de la primera fuente',result.coverage);renderResults(result);}
 }catch(error){if(revision===searchRevision&&error.name!=='AbortError')showSearchState('No se pudo completar la búsqueda',error.message);}
 finally{if(revision===searchRevision)$('search-results').setAttribute('aria-busy','false');}
}
const destinations={barcelona:'BCN',varsovia:'WAW',londres:'LGW',paris:'CDG',roma:'FCO',lisboa:'LIS',alicante:'ALC',malaga:'AGP',milan:'MXP',berlin:'BER',amsterdam:'AMS',dublin:'DUB'};
function resolveDestination(text){const value=text.trim().normalize('NFD').replace(/[\u0300-\u036f]/g,'');const code=value.match(/\(([A-Z]{3})\)$/i);if(code)return code[1].toUpperCase();if(/^[a-z]{3}$/i.test(value))return value.toUpperCase();if(destinations[value.toLowerCase()])return destinations[value.toLowerCase()];throw Error('Elige un destino de la lista o escribe su código de aeropuerto de tres letras.');}
function party(){return {adults:Number($('adults').value),children:Number($('children').value),infantsOnLap:Number($('infants-lap').value),infantsInSeat:Number($('infants-seat').value)};}
function syncTravelers(){$('travelers').value=Object.values(party()).reduce((a,b)=>a+b,0);}
for(const id of ['adults','children','infants-seat','infants-lap'])$(id).addEventListener('input',syncTravelers);
$('search-form').addEventListener('submit',event=>{event.preventDefault();$('search-error').textContent='';try{
 const origins=[...document.querySelectorAll('[name=origin]:checked')].map(x=>x.value);if(!origins.length)throw Error('Selecciona al menos un aeropuerto de salida.');
 const group=party(),travelers=Object.values(group).reduce((a,b)=>a+b,0);if(!Object.values(group).every(Number.isInteger)||group.adults<1||travelers>9||travelers<1||group.infantsOnLap>group.adults)throw Error('Revisa los viajeros: máximo nueve personas y un bebé en brazos por adulto.');
 const destination=resolveDestination($('destination').value);if(origins.includes(destination))throw Error('El destino coincide con uno de los orígenes. Desmárcalo o cambia el destino.');
 const pairs=TravelCore.combinations($('departure').value,$('return').value,0,today());if(!pairs.length||$('return').value<=$('departure').value)throw Error('La vuelta debe ser posterior a la salida.');
 const duration=$('duration').value,days=(Date.parse($('return').value)-Date.parse($('departure').value))/86400000;if(duration!=='any'){const [min,max]=duration.split('-').map(Number);if(days<min||days>max)throw Error('Las fechas no corresponden a la duración elegida.');}
 $('summary').textContent=`${origins.join(', ')} → ${destination} · ${travelers} viajeros · ${$('departure').value} / ${$('return').value} · búsqueda en fechas exactas`;
 runSearch({origins,destination,party:group,outboundDate:$('departure').value,returnDate:$('return').value});
 }catch(error){$('search-error').textContent=error.message;$('search-results').hidden=true;}});
$('search-form').addEventListener('input',()=>{searchRevision++;activeSearch?.abort();$('search-results').hidden=true;$('search-results').setAttribute('aria-busy','false');});
function syncDateLabels(){$('dates-label').textContent=$('departure').value?$('departure').value.split('-').reverse().join('/'):'Elige fechas';$('flex-label').textContent='Fechas exactas';}
for(const id of ['departure','return','flex'])$(id).addEventListener('input',syncDateLabels);
$('close-dates').addEventListener('click',()=>{$('date-settings').open=false;});
$('search-form').addEventListener('invalid',event=>{if(event.target.closest('#date-settings'))$('date-settings').open=true;},true);
syncDateLabels();
