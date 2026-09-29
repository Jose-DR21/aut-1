# Pruebas de control de acceso — simulación académica

**Alcance:** base `audit_sim`, empresa 3, usuarios de prueba 8–11. Lecturas no destructivas mediante XML-RPC el 2026-09-29 UTC: grupos efectivos con `res.users.has_group`, ACL con `check_access_rights`, reglas por registro con `has_access` sobre IDs 13 (compra), 27 (venta), 28 (factura nativa) y 39 (existencia). Respuestas actuales sin secretos en `docs/pruebas-acceso-odoo.json`. **Estas pruebas de roles** no ejecutaron `write`, `create`, `button_confirm` ni pago; las confirmaciones posteriores de flujos fueron realizadas por `admin` con autorización del usuario y se describen separadamente en `docs/estado-odoo.json`.

| Usuario | Rol previsto | Compra ID 13 (escritura) | Venta ID 27 (escritura) | Factura ID 28 (escritura) | Existencia ID 39 (escritura) |
|---|---|---|---|---|---|
| Elena ID 8 | Dirección | No | No | No | No |
| Martín ID 9 | Auditoría | No | No | No | No |
| Lucía ID 10 | Inventario | No | **Sí** | No | Sí |
| Diego ID 11 | Facturación | **Sí** | **Sí** | Sí | No |

## H-01 — Segregación incompleta en cuentas del laboratorio

**Hecho reproducible:** Diego (facturación) posee ACL `write=true` y `has_access('write')=true` para compra `P00013` y venta `S00027`, incluso tras confirmarlas como admin. En su sesión autenticada (UID 11), la pantalla histórica de `P00013` mostraba **Confirm Order**; captura `evidencias/odoo/diego-acceso-compra.png`. **Diego no pulsó ese botón**; el admin confirmó luego la compra autorizada. Lucía (inventario) posee `has_access('write')=true` en la venta `S00027`, pero su interfaz de Cotizaciones mostró un **Access Error** por el modelo secundario `sale.order.option`; captura `evidencias/odoo/lucia-acceso-venta.png`. Por ello **no** afirmar que Lucía puede completar el flujo de ventas desde UI, aunque el permiso sobre `sale.order` sea verdadero.

Ni Diego ni Lucía son miembros efectivos de `sale.group_sale_salesman` o `purchase.group_purchase_user` según `has_group`; las ACL observadas derivan de otras asignaciones/reglas en esta instalación. No deducir de ello un cambio de grupos sin revisar los permisos implícitos y el modelo secundario.

**Criterio del caso:** acceso mínimo por proceso y separación entre Inventario y Facturación. **Riesgo:** las cuentas de laboratorio podrían modificar documentos ajenos a su función. **Límite:** no hay prueba de cambio indebido, ni comparación con políticas reales de una empresa (los roles y la empresa son parte de la simulación). No se asigna opinión sobre un sistema productivo.

**Recomendación propuesta, no autorizada:** revisar grupos implícitos y ACL/reglas por modelo y registro, incluidos `sale.order`, `purchase.order` y `sale.order.option`, en una copia respaldada; definir matriz de funciones esperadas, retirar sólo los permisos sobrantes tras aprobación y repetir pruebas positivas/negativas. No cambiar grupos en esta base sin registrar solicitud, autorización, preparación, prueba, implantación y cierre del anexo 14.

## Pendiente para convertirlo en informe final

Validación humana del criterio de segregación y alcance; prueba del flujo funcional tras ajuste de roles autorizado; capturas detalladas de grupos y resultado antes/después; firma/aprobación de patrocinadora **no presumida**. Los documentos comerciales ya fueron confirmados y pagados por admin en el laboratorio **fuera de estas pruebas de roles**; eso no resuelve H-01 ni representa una aprobación institucional.
