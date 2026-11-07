(function(root){
'use strict';
class SearchClient {
 constructor(endpoint=''){this.endpoint=endpoint;}
 async search(request,{signal,accessCode}={}){
  if(!this.endpoint)return {status:'unavailable',offers:[]};
  const url=new URL(this.endpoint);
  if(url.protocol!=='https:')throw Error('El servicio de búsqueda debe usar HTTPS.');
  if(!accessCode||accessCode.length<12)throw Error('Introduce la clave de acceso familiar.');
  const response=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer '+accessCode},body:JSON.stringify(request),signal,credentials:'omit'});
  let data;try{data=await response.json();}catch{throw Error('No se recibió una respuesta válida del servicio.');}
  if(!response.ok)throw Error(typeof data.message==='string'?data.message:'No se pudo completar la búsqueda.');
  if(!['observed','partial'].includes(data.status)||!data.query||JSON.stringify(data.query.party)!==JSON.stringify(request.party))throw Error('La respuesta no corresponde a los viajeros solicitados.');
  if(data.query.outboundDate!==request.outboundDate||data.query.returnDate!==request.returnDate||data.query.destination!==request.destination||[...data.query.origins].sort().join()!==[...request.origins].sort().join())throw Error('La respuesta no corresponde a esta ruta y fechas.');
  for(const [direction,date] of [['outbound',request.outboundDate],['inbound',request.returnDate]]){
   if(!Array.isArray(data[direction]?.offers))throw Error('La fuente devolvió una respuesta incompleta.');
   for(const o of data[direction].offers){
    if(o.status!=='observed'||o.currency!=='EUR'||!Number.isInteger(o.displayedPriceMinor)||o.displayedPriceMinor<=0||!o.source||!Number.isFinite(Date.parse(o.checkedAt))||Date.parse(o.checkedAt)>Date.now()+60000||Date.now()-Date.parse(o.checkedAt)>20*60000||!Array.isArray(o.legs)||!o.legs.length||o.legs.length>2||!o.legs[0].departureLocal.startsWith(date))throw Error('Hay resultados sin precio observado válido o fuera de fecha.');
   }
  }
  return data;
 }
}
root.FlightSearchClient=SearchClient;
})(typeof globalThis!=='undefined'?globalThis:this);
