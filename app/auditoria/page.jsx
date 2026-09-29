const groups=[
  {name:'Iniciación',ids:[2,3],description:'Acta constitutiva e involucrados del caso ficticio.'},
  {name:'Planificación',ids:[4,5,6,7],description:'Alcance, cronograma, calidad y desarrollo individual. Anexo 8: comunicaciones.'},
  {name:'Ejecución',ids:[9,10,11],description:'Flujos comerciales y capturas del laboratorio; cambio de roles propuesto, no implantado.'},
  {name:'Seguimiento y control',ids:[12,13,14,15,16],description:'Desfase >10 %, demora máxima de 3 días y seguimiento sin aprobaciones anticipadas.'},
  {name:'Cierre',ids:[17,18,19,20],description:'Informe y evaluación como borradores: no hay cierre ni opinión auditora.'}
];
const names={2:'Acta constitutiva',3:'Involucrados',4:'Alcance',5:'Programación',6:'Aseguramiento de calidad',7:'Desarrollo individual',9:'Estado de auditoría',10:'Solicitud de cambio',11:'Contingencias',12:'Control de programación',13:'Lista de chequeo',14:'Control de cambios',15:'Comunicaciones',16:'Capacitación',17:'Informe de auditoría',18:'Activos de procesos',19:'Lecciones aprendidas',20:'Informe de cierre'};

export default function Home(){
  return <main className="simple-site">
    <header className="simple-nav"><a href="/" className="simple-brand">JR <span>/ portafolio</span></a><nav><a href="/">Portafolio</a><a href="#etapas">Etapas</a><a href="#formularios">Formularios</a><a href="/galeria">Capturas</a></nav></header>
    <section className="simple-hero" id="inicio"><div className="simple-container"><span className="simple-badge">SIMULACIÓN ACADÉMICA · 2026</span><h1>Simulacion de sistema<br/>de autoria por <em>Jose Ramos</em></h1><p>Auditoría informática de Inventario y Facturación en Odoo para Autopartes Horizonte, empresa del caso de estudio.</p><div className="simple-hero-actions"><a href="/formularios" className="simple-cta">Ver los 18 formularios ↗</a><a href="/galeria" className="simple-cta">Ver todas las capturas ↗</a><a href="/auditoria/resumen-videos" className="simple-cta">Ver mi resumen de los videos ↗</a></div></div></section>
    <section className="simple-container simple-section" id="etapas"><div className="simple-heading"><span>METODOLOGÍA DE ROMERO / PMBOK</span><h2>Cinco etapas, en orden.</h2><p>Los anexos están asociados a las decisiones y controles de su etapa. El proyecto permanece abierto hasta completar pruebas reales.</p></div><div className="simple-stages">{groups.map((g,i)=><article key={g.name}><span className="simple-num">0{i+1}</span><div><h3>{g.name}</h3><p>{g.description}</p><small>Anexos {g.ids.join(', ')}</small></div></article>)}</div></section>
    <section className="simple-section simple-files" id="formularios"><div className="simple-container"><div className="simple-heading simple-files-header"><span>DOCUMENTOS DEL CASO</span><a className="simple-cta" href="/formularios">Ver los 18 formularios ↗</a></div>{groups.map(g=><div className="simple-form-group" key={g.name}><h3>{g.name}</h3><div className="simple-form-grid">{g.ids.map(n=><a key={n} href={`/formulario/diligenciados/${n}`}><span>Anexo {String(n).padStart(2,'0')}</span><strong>{names[n]}</strong><span className="simple-arrow">↗</span></a>)}</div></div>)}</div></section>
    <section className="simple-container simple-bottom simple-bottom-links-only"><div className="simple-links"><a href="/galeria">Ver todas las capturas ↗</a><a href="/formularios">Ver los 18 formularios ↗</a></div></section>
    <footer className="simple-footer"><div className="simple-container">SIMULACIÓN ACADÉMICA · Sara María Romero, «Una metodología para la gestión de proyectos de auditoría informática bajo el enfoque PMI», Rev. Tecnol. 11(1), 2012, pp. 9–23. El anexo 1 se atribuye en la fuente a PMBOK (2008).</div></footer>
  </main>;
}
