import fs from 'node:fs';
import path from 'node:path';
const ids=[2,3,4,5,6,7,9,10,11,12,13,14,15,16,17,18,19,20];
let fail=0;
for(const kind of ['vacios','diligenciados'])for(const n of ids){const file=path.join('formularios',kind,`anexo-${String(n).padStart(2,'0')}.md`);if(!fs.existsSync(file)||!fs.readFileSync(file,'utf8').startsWith(`# Anexo ${n}`)){console.error('Falta o no es Markdown:',file);fail++;}}
for(const f of ['diagramas/anexo-01-interaccion.mmd','diagramas/anexo-08-comunicaciones.mmd','docs/EDT.md','docs/cronograma.csv'])if(!fs.existsSync(f)){console.error('Falta:',f);fail++;}
const rows=fs.readFileSync('docs/trazabilidad.csv','utf8').trim().split(/\r?\n/).slice(1);
let captures=0;
for(const row of rows){const columns=row.split(',');const capture=columns[6]?.trim();if(!capture)continue;captures++;if(!fs.existsSync(capture)){console.error('Captura referida inexistente:',capture);fail++;continue;}const bytes=fs.readFileSync(capture);if(bytes.length<1000||bytes.subarray(0,8).toString('hex')!=='89504e470d0a1a0a'){console.error('Captura no es PNG válido:',capture);fail++;}}
for(const n of ids){const image=`evidencias/formularios/anexo-${String(n).padStart(2,'0')}.png`;if(!fs.existsSync(image)){console.error('Falta captura de formulario:',image);fail++;}}
console.log(`Formularios: ${ids.length} vacíos + ${ids.length} diligenciados; referencias de captura PNG: ${captures}. Fallos: ${fail}`);
if(fail)process.exitCode=1;
