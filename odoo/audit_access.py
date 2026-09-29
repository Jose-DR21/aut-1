"""Pruebas NO destructivas de acceso en la base de laboratorio.

La respuesta ACL no demuestra permiso por registro; se añade lectura concreta
de documentos de empresa 3. No modifica datos ni imprime contraseñas.
"""
import datetime
import json
from pathlib import Path
import xmlrpc.client

db = 'audit_sim'
url = 'http://127.0.0.1:8070/xmlrpc/2/'
secrets = json.loads((Path(__file__).parent / 'credenciales-locales.json').read_text(encoding='utf-8'))
common = xmlrpc.client.ServerProxy(url + 'common', allow_none=True)
api = xmlrpc.client.ServerProxy(url + 'object', allow_none=True)
models = {
    'stock.quant': 39,
    'product.template': 49,
    'purchase.order': 13,
    'sale.order': 27,
    'account.move': 28,
}
groups = ['base.group_user', 'stock.group_stock_user', 'stock.group_stock_manager',
          'account.group_account_invoice', 'account.group_account_manager',
          'sale.group_sale_salesman', 'sale.group_sale_manager',
          'purchase.group_purchase_user', 'purchase.group_purchase_manager']
logins = ['elena.salcedo@horizonte.example', 'martin.varela@horizonte.example',
          'lucia.montes@horizonte.example', 'diego.rios@horizonte.example']

def execute(uid, pwd, model, method, *args, **kwargs):
    return api.execute_kw(db, uid, pwd, model, method, list(args), kwargs)

def attempt(fn):
    try:
        value = fn()
        return {'ok': True, 'valor': value}
    except xmlrpc.client.Fault as error:
        # No guardar tracebacks extensos ni credenciales potencialmente reflejadas.
        text = error.faultString
        code = 'AccessError' if 'AccessError' in text else 'MissingError' if 'MissingError' in text else 'Otro fallo RPC'
        return {'ok': False, 'tipo': code}

result = {'tipo': 'prueba_acceso_no_destructiva',
          'capturado_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
          'base': db, 'empresa_id': 3, 'documentos': models, 'usuarios': []}
for login in logins:
    pwd = secrets[login]
    uid = common.authenticate(db, login, pwd, {})
    if not uid:
        raise RuntimeError(f'Usuario no autentica: {login}; no asumir resultados')
    entry = {'login': login, 'uid': uid, 'grupos': {}, 'modelos': {}}
    for group in groups:
        entry['grupos'][group] = attempt(lambda g=group: execute(uid, pwd, 'res.users', 'has_group', [uid], g))
    for model, record_id in models.items():
        rights = {operation: attempt(lambda op=operation: execute(uid, pwd, model, 'check_access_rights', op, raise_exception=False))
                  for operation in ['read', 'create', 'write', 'unlink']}
        record = attempt(lambda: execute(uid, pwd, model, 'read', [record_id], fields=['id']))
        if record['ok']:
            record['valor'] = [row['id'] for row in record['valor']]
        record_access = {operation: attempt(lambda op=operation: execute(uid, pwd, model, 'has_access', [record_id], op))
                         for operation in ['read', 'write', 'unlink']}
        entry['modelos'][model] = {'acl': rights, 'lectura_registro': record, 'acceso_registro': record_access}
    result['usuarios'].append(entry)

file = Path('docs/pruebas-acceso-odoo.json')
file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
for entry in result['usuarios']:
    print(entry['login'], 'uid=', entry['uid'], 'inventario_admin=', entry['grupos']['stock.group_stock_manager'].get('valor'),
          'facturacion=', entry['grupos']['account.group_account_invoice'].get('valor'),
          'factura_legible=', entry['modelos']['account.move']['lectura_registro']['ok'])
print('Salida sin secretos:', file)
