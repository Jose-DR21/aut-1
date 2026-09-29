import fs from 'node:fs';
import path from 'node:path';
import GalleryViewer from './gallery-viewer';

const labels={
  'acceso-odoo-18.png':'Acceso a Odoo',
  'panel-odoo-18.png':'Panel de Odoo',
  'login-odoo.png':'Inicio de sesión (captura histórica)',
  'productos-odoo.png':'Productos',
  'usuarios-odoo.png':'Usuarios',
  'movimientos-inventario-odoo.png':'Movimientos de inventario',
  'compras-borrador-odoo.png':'Compra antes de confirmar · histórico',
  'ventas-borrador-odoo.png':'Venta antes de confirmar · histórico',
  'facturas-odoo.png':'Factura anterior · histórico',
  'diego-acceso-compra.png':'Prueba de acceso de Diego · histórico',
  'lucia-acceso-venta.png':'Prueba de acceso de Lucía · histórico',
  'recepcion-completada-odoo.png':'Recepción completada',
  'entrega-completada-odoo.png':'Entrega completada',
  'factura-cliente-pagada-odoo.png':'Factura de cliente pagada',
  'factura-proveedor-pagada-odoo.png':'Factura de proveedor pagada',
  'cobro-cliente-odoo.png':'Cobro de cliente',
  'pago-proveedor-odoo.png':'Pago a proveedor',
};

function images(directory, route){
  const folder=path.join(process.cwd(),'evidencias',directory);
  return fs.readdirSync(folder).filter(file=>/^[a-z0-9][a-z0-9-]*\.png$/.test(file)).sort().map(file=>({file,url:`/${route}/${file}`}));
}

export default function GalleryPage(){
  const odoo=images('odoo','capturas-odoo').map(item=>({...item,label:labels[item.file]||item.file,group:'Odoo'}));
  const forms=images('formularios','capturas').map(item=>({...item,label:`Anexo ${item.file.slice(6,8)}`,group:'Formularios'}));
  return <main className="gallery-page"><div className="gallery-container"><a className="gallery-back" href="/">← Volver al inicio</a><header><span className="gallery-eyebrow">EVIDENCIA VISUAL</span><h1>Galería de capturas</h1><p>{odoo.length+forms.length} imágenes del laboratorio: pantallas de Odoo y formularios diligenciados. Las capturas históricas muestran el estado en que fueron tomadas, no el estado actual del registro.</p></header><GalleryViewer groups={[{title:'Odoo',description:'Pantallas del entorno, operaciones y pruebas de acceso.',items:odoo},{title:'Formularios',description:'Capturas de los 18 anexos diligenciados; su contenido no sustituye los registros de Odoo.',items:forms}]}/></div></main>;
}
