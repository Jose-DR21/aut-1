# Anexo 11 — Plan de Contingencias

**Versión diligenciada (estado documentado, no auditoría concluida)** · Fuente de estructura: Romero (2012), anexo 11.

**PROYECTO:** Simulación de auditoría SI — Autopartes Horizonte

| Riesgo | Causas | Consecuencias | Alternativa1 | Alternativa2 | Alternativa3 | Responsable |
| --- | --- | --- | --- | --- | --- | --- |
| Indisponibilidad futura de Odoo | Servicio nativo caído o puerto ocupado | Interrupción de nuevas pruebas; evidencias ya capturadas permanecen | Comprobar servicio nativo y puertos | Restaurar base y filestore desde respaldo validado si procede | Reprogramar; declarar pendiente lo no probado | Jose Ramos — auditor líder |
| Pérdida de datos de laboratorio | Filestore o base dañados | No reproducibilidad | Respaldo de base y filestore | Restaurar en instancia aislada y comprobar IDs | Conservar matriz sin evidencia nueva hasta recuperar | Jose Ramos — auditor líder |
| Cambio de rol defectuoso | Permisos mal ajustados | Usuarios bloqueados | Probar cuenta no productiva | Revertir mediante copia propia verificada | Suspender implantación y notificar patrocinadora | Elena Salcedo — gerente general |

