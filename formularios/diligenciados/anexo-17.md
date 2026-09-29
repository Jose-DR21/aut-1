# Anexo 17 — Informe de Auditoría

**Versión diligenciada (estado documentado, no auditoría concluida)** · Fuente de estructura: Romero (2012), anexo 17.

**PROYECTO:** Simulación de auditoría SI — Autopartes Horizonte

| Patrocinador | Auditor Líder |
| --- | --- |
| Elena Salcedo — gerente general | Jose Ramos — auditor líder |

| Objetivo General de la Auditoría |
| --- |
| Evaluar controles informáticos de acceso, separación de funciones, trazabilidad, integridad y conciliación entre Inventario y Facturación de Odoo; no se trata de una auditoría real. |

| Procesos Auditados | Fecha | Lugar |
| --- | --- | --- |
| Inventario y Facturación del laboratorio | 2026-09-28/29 (sesiones técnicas) | audit_sim local; sin auditoría empresarial real |

| Área | Criterio de Aceptación | Sí | No | N/A | Hallazgo | Recomendaciones |
| --- | --- | --- | --- | --- | --- | --- |
| Acceso | Acceso mínimo por proceso | — | X | — | H-01: permiso de escritura cruzado en compra ID 13 y venta ID 27, observado sin modificar documentos. | Revisar grupos y reglas sólo tras autorización de cambio; ver docs/hallazgos-control.md |
| Inventario / Facturación | Trazabilidad y conciliación con ID | X | — | — | Entrada 5 y salida 2 confirman filtro 23; facturas 27/28 y pagos 1/2 enlazados a órdenes y asientos; ver JSON de conciliación. | Conservar capturas e IDs y repetir prueba tras cualquier cambio de roles |
| Documentación | Evidencia técnica por resultado | X | — | — | Capturas Odoo y JSON disponibles; evaluación final pendiente de revisión humana. | No cerrar ni atribuir firma sin aceptación expresa |

| Elaborado | Aprobado |
| --- | --- |
| Jose Ramos — auditor líder | Informe técnico preparado; aprobación y opinión final pendientes |

