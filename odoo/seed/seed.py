"""Carga idempotente mínima por XML-RPC para Odoo 18; ejecutarla sólo con instancia verificada.

No crea compras, entregas ni asientos por acceso SQL: esas operaciones se deben
confirmar en interfaz según edición y configuración contable efectiva.
"""
import os
import sys
import json
import secrets
from pathlib import Path
import xmlrpc.client

url = os.environ.get('ODOO_URL', 'http://127.0.0.1:8070')
db = os.environ.get('ODOO_DB', 'audit_sim')
user = os.environ.get('ODOO_LOGIN', '')
password = os.environ.get('ODOO_PASSWORD', '')
if not user or not password:
    sys.exit('Definir ODOO_LOGIN y ODOO_PASSWORD en variables locales (no imprimirlas).')
common = xmlrpc.client.ServerProxy(url + '/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(db, user, password, {})
if not uid:
    sys.exit('Autenticación fallida; verificar base, usuario y contraseña local.')
api = xmlrpc.client.ServerProxy(url + '/xmlrpc/2/object', allow_none=True)

def call(model, method, *args, **kwargs):
    return api.execute_kw(db, uid, password, model, method, list(args), kwargs)

def upsert(model, key, value, fields):
    ids = call(model, 'search', [[key, '=', value]], limit=1)
    if ids:
        print(f'{model}: existente id={ids[0]} ({value})')
        return ids[0]
    record = call(model, 'create', fields)
    print(f'{model}: creado id={record} ({value})')
    return record

company = upsert('res.company', 'name', 'Autopartes Horizonte', {'name': 'Autopartes Horizonte'})
# El plan contable se configura y verifica por separado antes de facturar;
# try_loading devuelve None y no es serializable por XML-RPC en Odoo 18.
partners = [
    ('Elena Salcedo', 'Gerente general', False, False),
    ('Martín Varela', 'Gerente de auditoría', False, False),
    ('Lucía Montes', 'Gerente de inventario', False, False),
    ('Diego Ríos', 'Gerente de facturación', False, False),
    ('Rodamientos Boreal', 'Proveedor', True, False),
    ('Electropartes Nébula', 'Proveedor', True, False),
    ('Taller Ronda', 'Cliente', False, True),
    ('Flotas Andina', 'Cliente', False, True),
]
for name, title, supplier, customer in partners:
    upsert('res.partner', 'name', name, {'name': name, 'function': title, 'supplier_rank': int(supplier), 'customer_rank': int(customer), 'company_id': False})

products = [
    ('AH-FLT-001', 'Filtro de aceite AH-01', 18.0, 32.0),
    ('AH-BAT-002', 'Batería 60Ah AH-02', 90.0, 145.0),
    ('AH-FRE-003', 'Pastillas de freno AH-03', 38.0, 67.0),
]
for code, name, cost, price in products:
    # La selección de tipo inventariable se confirma después en interfaz: Odoo 18
    # puede exponer el campo is_storable en lugar de tipos de otras versiones.
    upsert('product.template', 'default_code', code, {
        'name': name, 'default_code': code, 'list_price': price,
        'standard_price': cost, 'sale_ok': True, 'purchase_ok': True,
        'is_storable': True,
    })

for module in ('stock', 'account'):
    installed = call('ir.module.module', 'search', [('name', '=', module), ('state', '=', 'installed')], limit=1)
    if not installed:
        sys.exit(f'Instalar y comprobar {module} antes de crear usuarios con permisos; contactos y productos ya cargados.')

def group(xmlid):
    module, name = xmlid.split('.')
    found = call('ir.model.data', 'search_read', [('module', '=', module), ('name', '=', name)], fields=['res_id'], limit=1)
    if not found:
        sys.exit(f'No existe el grupo {xmlid} en esta edición. Revisar permisos en interfaz; no asignar uno aproximado.')
    return found[0]['res_id']

internal = group('base.group_user')
inventory = group('stock.group_stock_manager')
billing = group('account.group_account_invoice')
users = [
    ('Elena Salcedo', 'elena.salcedo@horizonte.example', 'Gerente general', [internal]),
    ('Martín Varela', 'martin.varela@horizonte.example', 'Gerente de auditoría', [internal]),
    ('Lucía Montes', 'lucia.montes@horizonte.example', 'Gerente de inventario', [internal, inventory]),
    ('Diego Ríos', 'diego.rios@horizonte.example', 'Gerente de facturación', [internal, billing]),
]
secrets_file = Path(__file__).resolve().parent.parent / 'credenciales-locales.json'
local_secrets = json.loads(secrets_file.read_text(encoding='utf-8')) if secrets_file.exists() else {}
for name, login, title, groups in users:
    found = call('res.users', 'search', [('login', '=', login)], limit=1)
    if found:
        print(f'res.users: existente id={found[0]} ({login}); credencial sin cambios')
        continue
    generated = secrets.token_urlsafe(32)
    record = call('res.users', 'create', {
        'name': name, 'login': login, 'password': generated,
        'function': title, 'company_id': company,
        'company_ids': [(6, 0, [company])], 'groups_id': [(6, 0, groups)],
    })
    local_secrets[login] = generated
    print(f'res.users: creado id={record} ({login}); contraseña guardada sólo en archivo ignorado')
if local_secrets:
    secrets_file.write_text(json.dumps(local_secrets, indent=2), encoding='utf-8')
    try:
        secrets_file.chmod(0o600)
    except OSError:
        pass
print('Carga base terminada. Verificar grupos y accesos desde interfaz. Pendiente: existencias, transferencias, compras, ventas, facturas, pagos y asientos.')
