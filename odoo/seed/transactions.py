"""Crea operaciones trazables sólo si los módulos y la configuración las permiten.

No marca transferencias/facturas/pagos como terminados al recibir un wizard.
Las excepciones se informan para investigar en UI; no se fabrican resultados.
"""
import datetime as dt
import json
import os
from pathlib import Path
import sys
import xmlrpc.client

db = os.environ.get('ODOO_DB', 'audit_sim')
url = os.environ.get('ODOO_URL', 'http://127.0.0.1:8070')
login = os.environ.get('ODOO_LOGIN', 'admin')
secrets_file = Path(__file__).resolve().parent.parent / 'credenciales-locales.json'
if not secrets_file.exists():
    sys.exit('No existe el archivo local de credenciales.')
password = json.loads(secrets_file.read_text(encoding='utf-8')).get(login)
if not password:
    sys.exit('No existe contraseña local para el login seleccionado.')
common = xmlrpc.client.ServerProxy(url + '/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(db, login, password, {})
if not uid:
    sys.exit('Autenticación fallida: no crear operaciones.')
api = xmlrpc.client.ServerProxy(url + '/xmlrpc/2/object', allow_none=True)

def call(model, method, *args, **kw):
    return api.execute_kw(db, uid, password, model, method, list(args), kw)

def record(model, domain, fields=None):
    ids = call(model, 'search', domain, limit=1)
    if not ids:
        raise RuntimeError(f'Falta {model} {domain}; detener y verificar en Odoo')
    return (ids[0], call(model, 'read', ids, fields=fields)[0] if fields else None)

company, _ = record('res.company', [('name', '=', 'Autopartes Horizonte')])
vendor, _ = record('res.partner', [('name', '=', 'Rodamientos Boreal')])
client, _ = record('res.partner', [('name', '=', 'Taller Ronda')])
products = {}
for code in ['AH-FLT-001', 'AH-BAT-002', 'AH-FRE-003']:
    products[code], _ = record('product.product', [('default_code', '=', code)])
warehouse, wh = record('stock.warehouse', [('company_id', '=', company)], ['lot_stock_id'])
location = wh['lot_stock_id'][0]
now = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Cada cuantificación provoca su propio movimiento de ajuste y queda vinculada a un ID.
for code, qty in [('AH-FLT-001', 20), ('AH-BAT-002', 8), ('AH-FRE-003', 12)]:
    existing = call('stock.quant', 'search_read', [('product_id', '=', products[code]), ('location_id', '=', location)], fields=['quantity'], limit=1)
    if existing and existing[0]['quantity']:
        print(f'Inventario ya presente {code}: quant ID={existing[0]["id"]} qty={existing[0]["quantity"]}; sin duplicar')
        continue
    quant = call('stock.quant', 'create', {'product_id': products[code], 'location_id': location, 'inventory_quantity': qty}, context={'inventory_mode': True})
    try:
        result = call('stock.quant', 'action_apply_inventory', [quant], context={'inventory_mode': True})
    except xmlrpc.client.Fault as error:
        # Odoo 18 aplica y confirma el ajuste antes de intentar serializar None.
        # Sólo tolerar ese error específico tras releer la cantidad real.
        if 'cannot marshal None' not in error.faultString:
            raise
        result = 'respuesta XML-RPC None no serializable; verificado por lectura posterior'
    updated = call('stock.quant', 'read', [quant], fields=['quantity'])[0]['quantity']
    if updated != qty:
        raise RuntimeError(f'Ajuste {code} no comprobado: quant {quant} cantidad={updated}')
    print(f'Ajuste {code}: quant ID={quant} cantidad={updated}, {result}')

po_ids = call('purchase.order', 'search', [('origin', '=', 'SIM-AUTO-PO-001'), ('company_id', '=', company)], limit=1)
if po_ids:
    po = po_ids[0]
else:
    po = call('purchase.order', 'create', {
        'partner_id': vendor, 'company_id': company, 'origin': 'SIM-AUTO-PO-001', 'date_order': now,
        'order_line': [(0, 0, {'product_id': products['AH-FLT-001'], 'name': 'Filtro de aceite AH-01', 'product_qty': 5, 'price_unit': 18, 'date_planned': now})],
    })
print(f'Compra ID={po} estado={call("purchase.order", "read", [po], fields=["state"])[0]["state"]}')

so_ids = call('sale.order', 'search', [('client_order_ref', '=', 'SIM-AUTO-SO-001'), ('company_id', '=', company)], limit=1)
if so_ids:
    so = so_ids[0]
else:
    so = call('sale.order', 'create', {
        'partner_id': client, 'company_id': company, 'client_order_ref': 'SIM-AUTO-SO-001', 'date_order': now,
        'order_line': [(0, 0, {'product_id': products['AH-FLT-001'], 'name': 'Filtro de aceite AH-01', 'product_uom_qty': 2, 'price_unit': 32})],
    })
print(f'Venta ID={so} estado={call("sale.order", "read", [so], fields=["state"])[0]["state"]}')

for marker, move_type, partner, price, qty in [
    ('SIM-AUTO-V-001', 'out_invoice', client, 32, 2),
    ('SIM-AUTO-C-001', 'in_invoice', vendor, 18, 5),
]:
    ids = call('account.move', 'search', [('ref', '=', marker), ('company_id', '=', company)], limit=1)
    if ids:
        move = ids[0]
    else:
        move = call('account.move', 'create', {
            'move_type': move_type, 'partner_id': partner, 'company_id': company, 'ref': marker,
            'invoice_date': dt.date.today().isoformat(),
            'invoice_line_ids': [(0, 0, {'product_id': products['AH-FLT-001'], 'name': 'Filtro de aceite AH-01', 'quantity': qty, 'price_unit': price})],
        })
    fields = call('account.move', 'read', [move], fields=['state', 'name', 'amount_total', 'payment_state'])[0]
    print(f'Factura {marker}: ID={move} {fields}')

print('Operaciones base creadas. Confirmar recepciones/entregas/facturas/pagos en interfaz; estados no asumidos.')
