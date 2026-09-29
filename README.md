# Horizonte · simulación académica de auditoría informática Odoo

**No es una auditoría real.** Empresa, personas y operaciones son ficticias. Documentación basada en Sara María Romero, «Una metodología para la gestión de proyectos de auditoría informática bajo el enfoque PMI», *Rev. Tecnol.* 11(1), 2012, pp. 9–23, tabla I y anexos 1–20. No se redistribuye el PDF.

## Estado comprobado al 2026-09-29 (UTC)

- Windows: PostgreSQL 18.6 **operativo y autenticado** en `127.0.0.1:5432` (rol `postgres`), Docker y WSL 2 **no disponibles**; Node.js 24.20.0 y npm 11.19.0 disponibles; ~158 GB libres en C:; navegador disponible mediante el entorno de trabajo.
- Odoo Community 18.0-20260928 funciona en `audit_sim` con Inventario, Contabilidad/Facturación, Compras y Ventas instalados; instancia nativa en 8069 e instancia de laboratorio con filestore local en 8070. Se creó la empresa ID 3, almacén ID 3, tres productos almacenables, tres ajustes de inventario y cuatro usuarios de prueba. `docs/estado-odoo.json` contiene la última lectura sin secretos.
- Compra ID 13 y venta ID 27 confirmadas; recepción ID 19 y entrega ID 20 en `done`. Las facturas nativas ID 27/28 están `posted` y `paid`, con pagos ID 1/2 y asientos de pago ID 29/30 publicados. Los borradores independientes 25/26 se cancelaron para evitar duplicidad. El filtro quedó en 23 = 20 + 5 − 2; los vínculos y saldos concilian en `docs/conciliacion-inventario.json` y `docs/conciliacion-financiera.json`. Son movimientos **sólo de laboratorio**, no dinero real ni auditoría aprobada. H-01 de accesos cruzados sigue pendiente de revisión y corrección autorizada; ver `docs/hallazgos-control.md` y `docs/RELEVO.md`.
- Responsables del caso: Elena Salcedo (gerente general y patrocinadora/coordinadora), Jose Ramos (auditor líder), Lucía Montes (gerente de inventario) y Diego Ríos (gerente de facturación). Las cuentas técnicas observadas en Odoo son Elena ID 8, Martín Varela ID 9, Lucía ID 10 y Diego ID 11; la cuenta ID 9 conserva su nombre histórico y **no se atribuye a Jose Ramos**. Las pruebas no destructivas de permisos por modelo y registro detectaron H-01; falta validación humana y retest tras un eventual cambio autorizado.

## Requisitos y versiones

**Ruta utilizada en este equipo:** instalador oficial de Odoo 18 Community para Windows más PostgreSQL 18.6 ya operativo; ver `odoo/INSTALACION-WINDOWS.md`. **Ruta alternativa no ejecutada:** Docker Desktop con Compose v2 y Linux containers, imágenes `odoo:18.0` y `postgres:16.9` (fijar digest tras validar). Node.js 20+; npm 10+; navegador. Odoo en 8069/8070 y Next.js en 3000 o 3001 según disponibilidad. Nunca guardar contraseñas en Git.

## Sitio y formularios

```powershell
npm install
npm run forms
npm run verify
npm run build
npm run dev
```

Abrir el puerto de Next.js configurado (por defecto `http://127.0.0.1:3000`). Los formularios están en `formularios/vacios/anexo-XX.md` y `formularios/diligenciados/anexo-XX.md`: **18 + 18 Markdown editables** en el proyecto. `npm run forms` regenera los archivos desde `scripts/forms.mjs` (editar la fuente para cambios permanentes). El sitio muestra formularios individuales y los 18 juntos en `/formularios`, sin descarga Markdown; `/galeria` permite recorrer las capturas dentro de la aplicación. Las figuras editables están en `diagramas/` como Mermaid. Cronograma libre en `docs/cronograma.csv`.

## Preparar Odoo: instalación nativa o Docker

