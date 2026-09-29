# Anexo 4 — Definición del Alcance de la Auditoría

**Versión diligenciada (estado documentado, no auditoría concluida)** · Fuente de estructura: Romero (2012), anexo 4.

**PROYECTO:** Simulación de auditoría SI — Autopartes Horizonte

| Campo | Valor |
| --- | --- |
| Fecha | 2026-10-09 (plan) |
| Nombre de la Auditoría | Simulación de auditoría SI — Autopartes Horizonte |
| Objetivo General de la Auditoría | Evaluar controles informáticos de acceso, separación de funciones, trazabilidad, integridad y conciliación entre Inventario y Facturación de Odoo; no se trata de una auditoría real. |

| Entregable | Descripción | Criterios de aceptación |
| --- | --- | --- |
| Entorno y datos | Instalación nativa, alternativa Compose, instrucciones y registros del caso | Odoo inicia; módulos verificados en interfaz; registros con ID y captura |
| Evidencia y trazabilidad | Capturas legibles y matriz por campo | Cada afirmación observada remite a ID y archivo existente |
| Control y cierre | Anexos 9–20 y conclusiones | No aprobar ni cerrar sin pruebas y criterios observados |

| Nombre del riesgo | Causas de Riesgo | Plan de mitigación |
| --- | --- | --- |
| Indisponibilidad de Odoo | Ruta Docker ausente; se usó instalación nativa | Esperar habilitación; documentar bloqueo; reprogramar ejecución |
| Privilegios excesivos | Accesos cruzados H-01 comprobados; cambio pendiente | Evaluar usuarios de prueba y mínimo privilegio antes del cambio |
| Descuadre existencias/facturación | Documentos sin vínculo o fechas distintas (hipótesis) | Conciliar por ID y registrar limitaciones de Community |

