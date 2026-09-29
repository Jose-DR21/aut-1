"""Configura una empresa de laboratorio ya creada mediante `odoo-bin shell`.

Odoo 18 devuelve None al cargar plan contable, por lo que XML-RPC no sirve para
este método. Sólo actúa sobre Autopartes Horizonte y nunca reinicializa un plan.
"""
company = env['res.company'].search([('name', '=', 'Autopartes Horizonte')], limit=1)
if not company or company.id != 3:
    raise RuntimeError('Empresa de laboratorio no encontrada con ID esperado; detener.')

warehouse = env['stock.warehouse'].search([('company_id', '=', company.id)], limit=1)
if not warehouse:
    warehouse = env['stock.warehouse'].create({
        'name': 'Almacén Horizonte', 'code': 'AH', 'company_id': company.id,
    })
    print(f'Almacén creado: ID={warehouse.id}, ubicación={warehouse.lot_stock_id.id}')
else:
    print(f'Almacén ya existente: ID={warehouse.id}, ubicación={warehouse.lot_stock_id.id}')

if not company.chart_template:
    env['account.chart.template'].try_loading('generic_coa', company)
    print(f'Plan contable genérico cargado en empresa ID={company.id}')
else:
    print(f'Plan contable ya configurado: {company.chart_template}')

if not company.chart_template or not env['account.journal'].search_count([('company_id', '=', company.id)]):
    raise RuntimeError('Plan/diarios no verificables; no confirmar cambios.')
env.cr.commit()
print('Configuración confirmada: empresa, almacén y diarios contables.')
