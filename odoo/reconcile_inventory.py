"""Concilia quants con ajustes y transferencias reales en AH/Stock; sólo lecturas."""
import datetime
import json
from pathlib import Path
import xmlrpc.client

creds = json.loads((Path(__file__).parent / 'credenciales-locales.json').read_text(encoding='utf-8'))
db = 'audit_sim'
url = 'http://127.0.0.1:8070/xmlrpc/2/'
uid = xmlrpc.client.ServerProxy(url + 'common').authenticate(db, 'admin', creds['admin'], {})
if not uid:
    raise RuntimeError('No autentica admin; no conciliar.')
api = xmlrpc.client.ServerProxy(url + 'object', allow_none=True)

def read(model, domain, fields):
    return api.execute_kw(db, uid, creds['admin'], model, 'search_read', [domain], {'fields': fields})

codes = {'AH-FLT-001': 60, 'AH-BAT-002': 61, 'AH-FRE-003': 62}
quants = read('stock.quant', [('location_id', '=', 39), ('product_id', 'in', list(codes.values()))], ['product_id', 'quantity', 'location_id'])
moves = read('stock.move', [('company_id', '=', 3), ('product_id', 'in', list(codes.values()))],
             ['product_id', 'quantity', 'state', 'location_id', 'location_dest_id', 'reference'])
result = {'tipo': 'conciliacion_ajustes_y_transferencias_de_laboratorio',
          'capturado_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
          'empresa_id': 3, 'ubicacion_id': 39, 'lineas': []}
for code, product_id in codes.items():
    product_quants = [q for q in quants if q['product_id'][0] == product_id]
    product_moves = [m for m in moves if m['product_id'][0] == product_id]
    actual = sum(q['quantity'] for q in product_quants)
    signed = sum((m['quantity'] if m['location_dest_id'][0] == 39 else -m['quantity'] if m['location_id'][0] == 39 else 0)
                 for m in product_moves if m['state'] == 'done')
    line = {'codigo': code, 'producto_id': product_id, 'quant_ids': [q['id'] for q in product_quants],
            'movimientos': [{'id': m['id'], 'cantidad': m['quantity'], 'estado': m['state'],
                             'origen_ubicacion': m['location_id'][0], 'destino_ubicacion': m['location_dest_id'][0]}
                            for m in product_moves],
            'cantidad_quant': actual, 'neto_movimientos_done': signed, 'coinciden': abs(actual - signed) < 1e-6}
    result['lineas'].append(line)
result['todos_coinciden'] = len(result['lineas']) == 3 and all(line['coinciden'] and line['movimientos'] for line in result['lineas'])
filter_row = next(line for line in result['lineas'] if line['codigo'] == 'AH-FLT-001')
result['flujo_filtro_verificado'] = (filter_row['cantidad_quant'] == 23 and
                                    {m['id'] for m in filter_row['movimientos']} == {41, 44, 45} and
                                    all(m['estado'] == 'done' for m in filter_row['movimientos']))
result['todos_coinciden'] = result['todos_coinciden'] and result['flujo_filtro_verificado']
file = Path('docs/conciliacion-inventario.json')
file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print('Conciliación de laboratorio:', result['todos_coinciden'], [(r['codigo'], r['cantidad_quant'], [m['id'] for m in r['movimientos']]) for r in result['lineas']])
if not result['todos_coinciden']:
    raise RuntimeError('Alguna cantidad no coincide; investigar antes de afirmarlo.')
