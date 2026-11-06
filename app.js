'use strict';
const $=id=>document.getElementById(id);
const today=()=>{const d=new Date();return [d.getFullYear(),String(d.getMonth()+1).padStart(2,'0'),String(d.getDate()).padStart(2,'0')].join('-');};
let plan=null;
$('departure').min=today();$('return').min=today();
$('independent').addEventListener('change',()=>{$('connection-warning').hidden=!$('independent').checked;});
const searchClient=new FlightSearchClient(document.querySelector('meta[name="flight-search-api"]').content);
let activeSearch=null,searchRevision=0;
function showSearchState(title,description){
 const panel=$('search-status');panel.replaceChildren();
 const heading=document.createElement('h3');heading.textContent=title;
 const message=document.createElement('p');message.textContent=description;panel.append(heading,message);
}
function renderOffers(offers){
 $('flight-results').replaceChildren();
 for(const offer of offers){
  const card=document.createElement('article');card.className='flight-card';
  const route=document.createElement('h3');route.textContent=offer.legs.map(l=>l.origin).concat(offer.legs.at(-1).destination).join(' → ');
  const cost=document.createElement('p');cost.textContent=new Intl.NumberFormat('es-ES',{style:'currency',currency:'EUR'}).format(offer.totalMinor/100)+' · total familiar';
  const source=document.createElement('p');source.textContent=`Fuente: ${offer.source} · consultado: ${new Date(offer.checkedAt).toLocaleString('es-ES')}`;
  card.append(route,cost,source);
  for(const leg of offer.legs){const detail=document.createElement('p');detail.textContent=`${leg.origin} → ${leg.destination} · ${leg.departure} → ${leg.arrival}`;card.append(detail);}
  if(offer.independent){const warning=document.createElement('p');warning.className='notice';warning.textContent='Billetes independientes. Un retraso puede hacer perder la conexión; comprueba equipaje, facturación y margen antes de reservar.';card.append(warning);}
  $('flight-results').append(card);
 }
}
async function runSearch(request){
 const revision=++searchRevision;activeSearch?.abort();activeSearch=new AbortController();
 $('search-results').hidden=false;$('search-results').setAttribute('aria-busy','true');$('flight-results').replaceChildren();
 showSearchState('Preparando búsqueda','Los resultados aparecerán en esta página.');
 $('search-results').focus({preventScroll:true});$('search-results').scrollIntoView({behavior:'smooth',block:'start'});
 try{
  const result=await searchClient.search(request,{signal:activeSearch.signal});if(revision!==searchRevision)return;
  if(result.status==='unavailable')showSearchState('Búsqueda de precios todavía no disponible','El motor de conexiones aún no está conectado a una fuente de vuelos y precios reales. Por eso no podemos mostrar opciones ni identificar la más barata. Tu búsqueda permanece aquí; no abrimos otras páginas.');
  else if(!result.offers.length)showSearchState('Sin ofertas en las fuentes consultadas','No se han obtenido ofertas para esta búsqueda. Esto no demuestra que no existan vuelos en otras compañías o fuentes.');
  else{showSearchState(`${result.offers.length} opciones encontradas`,'Precios para el grupo solicitado, con cobertura limitada a las fuentes consultadas.');renderOffers(result.offers);}
 }catch(error){if(revision===searchRevision&&error.name!=='AbortError')showSearchState('No se pudo completar la búsqueda',error.message);}
 finally{if(revision===searchRevision)$('search-results').setAttribute('aria-busy','false');}
}
$('search-form').addEventListener('submit',event=>{event.preventDefault();$('search-error').textContent='';try{const origins=[...document.querySelectorAll('[name=origin]:checked')].map(x=>x.value);if(!origins.length)throw Error('Selecciona al menos un aeropuerto de salida.');const travelers=Number($('travelers').value);if(!Number.isInteger(travelers)||travelers<1||travelers>9)throw Error('Indica entre 1 y 9 viajeros.');const destination=$('destination').value.trim()||'cualquier destino';let pairs=TravelCore.combinations($('departure').value,$('return').value,Number($('flex').value),today());const duration=$('duration').value;if(duration!=='any'){const [min,max]=duration.split('-').map(Number);pairs=pairs.filter(p=>{const days=(new Date(p.ret+'T00:00:00Z')-new Date(p.out+'T00:00:00Z'))/86400000;return days>=min&&days<=max;});}if(!pairs.length)throw Error('No hay combinaciones con esa duración. Amplía las fechas o elige cualquier duración.');plan={destination,origins,travelers,lowcost:$('lowcost').checked,independent:$('independent').checked,pairs};$('summary').textContent=`${origins.join(', ')} → ${destination} · ${travelers} viajeros · ${pairs.length} combinaciones de fechas`;runSearch({...plan,party:null});}catch(error){$('search-error').textContent=error.message;$('search-results').hidden=true;plan=null;}});
// Any edit invalidates the request and aborts stale responses.
$('search-form').addEventListener('input',()=>{searchRevision++;activeSearch?.abort();$('search-results').hidden=true;$('search-results').setAttribute('aria-busy','false');plan=null;});
// Keep the compact date summary in sync with the actual form fields.
function syncDateLabels(){
 $('dates-label').textContent=$('departure').value ? $('departure').value.split('-').reverse().join('/') : 'Fechas flexibles';
 $('flex-label').textContent=Number($('flex').value) ? `± ${$('flex').value} días` : 'Fechas exactas';
}
for(const id of ['departure','return','flex']) $(id).addEventListener('input',syncDateLabels);
$('close-dates').addEventListener('click',()=>{$('date-settings').open=false;});
$('search-form').addEventListener('invalid',event=>{if(event.target.closest('#date-settings'))$('date-settings').open=true;},true);
