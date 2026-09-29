import fs from 'node:fs';
import path from 'node:path';

export const formIds=[2,3,4,5,6,7,9,10,11,12,13,14,15,16,17,18,19,20];

export default function FormContent({kind,n}){
  const file=path.join(process.cwd(),'formularios',kind,`anexo-${String(n).padStart(2,'0')}.md`);
  if(!fs.existsSync(file))return <p>Formulario no disponible.</p>;
  const lines=fs.readFileSync(file,'utf8').split(/\r?\n/);
  const title=lines[0].replace(/^# /,'');
  let tables=[],current=[];
  for(const line of lines){
    if(line.startsWith('|')){
      if(!/^\|[\s\-|]+\|$/.test(line))current.push(line.slice(1,-1).split(/(?<!\\)\|/).map(c=>c.trim().replaceAll('\\|','|')));
    }else if(current.length){tables.push(current);current=[];}
  }
  if(current.length)tables.push(current);
  return <article className="form-paper"><div className="form-paper-top"><span>SIMULACION DE SISTEMA DE AUTORIA POR JOSE RAMOS</span><span>ANEXO {String(n).padStart(2,'0')}</span></div><h1>{title}</h1><p className="form-subtitle">Fuente de estructura: Sara María Romero (2012), anexo {n}. {kind==='diligenciados'?'Estado conocido; los pendientes no equivalen a pruebas ni aprobaciones.':'Plantilla para uso posterior.'}</p>{tables.map((rows,index)=><div className="form-table-wrap" key={index}><table className="form-table"><thead><tr>{rows[0].map((c,i)=><th key={i}>{c}</th>)}</tr></thead><tbody>{rows.slice(1).map((row,r)=><tr key={r}>{row.map((c,i)=><td key={i}>{c}</td>)}</tr>)}</tbody></table></div>)}</article>;
}
