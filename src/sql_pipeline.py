import argparse
import json
import re
from datetime import datetime, UTC
from pathlib import Path
from shutil import copyfile


def validate_sql(sql_text):
    issues = []
    normalized = sql_text.upper()

    if "DROP DATABASE" in normalized:
        issues.append({"severity": "error", "message": "Found forbidden statement: DROP DATABASE"})

    if "TRUNCATE TABLE" in normalized:
        issues.append({"severity": "error", "message": "Found forbidden statement: TRUNCATE TABLE"})

    delete_matches = re.findall(r"DELETE\s+FROM\s+[A-Z0-9_\.]+(\s*;|\s*$)", normalized)
    if delete_matches:
        issues.append({"severity": "error", "message": "Found DELETE without WHERE clause"})

    has_writes = bool(re.search(r"\b(UPDATE|DELETE|INSERT)\b", normalized))
    has_transaction = "BEGIN TRANSACTION" in normalized and "COMMIT" in normalized
    if has_writes and not has_transaction:
        issues.append({"severity": "warning", "message": "Write statements without explicit transaction"})

    return issues


def run_pipeline(sql_path, snapshot_path, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    backups_dir = output_dir / "backups"
    backups_dir.mkdir(parents=True, exist_ok=True)

    sql_text = sql_path.read_text(encoding="utf-8")
    issues = validate_sql(sql_text)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    has_errors = any(item["severity"] == "error" for item in issues)

    if has_errors:
        result = {
            "status": "blocked",
            "timestamp_utc": timestamp,
            "issues": issues,
            "backup_file": None,
            "sql_file": str(sql_path),
        }
    else:
        backup_file = backups_dir / f"backup_{timestamp}.json"
        copyfile(snapshot_path, backup_file)
        rollback_file = output_dir / f"rollback_{timestamp}.sql"
        rollback_file.write_text(
            "-- Mock rollback generated from snapshot metadata\n"
            "BEGIN TRANSACTION;\n"
            "-- TODO: replace with table-level restore commands\n"
            "ROLLBACK;\n",
            encoding="utf-8",
        )
        result = {
            "status": "approved",
            "timestamp_utc": timestamp,
            "issues": issues,
            "backup_file": str(backup_file),
            "rollback_file": str(rollback_file),
            "sql_file": str(sql_path),
        }

    return result


def process_batch(sql_files, snapshot_path, output_dir):
    results = [run_pipeline(path, snapshot_path, output_dir) for path in sql_files]
    run_summary = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "total_files": len(results),
        "approved_files": sum(1 for r in results if r["status"] == "approved"),
        "blocked_files": sum(1 for r in results if r["status"] == "blocked"),
        "results": results,
    }
    log_file = output_dir / "execution_log.json"
    latest_file = output_dir / "latest_run.json"
    if log_file.exists():
        history = json.loads(log_file.read_text(encoding="utf-8"))
    else:
        history = []
    history.append(run_summary)
    log_file.write_text(json.dumps(history, indent=2), encoding="utf-8")
    latest_file.write_text(json.dumps(run_summary, indent=2), encoding="utf-8")
    return run_summary


def main():
    parser = argparse.ArgumentParser(description="SQL validation + backup pipeline")
    parser.add_argument("--sql", help="SQL file to validate")
    parser.add_argument("--sql-dir", help="Directory with .sql files")
    parser.add_argument("--snapshot", required=True, help="Mock snapshot json")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if args.sql_dir:
        sql_files = sorted(Path(args.sql_dir).glob("*.sql"))
    elif args.sql:
        sql_files = [Path(args.sql)]
    else:
        raise ValueError("Either --sql or --sql-dir must be provided")

    summary = process_batch(sql_files, Path(args.snapshot), output_dir)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
