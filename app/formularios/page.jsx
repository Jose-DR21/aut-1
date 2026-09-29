import Link from 'next/link';
import FormContent,{formIds} from '../formulario/form-content';

export default function AllForms(){
  return <main className="form-page form-collection"><div className="form-toolbar"><Link href="/#formularios">← Volver al inicio</Link><span>18 FORMULARIOS DILIGENCIADOS</span><Link href="/galeria">Galería de capturas ↗</Link></div><nav className="form-collection-index" aria-label="Ir a un anexo">{formIds.map(n=><a key={n} href={`#anexo-${n}`}>Anexo {String(n).padStart(2,'0')}</a>)}</nav>{formIds.map(n=><section id={`anexo-${n}`} key={n} className="form-collection-item"><FormContent kind="diligenciados" n={n}/></section>)}</main>;
}
