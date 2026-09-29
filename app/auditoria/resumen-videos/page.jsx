const pdf = '/documentos/resumen-personal-videos-auditoria.pdf';

export const metadata = {
  title: 'Resumen personal de los videos | Auditoría Odoo',
  description: 'Resumen personal de Jose Ramos sobre los videos de auditoría de sistemas.',
};

export default function ResumenVideos() {
  return <main className="pdf-page"><div className="pdf-container"><nav className="pdf-nav" aria-label="Volver"><a href="/auditoria">← Auditoría</a><a href="/galeria">Galería de capturas</a></nav><header className="pdf-header"><span>DOCUMENTO PERSONAL / PDF</span><h1>Resumen de los videos</h1><p>Mi resumen personal sobre las funciones y la organización de la auditoría de sistemas. Este documento complementa la actividad; no es un informe de resultados de Odoo.</p><a href={pdf} target="_blank" rel="noopener noreferrer">Abrir PDF en otra pestaña ↗</a></header><div className="pdf-frame"><iframe title="Resumen personal sobre los videos de auditoría de sistemas" src={pdf} loading="lazy"/><p>Si el visor integrado no funciona en tu navegador, <a href={pdf} target="_blank" rel="noopener noreferrer">abre el PDF directamente</a>.</p></div></div></main>;
}
