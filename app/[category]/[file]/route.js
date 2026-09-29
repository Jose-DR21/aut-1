import fs from 'node:fs';
import path from 'node:path';
export async function GET(_request,{params}){
  const {category,file}=await params;
  if(category==='capturas' && /^anexo-(0[2-7]|09|1[0-9]|20)\.png$/.test(file)){
    const image=path.join(process.cwd(),'evidencias','formularios',file);
    if(!fs.existsSync(image))return new Response('Captura no disponible',{status:404});
    return new Response(fs.readFileSync(image),{headers:{'Content-Type':'image/png'}});
  }
  if(category==='capturas-odoo' && /^[a-z0-9][a-z0-9-]*\.png$/.test(file)){
    const image=path.join(process.cwd(),'evidencias','odoo',file);
    if(!fs.existsSync(image))return new Response('Captura no disponible',{status:404});
    return new Response(fs.readFileSync(image),{headers:{'Content-Type':'image/png'}});
  }
  const allowed={docs:['00-correspondencia.md','EDT.md','cronograma.csv','trazabilidad.csv','guia-evidencia.md','estado-odoo.json','pruebas-acceso-odoo.json','conciliacion-inventario.json','conciliacion-financiera.json','hallazgos-control.md','RELEVO.md'],diagramas:['anexo-01-interaccion.mmd','anexo-08-comunicaciones.mmd']};
  if(!allowed[category]?.includes(file))return new Response('No encontrado',{status:404});
  const filePath=path.join(process.cwd(),category,file);
  return new Response(fs.readFileSync(filePath),{headers:{'Content-Type':file.endsWith('.csv')?'text/csv; charset=utf-8':file.endsWith('.json')?'application/json; charset=utf-8':'text/plain; charset=utf-8','Content-Disposition':`inline; filename="${file}"`}});
}
