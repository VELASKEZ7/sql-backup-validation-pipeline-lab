# Arquitectura

Flujo:

1. Entrada de cambio SQL en `data/change.sql`.
2. `src/sql_pipeline.py` ejecuta validacion de reglas.
3. Si pasa, copia `data/mock_db_snapshot.json` a `out/backups/`.
4. Registra evento con estado y timestamp en `out/execution_log.json`.

Reglas de validacion:
- Bloquear `DROP DATABASE`
- Bloquear `TRUNCATE TABLE`
- Bloquear `DELETE FROM` sin clausula `WHERE`
