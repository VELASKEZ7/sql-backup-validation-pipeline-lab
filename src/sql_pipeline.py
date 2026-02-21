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
        issues.append("Found forbidden statement: DROP DATABASE")

    if "TRUNCATE TABLE" in normalized:
        issues.append("Found forbidden statement: TRUNCATE TABLE")

    delete_matches = re.findall(r"DELETE\s+FROM\s+[A-Z0-9_\.]+(\s*;|\s*$)", normalized)
    if delete_matches:
        issues.append("Found DELETE without WHERE clause")

    return issues


def run_pipeline(sql_path, snapshot_path, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    backups_dir = output_dir / "backups"
    backups_dir.mkdir(parents=True, exist_ok=True)

    sql_text = sql_path.read_text(encoding="utf-8")
    issues = validate_sql(sql_text)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")

    if issues:
        result = {
            "status": "blocked",
            "timestamp_utc": timestamp,
            "issues": issues,
            "backup_file": None,
        }
    else:
        backup_file = backups_dir / f"backup_{timestamp}.json"
        copyfile(snapshot_path, backup_file)
        result = {
            "status": "approved",
            "timestamp_utc": timestamp,
            "issues": [],
            "backup_file": str(backup_file),
        }

    log_file = output_dir / "execution_log.json"
    if log_file.exists():
        data = json.loads(log_file.read_text(encoding="utf-8"))
    else:
        data = []
    data.append(result)
    log_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description="SQL validation + backup pipeline")
    parser.add_argument("--sql", required=True, help="SQL file to validate")
    parser.add_argument("--snapshot", required=True, help="Mock snapshot json")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    args = parser.parse_args()

    result = run_pipeline(Path(args.sql), Path(args.snapshot), Path(args.output_dir))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
