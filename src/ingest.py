"""
ingest.py - Parse procurement CSVs and security tool outputs into the database.
"""

import csv
import json
import os
import sqlite3
from datetime import date
from typing import Optional

from database import get_connection, init_db, DB_PATH


# ---------------------------------------------------------------------------
# Asset ingestion from procurement CSV
# ---------------------------------------------------------------------------

def ingest_assets_csv(csv_path: str, db_path: str = DB_PATH) -> int:
    """
    Ingest assets from a CSV file.

    Expected columns (case-insensitive):
        asset_id, name, category, owner, location,
        purchase_date, warranty_expiry, status
    """
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    conn = get_connection(db_path)
    count = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Normalise headers
        reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]
        for row in reader:
            conn.execute(
                """
                INSERT INTO Assets (asset_id, name, category, owner, location,
                                    purchase_date, warranty_expiry, status)
                VALUES (:asset_id, :name, :category, :owner, :location,
                        :purchase_date, :warranty_expiry, :status)
                ON CONFLICT(asset_id) DO UPDATE SET
                    name            = excluded.name,
                    category        = excluded.category,
                    owner           = excluded.owner,
                    location        = excluded.location,
                    purchase_date   = excluded.purchase_date,
                    warranty_expiry = excluded.warranty_expiry,
                    status          = excluded.status
                """,
                {
                    "asset_id":       row.get("asset_id", "").strip(),
                    "name":           row.get("name", "").strip(),
                    "category":       row.get("category", "").strip(),
                    "owner":          row.get("owner", "").strip(),
                    "location":       row.get("location", "").strip(),
                    "purchase_date":  row.get("purchase_date", "").strip(),
                    "warranty_expiry":row.get("warranty_expiry", "").strip(),
                    "status":         row.get("status", "Active").strip(),
                },
            )
            count += 1

    conn.commit()
    conn.close()
    print(f"[Ingest] {count} asset(s) loaded from {csv_path}")
    return count


# ---------------------------------------------------------------------------
# Vulnerability ingestion from JSON (scanner output)
# ---------------------------------------------------------------------------

def ingest_vulnerabilities_json(json_path: str, db_path: str = DB_PATH) -> int:
    """
    Ingest vulnerabilities from a JSON file produced by a security scanner.

    Expected JSON structure:
        [
            {
                "asset_id": "A001",
                "cve_id":   "CVE-2024-1234",
                "severity": "High",
                "description": "...",
                "detected_date": "2024-01-15",
                "status": "Open"
            },
            ...
        ]
    """
    if not os.path.isfile(json_path):
        raise FileNotFoundError(f"JSON not found: {json_path}")

    with open(json_path, encoding="utf-8") as f:
        records = json.load(f)

    conn = get_connection(db_path)
    count = 0
    today = date.today().isoformat()
    for rec in records:
        conn.execute(
            """
            INSERT INTO Vulnerabilities
                (asset_id, cve_id, severity, description,
                 detected_date, remediated_date, status)
            VALUES
                (:asset_id, :cve_id, :severity, :description,
                 :detected_date, :remediated_date, :status)
            """,
            {
                "asset_id":       rec.get("asset_id", ""),
                "cve_id":         rec.get("cve_id", ""),
                "severity":       rec.get("severity", ""),
                "description":    rec.get("description", ""),
                "detected_date":  rec.get("detected_date", today),
                "remediated_date":rec.get("remediated_date"),
                "status":         rec.get("status", "Open"),
            },
        )
        count += 1

    conn.commit()
    conn.close()
    print(f"[Ingest] {count} vulnerability record(s) loaded from {json_path}")
    return count


# ---------------------------------------------------------------------------
# Compliance ingestion from CSV
# ---------------------------------------------------------------------------

def ingest_compliance_csv(csv_path: str, db_path: str = DB_PATH) -> int:
    """
    Ingest compliance status from a CSV file.

    Expected columns: asset_id, framework, control_id, compliant, last_checked, notes
    """
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    conn = get_connection(db_path)
    count = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]
        for row in reader:
            compliant_val = str(row.get("compliant", "0")).strip().lower()
            compliant_int = 1 if compliant_val in ("1", "yes", "true") else 0
            conn.execute(
                """
                INSERT INTO Compliance_Status
                    (asset_id, framework, control_id, compliant, last_checked, notes)
                VALUES
                    (:asset_id, :framework, :control_id, :compliant, :last_checked, :notes)
                """,
                {
                    "asset_id":    row.get("asset_id", "").strip(),
                    "framework":   row.get("framework", "").strip(),
                    "control_id":  row.get("control_id", "").strip(),
                    "compliant":   compliant_int,
                    "last_checked":row.get("last_checked", "").strip(),
                    "notes":       row.get("notes", "").strip(),
                },
            )
            count += 1

    conn.commit()
    conn.close()
    print(f"[Ingest] {count} compliance record(s) loaded from {csv_path}")
    return count


if __name__ == "__main__":
    init_db()
    base = os.path.join(os.path.dirname(__file__), "..", "data")
    ingest_assets_csv(os.path.join(base, "sample_assets.csv"))
    ingest_vulnerabilities_json(os.path.join(base, "sample_vulnerabilities.json"))
    ingest_compliance_csv(os.path.join(base, "sample_compliance.csv"))
