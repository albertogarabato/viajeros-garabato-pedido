(function(root){
'use strict';
class SearchClient {
  constructor(endpoint=''){this.endpoint=endpoint;}
  async search(request,{signal}={}){
    if(!this.endpoint)return {status:'unavailable',code:'PROVIDER_NOT_CONFIGURED',offers:[]};
    const url=new URL(this.endpoint);
    if(url.protocol!=='https:')throw Error('El servicio de búsqueda debe usar HTTPS.');
    const response=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(request),signal,credentials:'omit'});
    const data=await response.json();
    if(data.code==='PROVIDER_NOT_CONFIGURED')return {status:'unavailable',code:data.code,offers:[]};
    if(!response.ok)throw Error('El servicio de búsqueda no pudo completar la consulta. Inténtalo de nuevo más tarde.');
    if(data.status!=='complete'||!Array.isArray(data.offers))throw Error('El servicio devolvió una respuesta incompleta.');
    // Counts without composition/ages cannot establish exact family availability.
    if(!request.party)throw Error('Configura adultos y edades de menores antes de consultar precios reales.');
    const now=Date.now();
    const valid=data.offers.filter(o=>o.status==='live'&&o.currency==='EUR'&&Number.isInteger(o.totalMinor)&&o.totalMinor>0&&o.source&&Number.isFinite(Date.parse(o.checkedAt))&&Date.parse(o.checkedAt)<=now&&Date.parse(o.expiresAt)>now&&JSON.stringify(o.party)===JSON.stringify(request.party)&&Array.isArray(o.legs)&&o.legs.length>0);
    if(data.offers.length&&valid.length!==data.offers.length)throw Error('Hay ofertas sin precio vigente o sin disponibilidad confirmada para vuestra familia.');
    return {status:'complete',offers:valid,coverage:data.coverage||'limited'};
  }
}
root.FlightSearchClient=SearchClient;
})(typeof globalThis!=='undefined'?globalThis:this);
