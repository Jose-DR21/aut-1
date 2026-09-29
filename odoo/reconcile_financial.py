"""Verifica vínculos orden-factura-pago y saldos de la simulación; sólo lecturas."""
import datetime
import json
from pathlib import Path
import xmlrpc.client

password = json.loads((Path(__file__).parent / 'credenciales-locales.json').read_text(encoding='utf-8'))['admin']
url, db = 'http://127.0.0.1:8070/xmlrpc/2/', 'audit_sim'
uid = xmlrpc.client.ServerProxy(url + 'common').authenticate(db, 'admin', password, {})
if not uid:
    raise RuntimeError('No autentica admin.')
api = xmlrpc.client.ServerProxy(url + 'object', allow_none=True)

def record(model, record_id, fields):
    rows = api.execute_kw(db, uid, password, model, 'read', [[record_id]], {'fields': fields})
    if len(rows) != 1:
        raise RuntimeError(f'Falta {model} ID {record_id}')
    return rows[0]

checks = []
for order_model, order_id, order_name, picking_id, invoice_id, payment_id, expected_amount, invoice_type in [
    ('purchase.order', 13, 'P00013', 19, 27, 1, 103.5, 'in_invoice'),
    ('sale.order', 27, 'S00027', 20, 28, 2, 73.6, 'out_invoice'),
]:
    order = record(order_model, order_id, ['name', 'state', 'picking_ids', 'invoice_ids', 'invoice_status', 'amount_total'])
    picking = record('stock.picking', picking_id, ['name', 'state', 'origin', 'move_ids'])
    invoice = record('account.move', invoice_id, ['name', 'state', 'move_type', 'invoice_origin', 'amount_total', 'amount_residual', 'payment_state'])
    payment = record('account.payment', payment_id, ['name', 'state', 'amount', 'journal_id', 'move_id', 'reconciled_invoice_ids', 'reconciled_bill_ids'])
    entry = record('account.move', payment['move_id'][0], ['state', 'journal_id', 'name'])
    linked = payment['reconciled_bill_ids'] if invoice_type == 'in_invoice' else payment['reconciled_invoice_ids']
    valid = (order['name'] == order_name and order['state'] == ('purchase' if invoice_type == 'in_invoice' else 'sale')
             and picking_id in order['picking_ids'] and invoice_id in order['invoice_ids'] and order['invoice_status'] == 'invoiced'
             and picking['state'] == 'done' and picking['origin'] == order_name
             and invoice['state'] == 'posted' and invoice['move_type'] == invoice_type and invoice['invoice_origin'] == order_name
             and invoice['payment_state'] == 'paid' and abs(invoice['amount_residual']) < 0.001
             and abs(invoice['amount_total'] - expected_amount) < 0.001
             and payment['state'] == 'paid' and abs(payment['amount'] - expected_amount) < 0.001
             and payment['journal_id'][0] == 14 and invoice_id in linked and entry['state'] == 'posted' and entry['journal_id'][0] == 14)
    checks.append({'orden_id': order_id, 'orden': order_name, 'transferencia_id': picking_id, 'transferencia': picking['name'],
                   'factura_id': invoice_id, 'factura': invoice['name'], 'factura_estado': invoice['state'],
                   'factura_saldo': invoice['amount_residual'], 'factura_pago_estado': invoice['payment_state'],
                   'pago_id': payment_id, 'pago': payment['name'], 'pago_estado': payment['state'],
                   'asiento_pago_id': payment['move_id'][0], 'asiento_pago_estado': entry['state'],
                   'importe': expected_amount, 'coincide': bool(valid)})

old = [record('account.move', i, ['state', 'ref']) for i in [25, 26]]
result = {'tipo': 'conciliacion_documental_laboratorio',
          'capturado_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
          'empresa_id': 3, 'flujos': checks, 'borradores_independientes_cancelados': [r['id'] for r in old if r['state'] == 'cancel'],
          'todos_coinciden': all(row['coincide'] for row in checks) and len([r for r in old if r['state'] == 'cancel']) == 2,
          'limite': 'La confirmación en Odoo es de laboratorio; no acredita dinero real ni aceptación humana del informe.'}
file = Path('docs/conciliacion-financiera.json')
file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print('Vínculos orden-transferencia-factura-pago-asiento verificados:', result['todos_coinciden'])
if not result['todos_coinciden']:
    raise RuntimeError('Discrepancia en flujos; investigar antes de declarar conciliación.')
