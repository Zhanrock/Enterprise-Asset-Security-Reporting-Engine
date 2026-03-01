"""
database.py - SQLite schema and connection management for the
Enterprise Asset & Security Reporting Engine.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "assets.db")


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Return a connection with row_factory set."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: str = DB_PATH) -> None:
    """Create all tables if they do not yet exist."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS Assets (
            asset_id        TEXT PRIMARY KEY,
            name            TEXT NOT NULL,
            category        TEXT NOT NULL,          -- e.g. Laptop, Server, Switch
            owner           TEXT,
            location        TEXT,
            purchase_date   TEXT,
            warranty_expiry TEXT,
            status          TEXT DEFAULT 'Active'   -- Active | Decommissioned | In-Repair
        );

        CREATE TABLE IF NOT EXISTS Vulnerabilities (
            vuln_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id        TEXT NOT NULL REFERENCES Assets(asset_id),
            cve_id          TEXT,
            severity        TEXT,                   -- Critical | High | Medium | Low
            description     TEXT,
            detected_date   TEXT,
            remediated_date TEXT,
            status          TEXT DEFAULT 'Open'     -- Open | In-Progress | Remediated
        );

        CREATE TABLE IF NOT EXISTS Compliance_Status (
            compliance_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id        TEXT NOT NULL REFERENCES Assets(asset_id),
            framework       TEXT,                   -- e.g. CIS, NIST, ISO27001
            control_id      TEXT,
            compliant       INTEGER DEFAULT 0,      -- 0=No, 1=Yes
            last_checked    TEXT,
            notes           TEXT
        );
        """
    )
    conn.commit()
    conn.close()
    print(f"[DB] Database initialised at: {db_path}")


if __name__ == "__main__":
    init_db()
