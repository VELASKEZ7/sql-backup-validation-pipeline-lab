# SQL Backup Validation Pipeline Lab

Pipeline local para validar scripts SQL y simular respaldo antes de ejecutar cambios.

## Que hace
- Revisa reglas basicas de seguridad SQL
- Bloquea patrones de alto riesgo (`DROP DATABASE`, `TRUNCATE`, `DELETE` sin `WHERE`)
- Genera backup de snapshot JSON
- Registra ejecucion en `out/execution_log.json`

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
