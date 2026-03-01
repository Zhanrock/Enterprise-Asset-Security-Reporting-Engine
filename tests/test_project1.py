"""
test_project1.py - Unit tests for Enterprise Asset & Security Reporting Engine
"""

import os
import sys
import json
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from database import init_db, get_connection
from ingest import (ingest_assets_csv, ingest_vulnerabilities_json,
                    ingest_compliance_csv)
from report import generate_report


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.tmp.name
        self.tmp.close()
        init_db(self.db_path)

    def tearDown(self):
        os.unlink(self.db_path)

    def test_tables_created(self):
        conn = get_connection(self.db_path)
        tables = {
            row["name"]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        conn.close()
        self.assertIn("Assets", tables)
        self.assertIn("Vulnerabilities", tables)
        self.assertIn("Compliance_Status", tables)


class TestIngest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.tmp.name
        self.tmp.close()
        init_db(self.db_path)

        # Write a temp CSV
        self.csv_fd, self.csv_path = tempfile.mkstemp(suffix=".csv")
        with os.fdopen(self.csv_fd, "w") as f:
            f.write("asset_id,name,category,owner,location,purchase_date,warranty_expiry,status\n")
            f.write("T001,Test Laptop,Laptop,Tester,Office,2023-01-01,2026-01-01,Active\n")
            f.write("T002,Test Server,Server,Ops,DC,2022-06-01,2025-06-01,Active\n")

        # Write a temp JSON
        self.json_fd, self.json_path = tempfile.mkstemp(suffix=".json")
        data = [
            {"asset_id": "T001", "cve_id": "CVE-2024-9999",
             "severity": "High", "description": "Test vuln",
             "detected_date": "2024-01-01", "status": "Open"},
        ]
        with os.fdopen(self.json_fd, "w") as f:
            json.dump(data, f)

        # Write compliance CSV
        self.comp_fd, self.comp_path = tempfile.mkstemp(suffix=".csv")
        with os.fdopen(self.comp_fd, "w") as f:
            f.write("asset_id,framework,control_id,compliant,last_checked,notes\n")
            f.write("T001,CIS,CIS-1.1,Yes,2024-01-15,OK\n")

    def tearDown(self):
        os.unlink(self.db_path)
        os.unlink(self.csv_path)
        os.unlink(self.json_path)
        os.unlink(self.comp_path)

    def test_ingest_assets(self):
        count = ingest_assets_csv(self.csv_path, self.db_path)
        self.assertEqual(count, 2)
        conn = get_connection(self.db_path)
        rows = conn.execute("SELECT * FROM Assets").fetchall()
        conn.close()
        self.assertEqual(len(rows), 2)

    def test_ingest_vulnerabilities(self):
        ingest_assets_csv(self.csv_path, self.db_path)  # FK dependency
        count = ingest_vulnerabilities_json(self.json_path, self.db_path)
        self.assertEqual(count, 1)
        conn = get_connection(self.db_path)
        rows = conn.execute("SELECT * FROM Vulnerabilities").fetchall()
        conn.close()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["cve_id"], "CVE-2024-9999")

    def test_ingest_compliance(self):
        ingest_assets_csv(self.csv_path, self.db_path)
        count = ingest_compliance_csv(self.comp_path, self.db_path)
        self.assertEqual(count, 1)

    def test_upsert_asset(self):
        """Ingesting the same asset twice should not duplicate it."""
        ingest_assets_csv(self.csv_path, self.db_path)
        ingest_assets_csv(self.csv_path, self.db_path)
        conn = get_connection(self.db_path)
        rows = conn.execute("SELECT * FROM Assets").fetchall()
        conn.close()
        self.assertEqual(len(rows), 2)  # Still 2, not 4

    def test_report_generation(self):
        ingest_assets_csv(self.csv_path, self.db_path)
        ingest_vulnerabilities_json(self.json_path, self.db_path)
        ingest_compliance_csv(self.comp_path, self.db_path)
        with tempfile.TemporaryDirectory() as out_dir:
            path = generate_report(db_path=self.db_path, output_dir=out_dir)
            self.assertTrue(os.path.isfile(path))
            self.assertTrue(path.endswith(".xlsx"))

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            ingest_assets_csv("/no/such/file.csv", self.db_path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
