// Capturas reales de las páginas Next.js de cada formulario diligenciado.
// Requiere Next.js en 127.0.0.1:3001 (o FORM_PORT) y Edge CDP local en puerto 9223.
import fs from 'node:fs';
const target = await (await fetch('http://127.0.0.1:9223/json/new?about:blank', {method:'PUT'})).json();
const socket = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((ok, fail) => { socket.onopen=ok; socket.onerror=fail; });
let id=0;const pending=new Map();
socket.onmessage=({data})=>{const msg=JSON.parse(data);if(!pending.has(msg.id))return;const [ok,fail]=pending.get(msg.id);pending.delete(msg.id);msg.error?fail(new Error(msg.error.message)):ok(msg.result);};
const send=(method,params={})=>new Promise((ok,fail)=>{const key=++id;pending.set(key,[ok,fail]);socket.send(JSON.stringify({id:key,method,params}));});
const evalJs=async expression=>(await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true})).result.value;
const ids=[2,3,4,5,6,7,9,10,11,12,13,14,15,16,17,18,19,20];
const port=process.env.FORM_PORT || '3001';
try{
  await send('Page.enable');await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
  for(const n of ids){
    await send('Page.navigate',{url:`http://127.0.0.1:${port}/formulario/diligenciados/${n}`});
    let ready=false;
    for(let i=0;i<60;i++){
      ready=await evalJs(`document.readyState === 'complete' && document.body?.innerText.includes('Anexo ${n}')`);
      if(ready)break;
      await new Promise(r=>setTimeout(r,500));
    }
    if(!ready)throw new Error(`Formulario ${n} no visible; no guardar captura`);
    await evalJs('document.fonts.ready');
    const {data}=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});
    const name=`evidencias/formularios/anexo-${String(n).padStart(2,'0')}.png`;
    fs.writeFileSync(name,Buffer.from(data,'base64'));
    console.log(`${name} ${fs.statSync(name).size} bytes`);
  }
}finally{socket.close();}
