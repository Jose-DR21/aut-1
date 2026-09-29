# Anexo 19 — Relación de Lecciones Aprendidas

**Versión diligenciada (estado documentado, no auditoría concluida)** · Fuente de estructura: Romero (2012), anexo 19.

**PROYECTO:** Simulación de auditoría SI — Autopartes Horizonte

| Código de Lección Aprendida | Entregable afectado | Descripción y Causa del problema | Acción Correctiva | Resultado obtenido | Lección Aprendida |
| --- | --- | --- | --- | --- | --- |
| LA-01 | Entorno Odoo | Docker y WSL 2 no disponibles; PostgreSQL 18.6 existente | Usar instalación nativa y corregir locale sólo en base nueva vacía | Odoo 18 y módulos verificados; base preservada | Comprobar locale y filestore antes de crear datos |
| LA-02 | Facturación | Facturas independientes inicialmente sin vínculo con órdenes | Crear facturas nativas tras recibir/entregar; cancelar sólo borradores independientes 25/26 | Facturas 27/28 vinculadas y pagadas en laboratorio | No asumir trazabilidad por importe coincidente; exigir ID y origen |
| LA-03 | Control de acceso | Grupos previstos no garantizan mínimo privilegio | Probar ACL y acceso por registro sin cambiar datos | H-01 documentado; cambio de roles pendiente | Revisar grupos implícitos y modelos secundarios antes de implantar |

| Elaborado | Aprobado |
| --- | --- |
| Jose Ramos — auditor líder | Pendiente: Elena Salcedo — gerente general / coordinación |

