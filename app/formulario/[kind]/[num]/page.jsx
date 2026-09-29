import Link from 'next/link';
import FormContent,{formIds} from '../../form-content';

export default async function FormPage({params}){
  const {kind,num}=await params;
  const n=Number(num);
  if(!['vacios','diligenciados'].includes(kind)||!formIds.includes(n))return <div>Formulario no disponible</div>;
  return <main className="form-page"><div className="form-toolbar"><Link href="/#formularios">← Formularios</Link><span>SIMULACIÓN ACADÉMICA · {kind==='vacios'?'PLANTILLA VACÍA':'ESTADO DOCUMENTADO'}</span><Link href="/formularios">Ver los 18 formularios ↗</Link></div><FormContent kind={kind} n={n}/></main>;
}
