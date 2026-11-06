'use strict';
const $=id=>document.getElementById(id);
const today=()=>{const d=new Date();return [d.getFullYear(),String(d.getMonth()+1).padStart(2,'0'),String(d.getDate()).padStart(2,'0')].join('-');};
let plan=null;
$('departure').min=today();$('return').min=today();
$('independent').addEventListener('change',()=>{$('connection-warning').hidden=!$('independent').checked;});
function renderLinks(){const p=plan.pairs[Number($('date-pair').value)];$('origin-links').replaceChildren();for(const origin of plan.origins){const a=document.createElement('a');const query=`Vuelos ida y vuelta ${origin} a ${plan.destination}, salida ${p.out}, vuelta ${p.ret}, ${plan.travelers} viajeros${plan.lowcost?', incluir low cost':''}${plan.independent?', explorar conexiones con billetes separados':''}`;a.href='https://www.google.com/travel/flights?q='+encodeURIComponent(query);a.target='_blank';a.rel='noopener noreferrer';a.textContent=`Consultar desde ${origin} ↗`;$('origin-links').append(a);}}
$('search-form').addEventListener('submit',event=>{event.preventDefault();$('search-error').textContent='';try{const origins=[...document.querySelectorAll('[name=origin]:checked')].map(x=>x.value);if(!origins.length)throw Error('Selecciona al menos un aeropuerto de salida.');const travelers=Number($('travelers').value);if(!Number.isInteger(travelers)||travelers<1||travelers>9)throw Error('Indica entre 1 y 9 viajeros.');const destination=$('destination').value.trim()||'cualquier destino';let pairs=TravelCore.combinations($('departure').value,$('return').value,Number($('flex').value),today());const duration=$('duration').value;if(duration!=='any'){const [min,max]=duration.split('-').map(Number);pairs=pairs.filter(p=>{const days=(new Date(p.ret+'T00:00:00Z')-new Date(p.out+'T00:00:00Z'))/86400000;return days>=min&&days<=max;});}if(!pairs.length)throw Error('No hay combinaciones con esa duración. Amplía las fechas o elige cualquier duración.');plan={destination,origins,travelers,lowcost:$('lowcost').checked,independent:$('independent').checked,pairs};$('date-pair').replaceChildren();pairs.forEach((p,i)=>{const o=document.createElement('option');o.value=i;o.textContent=`${p.out} → ${p.ret}${p.out===$('departure').value&&p.ret===$('return').value?' · fechas elegidas':''}`;$('date-pair').append(o);});$('summary').textContent=`${origins.length} aeropuertos · ${pairs.length} combinaciones de fechas · ${origins.length*pairs.length} consultas posibles · ${travelers} viajeros → ${destination}`;$('search-results').hidden=false;renderLinks();}catch(error){$('search-error').textContent=error.message;$('search-results').hidden=true;plan=null;}});
$('date-pair').addEventListener('change',renderLinks);
// Changing the form invalidates the generated plan so that stale links cannot be mistaken for updated results.
$('search-form').addEventListener('input',()=>{$('search-results').hidden=true;plan=null;});
$('export').addEventListener('click',()=>{if(!plan)return;const blob=new Blob([JSON.stringify({...plan,notice:'Plan de consultas. Sin disponibilidad ni precios verificados.'},null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='plan-viajeros-garabato.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
// Keep the compact date summary in sync with the actual form fields.
function syncDateLabels(){
 $('dates-label').textContent=$('departure').value ? $('departure').value.split('-').reverse().join('/') : 'Fechas flexibles';
 $('flex-label').textContent=Number($('flex').value) ? `± ${$('flex').value} días` : 'Fechas exactas';
}
for(const id of ['departure','return','flex']) $(id).addEventListener('input',syncDateLabels);
$('close-dates').addEventListener('click',()=>{$('date-settings').open=false;});
$('search-form').addEventListener('invalid',event=>{if(event.target.closest('#date-settings'))$('date-settings').open=true;},true);
