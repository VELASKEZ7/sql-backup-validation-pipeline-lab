import json
import shutil
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from sql_pipeline import run_pipeline, validate_sql  # noqa: E402


class SqlPipelineTests(unittest.TestCase):
    def test_validate_sql_blocks_dangerous_ops(self):
        sql = "DROP DATABASE prod_db;"
        issues = validate_sql(sql)
        self.assertTrue(issues)

    def test_run_pipeline_approved_creates_backup(self):
        tmp_path = ROOT / "tests" / ".tmp_sql_pipeline"
        if tmp_path.exists():
            shutil.rmtree(tmp_path)
        tmp_path.mkdir(parents=True, exist_ok=True)
        try:
            sql_path = tmp_path / "change.sql"
            snap = tmp_path / "snap.json"
            out = tmp_path / "out"
            sql_path.write_text("UPDATE users SET active = 1 WHERE id = 7;", encoding="utf-8")
            snap.write_text(json.dumps({"rows": 10}), encoding="utf-8")
            result = run_pipeline(sql_path, snap, out)
            self.assertEqual(result["status"], "approved")
            self.assertTrue(Path(result["backup_file"]).exists())
        finally:
            if tmp_path.exists():
                shutil.rmtree(tmp_path)


if __name__ == "__main__":
    unittest.main()
