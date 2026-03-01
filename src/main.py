"""
main.py - CLI entry point for the Enterprise Asset & Security Reporting Engine.

Usage:
    python main.py init                  # Initialise database
    python main.py ingest                # Load all sample data
    python main.py ingest --assets path/to/assets.csv
    python main.py ingest --vulns  path/to/vulns.json
    python main.py ingest --compliance path/to/comp.csv
    python main.py report                # Generate Excel report
    python main.py all                   # init + ingest + report
"""

import argparse
import os
import sys

# Make src importable when called from project root
sys.path.insert(0, os.path.dirname(__file__))

from database import init_db, DB_PATH
from ingest import ingest_assets_csv, ingest_vulnerabilities_json, ingest_compliance_csv
from report import generate_report

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def cmd_init(args):
    init_db(DB_PATH)


def cmd_ingest(args):
    if args.assets:
        ingest_assets_csv(args.assets)
    if args.vulns:
        ingest_vulnerabilities_json(args.vulns)
    if args.compliance:
        ingest_compliance_csv(args.compliance)
    if not any([args.assets, args.vulns, args.compliance]):
        # Default: load all sample files
        ingest_assets_csv(os.path.join(DATA_DIR, "sample_assets.csv"))
        ingest_vulnerabilities_json(os.path.join(DATA_DIR, "sample_vulnerabilities.json"))
        ingest_compliance_csv(os.path.join(DATA_DIR, "sample_compliance.csv"))


def cmd_report(args):
    path = generate_report()
    if path:
        print(f"Report ready: {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Enterprise Asset & Security Reporting Engine"
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init", help="Initialise the SQLite database")

    ingest_p = sub.add_parser("ingest", help="Load data into the database")
    ingest_p.add_argument("--assets",     help="Path to assets CSV")
    ingest_p.add_argument("--vulns",      help="Path to vulnerabilities JSON")
    ingest_p.add_argument("--compliance", help="Path to compliance CSV")

    sub.add_parser("report", help="Generate Excel dashboard report")

    sub.add_parser("all", help="Run init + ingest (samples) + report")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
    elif args.command == "ingest":
        cmd_ingest(args)
    elif args.command == "report":
        cmd_report(args)
    elif args.command == "all":
        cmd_init(args)
        # Create a namespace with default None values for ingest args
        import types
        ingest_args = types.SimpleNamespace(assets=None, vulns=None, compliance=None)
        cmd_ingest(ingest_args)
        cmd_report(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
