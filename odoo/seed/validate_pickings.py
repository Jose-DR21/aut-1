"""Valida recepción y entrega específicas de audit_sim, con lectura tras cada paso.

Requiere respaldo validado y órdenes 13/27 confirmadas; no ejecuta asistentes
que Odoo devuelva implícitamente ni interpreta HTTP 200 como transferencia hecha.
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

for name, origin, qty, src, dest in [
    ('AH/IN/00001', 'P00013', 5, 4, 39),
    ('AH/OUT/00001', 'S00027', 2, 39, 5),
]:
    ids = call('stock.picking', 'search', [('name', '=', name), ('company_id', '=', 3), ('origin', '=', origin)])
    if len(ids) != 1:
        raise RuntimeError(f'{name}: transferencia de laboratorio no única.')
    fields = ['state', 'move_ids', 'location_id', 'location_dest_id']
    row = call('stock.picking', 'read', ids, fields=fields)[0]
    if len(row['move_ids']) != 1 or row['location_id'][0] != src or row['location_dest_id'][0] != dest:
        raise RuntimeError(f'{name}: ubicaciones o movimientos distintos a los esperados.')
    move = call('stock.move', 'read', row['move_ids'], fields=['product_id', 'product_uom_qty', 'quantity', 'state'])[0]
    if move['product_id'][0] != 60 or move['product_uom_qty'] != qty or move['quantity'] != qty:
        raise RuntimeError(f'{name}: cantidad o producto no coinciden; no validar.')
    if row['state'] == 'done':
        print(f'{name}: ya done; no repetir.')
        continue
    if row['state'] != 'assigned':
        raise RuntimeError(f'{name}: estado no previsto {row["state"]}.')
    response = call('stock.picking', 'button_validate', ids)
    after = call('stock.picking', 'read', ids, fields=['state', 'date_done', 'move_ids'])[0]
    move_after = call('stock.move', 'read', after['move_ids'], fields=['state', 'quantity'])[0]
    print(f'{name}: picking_id={ids[0]} respuesta={str(response)[:90]} estado={after["state"]} movimiento={move_after["state"]} cantidad={move_after["quantity"]}')
    if after['state'] != 'done' or move_after['state'] != 'done' or move_after['quantity'] != qty:
        raise RuntimeError(f'{name}: wizard o fallo; detener y revisar respuesta, no afirmar recepción/entrega.')

quants = call('stock.quant', 'search_read', [('product_id', '=', 60), ('location_id', '=', 39)], fields=['quantity'])
total = sum(row['quantity'] for row in quants)
print(f'Existencia filtro AH-FLT-001 en AH/Stock tras +5 y -2: {total}')
if total != 23:
    raise RuntimeError('La existencia final no concilia con 20+5-2.')
