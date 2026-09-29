# Anexo 13 — Lista de Chequeo Riesgos Informáticos

**Versión diligenciada (estado documentado, no auditoría concluida)** · Fuente de estructura: Romero (2012), anexo 13.

**PROYECTO:** Simulación de auditoría SI — Autopartes Horizonte

| Área | Riesgo | Criterio de Aceptación | Sí | No | N/A | Observaciones |
| --- | --- | --- | --- | --- | --- | --- |
| Seguridad | Acceso excesivo | Acceso mínimo por función en cuentas del caso | — | X | — | H-01: Diego (facturación) tiene escritura en compra ID 13 y venta ID 27; Lucía (inventario) en venta ID 27, con límite de UI por modelo secundario. Ver docs/hallazgos-control.md. |
| Software | Integridad | Ajustes y flujos comerciales conciliables por ID | X | — | — | Ajustes 41–43; recepción 19 y entrega 20 done; facturas vinculadas 27/28 posted y paid; pagos 1/2, asientos 29/30. Conciliaciones JSON sin diferencias. |
| Documentación | Falta de evidencia | ID y captura por resultado | X | — | — | Capturas reales y lecturas de Odoo para flujo y H-01; aprobación del informe todavía pendiente. |
| Instalaciones | Seguridad física empresarial | Inspección del local productivo | — | — | X | N/A justificado: sólo laboratorio local, empresa ; no hay planta. |
| Comunicaciones | Rastro del cambio | Fechas y aprobadores por fase | — | X | — | Cambio de roles no autorizado ni implantado; no confundir con transacciones del laboratorio. |

