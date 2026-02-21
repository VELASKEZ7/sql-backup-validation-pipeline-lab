# SQL Backup Validation Pipeline Lab

Pipeline local para validar scripts SQL y simular respaldo antes de ejecutar cambios.

## Que hace
- Revisa reglas basicas de seguridad SQL
- Bloquea patrones de alto riesgo (`DROP DATABASE`, `TRUNCATE`, `DELETE` sin `WHERE`)
- Marca warning cuando hay escrituras sin transaccion explicita
- Procesa lotes de cambios desde `data/changes/*.sql`
- Genera backup de snapshot JSON
- Genera rollback SQL base por ejecucion aprobada
- Registra corridas en `out/execution_log.json` y `out/latest_run.json`

## Ejecutar
```powershell
cd C:\Users\Administrator\portfolio-redes-projects\sql-backup-validation-pipeline-lab
powershell -ExecutionPolicy Bypass -File .\scripts\main.ps1
```

## Probar
```powershell
cd C:\Users\Administrator\portfolio-redes-projects\sql-backup-validation-pipeline-lab
python -m unittest tests\test_sql_pipeline.py -v
```