**Sin WSL:** la instalación nativa ya se realizó en este laboratorio. `odoo/INSTALACION-WINDOWS.md` describe el incidente de locale y los dos filestores; no recrear la base poblada.

**Con Docker disponible posteriormente:** ejecutar:

```powershell
Copy-Item .env.example .env
# editar .env localmente con DB_PASSWORD aleatoria fuerte; nunca subirla
docker compose --env-file .env -f odoo/compose.yaml up -d
docker compose --env-file .env -f odoo/compose.yaml ps
```

Abrir `http://127.0.0.1:8069`, crear la base `audit_sim` y cambiar inmediatamente credenciales iniciales. Guardar en `.env` local `ODOO_LOGIN`, `ODOO_PASSWORD` y `ODOO_DB`; no publicar master password. Instalar en **Aplicaciones** Inventario (`stock`) y Facturación/Contabilidad (`account`) y verificar visualmente qué menús y funciones ofrece exactamente la edición Community. **No presuponer contabilidad completa.** Crear la empresa de laboratorio o seleccionar la creada por la carga. Evitar operar cualquier instancia productiva.

### Carga base

Con Python 3 local (o el Python provisto por el instalador Odoo), en PowerShell:

```powershell
$env:ODOO_DB='audit_sim'
$env:ODOO_LOGIN='<usuario local>'
$env:ODOO_PASSWORD='<contraseña local>'
python odoo/seed/seed.py
```

El script idempotente creó empresa, contactos, productos y usuarios. Generó contraseñas aleatorias en `odoo/credenciales-locales.json` (ignorado por Git); no las muestra ni ofrece edición en la landing. Se verificó tipo *almacenable*; plan contable y almacén se configuraron mediante `odoo/prepare_company.py`. Antes de confirmar transacciones se guardó un respaldo local de base y filestore en `odoo/backups/` (ignorado). Los scripts `odoo/seed/confirm_orders.py`, `validate_pickings.py`, `invoice_orders.py` y `register_payments.py` aplicaron pasos nativos con lectura posterior. **No reejecutar a ciegas:** cada paso valida IDs y estados. Para recargar en otro laboratorio usar una copia autorizada de base y filestore; no reiniciar esta base.

## Estructura y aceptación

| Ruta | Contenido |
|---|---|
| `odoo/compose.yaml`, `odoo/INSTALACION-WINDOWS.md`, `odoo/seed/` | Dos rutas de instalación y carga base reproducible |
| `docs/00-correspondencia.md`, `docs/EDT.md`, `docs/cronograma.csv` | Método, EDT y línea base futura |
| `formularios/vacios/`, `formularios/diligenciados/` | 36 formularios Markdown editables |
| `diagramas/` | Anexos 1 y 8 editables, atribuidos |
| `docs/trazabilidad.csv`, `docs/guia-evidencia.md` | Trazabilidad preliminar y protocolo de captura |
| `evidencias/odoo/`, `evidencias/formularios/` | Capturas reales de Odoo y 18 capturas reales de formularios diligenciados |
| `app/`, `scripts/` | Landing Next.js y verificadores |

**Criterio estricto:** ninguna fila «observada en Odoo» sin pantalla, ID y captura existente. `npm run verify` controla archivos de formularios y rutas declaradas; no sustituye prueba manual de instalación, datos, legibilidad ni reconciliación. La etapa de cierre es un **borrador no aprobado** hasta que se revise H-01, cualquier remediación autorizada y los entregables. `docs/guia-evidencia.md` detalla evidencias y límites.

## Qué falta para completar la solicitud original

Instalación, datos, dos flujos comerciales y conciliaciones técnicas completados en el laboratorio. Faltan decidir y autorizar formalmente la corrección de H-01, probar permisos después del cambio, documentar comunicaciones y tiempos reales de acuerdo con el cronograma, y realizar revisión/aceptación final. `docs/RELEVO.md` deja el estado para continuar. Ninguna firma ni aprobación institucional se presume.
