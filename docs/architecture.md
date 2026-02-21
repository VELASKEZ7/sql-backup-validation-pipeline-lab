# Arquitectura

Flujo:

1. Entrada de cambios SQL en `data/changes/*.sql`.
2. `src/sql_pipeline.py` ejecuta validacion de reglas por archivo.
3. Si pasa, copia `data/mock_db_snapshot.json` a `out/backups/`.
4. Genera archivo de rollback base en `out/rollback_*.sql`.
5. Registra corrida consolidada en `out/execution_log.json` y `out/latest_run.json`.

Reglas de validacion:
- Bloquear `DROP DATABASE`
- Bloquear `TRUNCATE TABLE`
- Bloquear `DELETE FROM` sin clausula `WHERE`
- Warning para `UPDATE/DELETE/INSERT` sin `BEGIN TRANSACTION ... COMMIT`
