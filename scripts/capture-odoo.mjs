// Captura la interfaz REAL de Odoo con Edge/CDP; lee el secreto sólo de archivo ignorado.
// Requiere Edge local iniciado con --headless=new --remote-debugging-port=9223.
import fs from 'node:fs';
import path from 'node:path';

const credentials = JSON.parse(fs.readFileSync('odoo/credenciales-locales.json', 'utf8'));
const page = await (await fetch('http://127.0.0.1:9223/json/new?about:blank', { method: 'PUT' })).json();
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject; });
let serial = 0;
const pending = new Map();
const pageErrors = [];
ws.onmessage = ({ data }) => {
  const msg = JSON.parse(data);
  if (msg.method === 'Runtime.exceptionThrown') pageErrors.push(msg.params.exceptionDetails.text);
  if (!pending.has(msg.id)) return;
  const { resolve, reject } = pending.get(msg.id);
  pending.delete(msg.id);
  msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result);
};
const send = (method, params = {}) => new Promise((resolve, reject) => {
  const id = ++serial;
  pending.set(id, { resolve, reject });
  ws.send(JSON.stringify({ id, method, params }));
});
const evaluate = async expression => {
  const result = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text);
  return result.result.value;
};
const waitFor = async (predicate, tries = 40) => {
  for (let i = 0; i < tries; i++) {
    if (await evaluate(predicate)) return;
    await new Promise(r => setTimeout(r, 500));
  }
  throw new Error('La interfaz no mostró el estado esperado; no tomar captura como evidencia.');
};
const navigate = async url => {
  await send('Page.navigate', { url });
  await waitFor('document.readyState === "complete" && document.body != null');
};
const capture = async name => {
  const file = path.join('evidencias', 'odoo', `${name}.png`);
  const { data } = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, Buffer.from(data, 'base64'));
  console.log(`${file} (${fs.statSync(file).size} bytes) URL=${await evaluate('location.href')}`);
};
try {
  await send('Page.enable');
  await send('Runtime.enable');
  await send('Network.enable');
  await send('Network.clearBrowserCookies');
  await send('Storage.clearDataForOrigin', {origin:'http://127.0.0.1:8070',storageTypes:'all'});
  await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
  await navigate('http://127.0.0.1:8070/web/login?db=audit_sim');
  await waitFor('!!document.querySelector(".oe_login_form")', 60);
  if (!process.env.ONLY_ROLES && !process.env.ONLY_MOVES && !process.env.ONLY_FINISHED) await capture('acceso-odoo-18');
  const login = async (user, expectedUid) => {
    if (!await evaluate('!!document.querySelector(".oe_login_form") && !document.querySelector(".oe_login_form").classList.contains("d-none")')) {
      await evaluate('Array.from(document.querySelectorAll("span")).find(a=>a.innerText.includes("Use another user"))?.closest("a,button")?.click()');
      await waitFor('!!document.querySelector(".oe_login_form") && !document.querySelector(".oe_login_form").classList.contains("d-none")', 30);
    }
    const expression = `(() => {
    document.querySelector('input[name=login]').value = ${JSON.stringify(user)};
    document.querySelector('input[name=password]').value = ${JSON.stringify(credentials[user])};
    document.querySelector('.oe_login_form').requestSubmit();
    return true;
  })()`;
    await evaluate(expression);
    await waitFor('location.pathname.startsWith("/odoo") && document.querySelector(".o_web_client") != null', 100);
    await waitFor('document.body.innerText.includes("Inbox")', 160);
    const currentUid = await evaluate('fetch("/web/session/get_session_info", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({jsonrpc:"2.0",params:{}})}).then(r=>r.json()).then(data=>data.result?.uid)');
    if (currentUid !== expectedUid) throw new Error(`Sesión inesperada: UID=${currentUid}, se esperaba ${expectedUid}`);
  };
  await login('admin', 2);
  if (!process.env.ONLY_ROLES) {
    if (!process.env.ONLY_MOVES && !process.env.ONLY_FINISHED) {
      console.log('Odoo autenticado; contenido visible: ' + (await evaluate('document.body.innerText.slice(0, 350)')).replaceAll('\n', ' | '));
      await capture('panel-odoo-18');
    }
  const adminActions = [
    ['productos-odoo', 391, 'Products'],
    ['usuarios-odoo', 70, 'Users'],
    ['facturas-odoo', 263, 'Invoices'],
    ['compras-borrador-odoo', 417, 'Requests for Quotation'],
    ['ventas-borrador-odoo', 451, 'Quotations'],
    ['movimientos-inventario-odoo', 358, 'Moves History'],
  ];
  const finishedActions = [
    ['recepcion-completada-odoo', 'stock.picking/19', 'AH/IN/00001'],
    ['entrega-completada-odoo', 'stock.picking/20', 'AH/OUT/00001'],
    ['factura-cliente-pagada-odoo', 'action-263/28', 'INV/2026/00001'],
    ['factura-proveedor-pagada-odoo', 'action-266/27', 'BILL/2026/09/0001'],
    ['cobro-cliente-odoo', 'action-239/2', 'PBNK1/2026/00002'],
    ['pago-proveedor-odoo', 'action-240/1', 'PBNK1/2026/00001'],
  ];
  const actions = process.env.ONLY_FINISHED ? finishedActions : process.env.ONLY_MOVES ? adminActions.slice(-1) : adminActions;
  for (const [name, action, expected] of actions) {
    const segment = typeof action === 'number' ? `action-${action}` : action;
    await navigate(`http://127.0.0.1:8070/odoo/${segment}?cids=3`);
    await waitFor(`document.body.innerText.includes(${JSON.stringify(expected)}) && document.querySelector('.o_action_manager') != null`, 160);
    await new Promise(r => setTimeout(r, 1500));
    console.log(name + ': ' + (await evaluate('document.body.innerText.slice(0, 400)')).replaceAll('\n', ' | '));
    await capture(name);
  }
  }
  if (!process.env.ONLY_ADMIN && !process.env.ONLY_MOVES && !process.env.ONLY_FINISHED) for (const [user, uid, action, id, section, name] of [
    ['lucia.montes@horizonte.example', 10, 451, 27, 'Quotations', 'lucia-acceso-venta'],
    ['diego.rios@horizonte.example', 11, 417, 13, 'Requests for Quotation', 'diego-acceso-compra'],
  ]) {
    await send('Network.clearBrowserCookies');
    await send('Storage.clearDataForOrigin', {origin:'http://127.0.0.1:8070',storageTypes:'all'});
    await navigate('http://127.0.0.1:8070/web/login?db=audit_sim');
    await waitFor('location.pathname === "/web/login" && !!document.querySelector(".oe_login_form")', 120);
    await login(user, uid);
    await navigate(`http://127.0.0.1:8070/odoo/action-${action}/${id}?cids=3`);
    await waitFor(`document.body.innerText.includes(${JSON.stringify(section)})`, 160);
    console.log(`${name}: UID=${uid}; sección ${section} visible; permiso de registro comprobado aparte por XML-RPC`);
    await capture(name);
  }
} catch (error) {
  console.error('UI:', JSON.stringify(await evaluate('({url:location.href,text:document.body?.innerText.slice(0,600),body:document.body?.className,inputs:Array.from(document.querySelectorAll("input")).map(x=>x.name),forms:Array.from(document.querySelectorAll("form")).map(x=>x.className),switchers:Array.from(document.querySelectorAll("*")).filter(a=>a.children.length===0&&a.textContent?.includes("Use another user")).map(a=>({tag:a.tagName,class:a.className,html:a.outerHTML.slice(0,300)})).slice(0,3)})')));
  console.error('Errores del navegador:', pageErrors.slice(-4));
  throw error;
} finally {
  ws.close();
}
