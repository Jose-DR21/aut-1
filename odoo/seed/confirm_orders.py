"""Confirma SOLO las dos órdenes de laboratorio existentes; requiere respaldo previo.

No interpreta un resultado de API como prueba: relee estado y pickings. No toca
facturas creadas aparte ni otros pedidos, y no crea duplicados al reejecutar.
"""
import json
from pathlib import Path
import xmlrpc.client

password = json.loads((Path(__file__).resolve().parent.parent / 'credenciales-locales.json').read_text(encoding='utf-8'))['admin']
url, db = 'http://127.0.0.1:8070/xmlrpc/2/', 'audit_sim'
uid = xmlrpc.client.ServerProxy(url + 'common').authenticate(db, 'admin', password, {})
if not uid:
    raise RuntimeError('No autentica admin; detener.')
api = xmlrpc.client.ServerProxy(url + 'object', allow_none=True)

def call(model, method, *args, **kw):
    return api.execute_kw(db, uid, password, model, method, list(args), kw)

for model, number, marker, operation, expected in [
    ('purchase.order', 'P00013', 'SIM-AUTO-PO-001', 'button_confirm', 'purchase'),
    ('sale.order', 'S00027', 'SIM-AUTO-SO-001', 'action_confirm', 'sale'),
]:
    ids = call(model, 'search', [('name', '=', number), ('company_id', '=', 3)])
    if len(ids) != 1:
        raise RuntimeError(f'{model} {number}: esperaba una única orden en empresa 3.')
    fields = ['name', 'state', 'company_id', 'order_line', 'picking_ids', 'origin' if model == 'purchase.order' else 'client_order_ref']
    before = call(model, 'read', ids, fields=fields)[0]
    if before[fields[-1]] != marker or len(before['order_line']) != 1:
        raise RuntimeError(f'{number}: identificador o líneas no corresponden al laboratorio.')
    if before['state'] in (expected, 'done'):
        print(f'{number}: ya en {before["state"]}; no repetir confirmación.')
    elif before['state'] not in ('draft', 'sent'):
        raise RuntimeError(f'{number}: estado no previsto {before["state"]}.')
    else:
        call(model, operation, ids)
    after = call(model, 'read', ids, fields=fields)[0]
    print(f'{number}: estado={after["state"]}, picking_ids={after["picking_ids"]}')
    if after['state'] != expected or not after['picking_ids']:
        raise RuntimeError(f'{number}: no se verificó confirmación y transferencia; detener.')
