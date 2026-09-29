"""Registra pagos de dos facturas nativas publicadas del laboratorio.

La conciliación banco-extracto no se presume: Odoo puede devolver in_payment.
Verifica diarios, facturas y montos; nunca paga los borradores cancelados.
"""
import json
from pathlib import Path
import xmlrpc.client

password = json.loads((Path(__file__).resolve().parent.parent / 'credenciales-locales.json').read_text(encoding='utf-8'))['admin']
db, url = 'audit_sim', 'http://127.0.0.1:8070/xmlrpc/2/'
uid = xmlrpc.client.ServerProxy(url + 'common').authenticate(db, 'admin', password, {})
if not uid:
    raise RuntimeError('No autentica admin.')
api = xmlrpc.client.ServerProxy(url + 'object', allow_none=True)

def call(model, method, *args, **kwargs):
    return api.execute_kw(db, uid, password, model, method, list(args), kwargs)

journal = call('account.journal', 'read', [14], fields=['company_id', 'type', 'inbound_payment_method_line_ids', 'outbound_payment_method_line_ids'])[0]
if journal['company_id'][0] != 3 or journal['type'] != 'bank' or 5 not in journal['inbound_payment_method_line_ids'] or 6 not in journal['outbound_payment_method_line_ids']:
    raise RuntimeError('Diario Banco no coincide con empresa/métodos; no pagar.')

for invoice_id, move_type, amount, method_id in [(27, 'in_invoice', 103.5, 6), (28, 'out_invoice', 73.6, 5)]:
    fields = ['state', 'move_type', 'company_id', 'amount_total', 'amount_residual', 'payment_state', 'invoice_payments_widget']
    row = call('account.move', 'read', [invoice_id], fields=fields)[0]
    if row['company_id'][0] != 3 or row['move_type'] != move_type or row['state'] != 'posted' or abs(row['amount_total'] - amount) > 0.001:
        raise RuntimeError(f'Factura {invoice_id} fuera de contexto o no publicada.')
    if row['amount_residual'] == 0:
        print(f'Factura {invoice_id}: saldo 0, estado {row["payment_state"]}; no duplicar pago.')
        continue
    if abs(row['amount_residual'] - amount) > 0.001:
        raise RuntimeError(f'Factura {invoice_id} parcialmente pagada; intervención manual requerida.')
    context = {'active_model': 'account.move', 'active_ids': [invoice_id], 'active_id': invoice_id, 'allowed_company_ids': [3]}
    wizard = call('account.payment.register', 'create', {'journal_id': 14, 'payment_method_line_id': method_id}, context=context)
    data = call('account.payment.register', 'read', [wizard], fields=['amount', 'company_id', 'journal_id', 'payment_type', 'payment_method_line_id', 'line_ids'])[0]
    expected_type = 'outbound' if move_type == 'in_invoice' else 'inbound'
    if (data['company_id'][0] != 3 or data['journal_id'][0] != 14 or data['payment_method_line_id'][0] != method_id
            or data['payment_type'] != expected_type or abs(data['amount'] - amount) > 0.001 or len(data['line_ids']) != 1):
        raise RuntimeError(f'Wizard factura {invoice_id}: importe/empresa/método no coinciden. No ejecutar.')
    response = call('account.payment.register', 'action_create_payments', [wizard], context={**context, 'dont_redirect_to_payments': True})
    after = call('account.move', 'read', [invoice_id], fields=['amount_residual', 'payment_state', 'invoice_payments_widget'])[0]
    print(f'Factura {invoice_id}: respuesta={response}, saldo={after["amount_residual"]}, payment_state={after["payment_state"]}')
    if abs(after['amount_residual']) > 0.001:
        raise RuntimeError(f'Factura {invoice_id}: saldo no se concilió con registro de pago; detener.')

print('Pagos registrados y saldos comprobados; comprobar asientos y estado bancario antes de declarar pago final.')
