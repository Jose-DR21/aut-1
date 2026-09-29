"""Factura órdenes ya entregadas/recibidas mediante las acciones nativas Odoo.

Conserva los borradores independientes 25/26 hasta verificar facturas vinculadas.
Después cancela sólo esos borradores, y publica las facturas nuevas verificadas.
No crea pagos ni inventa asientos. Se puede reejecutar sin duplicar facturas.
"""
import json
from pathlib import Path
import xmlrpc.client

password = json.loads((Path(__file__).resolve().parent.parent / 'credenciales-locales.json').read_text(encoding='utf-8'))['admin']
db, url = 'audit_sim', 'http://127.0.0.1:8070/xmlrpc/2/'
uid = xmlrpc.client.ServerProxy(url + 'common').authenticate(db, 'admin', password, {})
if not uid:
    raise RuntimeError('No autentica admin; detener.')
api = xmlrpc.client.ServerProxy(url + 'object', allow_none=True)

def call(model, method, *args, **kwargs):
    return api.execute_kw(db, uid, password, model, method, list(args), kwargs)

def order(model, order_id, expected_name, expected_state):
    fields = ['name', 'state', 'invoice_ids', 'invoice_status', 'amount_total', 'company_id']
    row = call(model, 'read', [order_id], fields=fields)[0]
    if row['name'] != expected_name or row['state'] != expected_state or row['company_id'][0] != 3:
        raise RuntimeError(f'{model} ID {order_id}: datos fuera del caso; detener.')
    return row

purchase = order('purchase.order', 13, 'P00013', 'purchase')
sale = order('sale.order', 27, 'S00027', 'sale')
for picking_id in [19, 20]:
    if call('stock.picking', 'read', [picking_id], fields=['state'])[0]['state'] != 'done':
        raise RuntimeError(f'Picking {picking_id} no está done; no facturar.')

if not purchase['invoice_ids']:
    if purchase['invoice_status'] != 'to invoice':
        raise RuntimeError('Compra no indica to invoice; detener.')
    call('purchase.order', 'action_create_invoice', [13])
    purchase = order('purchase.order', 13, 'P00013', 'purchase')
if not sale['invoice_ids']:
    if sale['invoice_status'] != 'to invoice':
        raise RuntimeError('Venta no indica to invoice; detener.')
    wizard = call('sale.advance.payment.inv', 'create', {'sale_order_ids': [(6, 0, [27])], 'advance_payment_method': 'delivered'})
    try:
        call('sale.advance.payment.inv', 'create_invoices', [wizard])
    except xmlrpc.client.Fault as error:
        # Odoo 18 puede confirmar la creación pero no serializar una acción
        # que incluye None. Releer enlace y factura antes de considerar éxito.
        if 'cannot marshal None' not in error.faultString:
            raise
    sale = order('sale.order', 27, 'S00027', 'sale')

targets = [(purchase, 'in_invoice', 'P00013', 103.5), (sale, 'out_invoice', 'S00027', 73.6)]
native_ids = []
for linked, move_type, origin, amount in targets:
    if len(linked['invoice_ids']) != 1:
        raise RuntimeError(f'{origin}: esperaba una única factura enlazada.')
    invoice_id = linked['invoice_ids'][0]
    row = call('account.move', 'read', [invoice_id], fields=['state', 'move_type', 'invoice_origin', 'amount_total', 'company_id', 'invoice_line_ids'])[0]
    if (invoice_id in [25, 26] or row['move_type'] != move_type or row['invoice_origin'] != origin
            or abs(row['amount_total'] - amount) > 0.001 or row['company_id'][0] != 3 or len(row['invoice_line_ids']) != 1):
        raise RuntimeError(f'Factura enlazada de {origin} no satisface tipo/origen/monto/empresa; detener.')
    native_ids.append(invoice_id)
    print(f'{origin}: factura nativa ID={invoice_id} estado={row["state"]} total={row["amount_total"]}')

for old_id, marker in [(25, 'SIM-AUTO-V-001'), (26, 'SIM-AUTO-C-001')]:
    old = call('account.move', 'read', [old_id], fields=['state', 'ref', 'company_id'])[0]
    if old['ref'] != marker or old['company_id'][0] != 3:
        raise RuntimeError(f'Borrador {old_id} no corresponde al laboratorio; detener.')
    if old['state'] == 'draft':
        try:
            call('account.move', 'button_cancel', [old_id])
        except xmlrpc.client.Fault as error:
            if 'cannot marshal None' not in error.faultString:
                raise
    state = call('account.move', 'read', [old_id], fields=['state'])[0]['state']
    print(f'Factura independiente anterior ID={old_id}: estado={state}')
    if state != 'cancel':
        raise RuntimeError(f'Borrador independiente {old_id} no cancelado; evitar duplicidad.')

for invoice_id in native_ids:
    row = call('account.move', 'read', [invoice_id], fields=['state', 'name', 'payment_state', 'invoice_date', 'date'])[0]
    if row['state'] == 'draft':
        if not row['invoice_date']:
            if not row['date']:
                raise RuntimeError(f'Factura {invoice_id} sin fecha contable; detener.')
            call('account.move', 'write', [invoice_id], {'invoice_date': row['date']})
        response = call('account.move', 'action_post', [invoice_id])
        if isinstance(response, dict):
            print(f'Factura {invoice_id}: Odoo devolvió asistente {response.get("res_model")}; verificar estado.')
    row = call('account.move', 'read', [invoice_id], fields=['state', 'name', 'payment_state', 'amount_total'])[0]
    print(f'Factura {invoice_id}: nombre={row["name"]} estado={row["state"]} pago={row["payment_state"]} total={row["amount_total"]}')
    if row['state'] != 'posted' or not row['name']:
        raise RuntimeError(f'Factura {invoice_id} no publicada; detener, no asumir pago.')

print('Órdenes y facturas nativas verificadas. Pagos pendientes: no ejecutar sin comprobar diarios y estados.')
