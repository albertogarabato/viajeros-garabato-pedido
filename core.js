(function(root){
'use strict';
const dateRE = /^\d{4}-\d{2}-\d{2}$/;
function day(value){if(!dateRE.test(value))throw Error('Fecha no válida.');const d=new Date(value+'T00:00:00Z');if(!Number.isFinite(+d)||d.toISOString().slice(0,10)!==value)throw Error('Fecha no válida.');return d;}
function shifted(value,delta){const d=day(value);d.setUTCDate(d.getUTCDate()+delta);return d.toISOString().slice(0,10);}
function combinations(departure,back,flex,today){day(departure);day(back);day(today);if(back<departure)throw Error('La vuelta no puede ser anterior a la salida.');if(departure<today)throw Error('La salida no puede estar en el pasado.');if(![0,1,3,7].includes(flex))throw Error('Flexibilidad no válida.');let pairs=[];for(let i=-flex;i<=flex;i++)for(let j=-flex;j<=flex;j++){const out=shifted(departure,i),ret=shifted(back,j);if(out>=today&&ret>=out)pairs.push({out,ret,offset:Math.abs(i)+Math.abs(j)});}return pairs.sort((a,b)=>a.offset-b.offset||a.out.localeCompare(b.out)||a.ret.localeCompare(b.ret));}
function total(person,travelers,extras){if(!Number.isInteger(travelers)||travelers<1||travelers>9)throw Error('Indica entre 1 y 9 viajeros.');if(![person,...extras].every(n=>Number.isFinite(n)&&n>=0)||person===0)throw Error('Introduce un precio por persona mayor que cero y todos los extras (0 si no hay).');return Math.round((person*travelers+extras.reduce((a,b)=>a+b,0))*100)/100;}
root.TravelCore={combinations,total};
})(typeof globalThis!=='undefined'?globalThis:this);
