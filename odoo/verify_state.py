"""Lecturas XML-RPC de audit_sim; exporta hechos, nunca credenciales.

No sustituye las pruebas manuales de segregación, conciliación ni autorizaciones.
"""
import datetime
import json
from pathlib import Path
import xmlrpc.client

secrets = json.loads((Path(__file__).parent / 'credenciales-locales.json').read_text(encoding='utf-8'))
db, url = 'audit_sim', 'http://127.0.0.1:8070/xmlrpc/2/'
common = xmlrpc.client.ServerProxy(url + 'common', allow_none=True)
uid = common.authenticate(db, 'admin', secrets['admin'], {})
if not uid:
    raise RuntimeError('No autentica admin: abortar lectura.')
api = xmlrpc.client.ServerProxy(url + 'object', allow_none=True)

def search_read(model, domain, fields):
    return api.execute_kw(db, uid, secrets['admin'], model, 'search_read', [domain], {'fields': fields})

data = {
    'tipo': 'simulacion_academica',
    'capturado_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
    'base': db,
    'version': common.version()['server_version'],
    'modulos': search_read('ir.module.module', [('name', 'in', ['stock', 'account', 'purchase', 'sale_management'])], ['name', 'state']),
    'empresa': search_read('res.company', [('name', '=', 'Autopartes Horizonte')], ['name', 'chart_template']),
    'almacen': search_read('stock.warehouse', [('company_id', '=', 3)], ['name', 'company_id', 'lot_stock_id']),
    'productos': search_read('product.template', [('default_code', 'in', ['AH-FLT-001', 'AH-BAT-002', 'AH-FRE-003'])], ['default_code', 'name', 'is_storable', 'list_price']),
    'usuarios': search_read('res.users', [('login', 'like', '%@horizonte.example')], ['name', 'login', 'company_id', 'groups_id']),
    'existencias': search_read('stock.quant', [('location_id', '=', 39), ('product_id.default_code', 'in', ['AH-FLT-001', 'AH-BAT-002', 'AH-FRE-003'])], ['product_id', 'quantity', 'location_id']),
    'compras': search_read('purchase.order', [('origin', '=', 'SIM-AUTO-PO-001')], ['name', 'state', 'partner_id', 'amount_total', 'picking_ids', 'invoice_ids', 'invoice_status']),
    'ventas': search_read('sale.order', [('client_order_ref', '=', 'SIM-AUTO-SO-001')], ['name', 'state', 'partner_id', 'amount_total', 'picking_ids', 'invoice_ids', 'invoice_status']),
    'transferencias': search_read('stock.picking', [('id', 'in', [19, 20]), ('company_id', '=', 3)], ['name', 'origin', 'state', 'date_done', 'move_ids']),
    'movimientos_stock': search_read('stock.move', [('id', 'in', [41, 42, 43, 44, 45]), ('company_id', '=', 3)], ['product_id', 'quantity', 'state', 'location_id', 'location_dest_id', 'picking_id']),
    'facturas': search_read('account.move', [('id', 'in', [25, 26, 27, 28]), ('company_id', '=', 3)], ['ref', 'move_type', 'state', 'name', 'amount_total', 'amount_residual', 'payment_state', 'invoice_origin', 'journal_id']),
    'pagos': search_read('account.payment', [('company_id', '=', 3)], ['name', 'state', 'payment_type', 'amount', 'journal_id', 'move_id', 'reconciled_invoice_ids', 'reconciled_bill_ids']),
    'asientos_pago': search_read('account.move', [('id', 'in', [29, 30]), ('company_id', '=', 3)], ['name', 'state', 'journal_id', 'amount_total']),
}
for login in ['elena.salcedo@horizonte.example', 'martin.varela@horizonte.example', 'lucia.montes@horizonte.example', 'diego.rios@horizonte.example']:
    account_id = common.authenticate(db, login, secrets[login], {})
    data.setdefault('autenticacion', []).append({'login': login, 'autenticado': bool(account_id), 'id': account_id or None})

output = Path('docs/estado-odoo.json')
output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Lecturas registradas en {output}; credenciales omitidas. Módulos={len(data["modulos"])}, usuarios={len(data["usuarios"])}.')
