"""Replace the initial admin password on the new, otherwise empty audit_sim database.

Uses the random password already stored in the git-ignored local credentials file.
No password is printed or supplied as a command-line argument.
"""
import json
from pathlib import Path
import sys
import xmlrpc.client

file = Path(__file__).parent / 'credenciales-locales.json'
if not file.exists():
    sys.exit('Falta archivo local de credenciales creado por setup_native.py.')
secret = json.loads(file.read_text(encoding='utf-8'))['admin']
url, db = 'http://127.0.0.1:8070', 'audit_sim'
common = xmlrpc.client.ServerProxy(url + '/xmlrpc/2/common', allow_none=True)
if common.authenticate(db, 'admin', secret, {}):
    print('La contraseña aleatoria ya está activa.')
    sys.exit(0)
uid = common.authenticate(db, 'admin', 'admin', {})
if not uid:
    sys.exit('El usuario admin no autentica con la clave inicial; no se modifica.')
api = xmlrpc.client.ServerProxy(url + '/xmlrpc/2/object', allow_none=True)
api.execute_kw(db, uid, 'admin', 'res.users', 'write', [[uid], {'password': secret}])
verified = common.authenticate(db, 'admin', secret, {})
if verified != uid:
    sys.exit('No se verificó el cambio de contraseña: revisar antes de continuar.')
print(f'Contraseña inicial cambiada y verificada para admin ID={uid}.')
