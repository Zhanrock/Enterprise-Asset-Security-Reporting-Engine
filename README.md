# 🔐 Enterprise Asset & Security Reporting Engine

A centralized relational database and reporting system that automates the lifecycle management of corporate assets while tracking real-time cybersecurity KPIs.

## Overview

This tool ingests procurement CSVs and security scanner outputs into a normalized SQLite database, then generates rich multi-sheet Excel dashboards with vulnerability summaries, patch compliance tables (VLOOKUP/INDEX MATCH equivalent), and KPI charts.

### Key Features

- **SQLite database** with normalized `Assets`, `Vulnerabilities`, and `Compliance_Status` tables
- **Python ingestion pipeline** for procurement CSVs and JSON vulnerability scanner outputs
- **Excel dashboard** with 5 sheets: KPI Dashboard (with bar charts), Patch Compliance, Assets Inventory, Vulnerabilities (colour-coded by severity), Compliance Status
- **Upsert logic** to safely re-ingest updated data without duplication
- **100% audit visibility** for security reviews

## Tech Stack

| Component   | Technology         |
|-------------|-------------------|
| Database    | SQLite3 (built-in) |
| Data Layer  | Python, Pandas     |
| Reporting   | Openpyxl, Excel    |
| Testing     | unittest           |

## Project Structure

```
project1/
├── src/
│   ├── database.py     # Schema init & connection management
│   ├── ingest.py       # CSV/JSON data ingestion
│   ├── report.py       # Excel dashboard generation
│   └── main.py         # CLI entry point
├── data/
│   ├── sample_assets.csv
│   ├── sample_vulnerabilities.json
│   └── sample_compliance.csv
├── outputs/            # Generated Excel reports
├── tests/
│   └── test_project1.py
└── requirements.txt
```

## Installation

```bash
cd project1
pip install -r requirements.txt
```

## Usage

```bash
# Full pipeline: init DB, ingest sample data, generate report
cd src
python main.py all

# Step by step:
python main.py init                                      # Initialise database
python main.py ingest                                    # Load sample data
python main.py ingest --assets ../data/my_assets.csv    # Custom assets file
python main.py ingest --vulns  ../data/vulns.json        # Custom vulnerabilities
python main.py report                                    # Generate Excel report
```

## Data Formats

### Assets CSV
```
asset_id,name,category,owner,location,purchase_date,warranty_expiry,status
A001,Dell XPS 15,Laptop,Alice Johnson,HQ Floor 2,2022-03-10,2025-03-10,Active
```

### Vulnerabilities JSON
```json
[
  {
    "asset_id": "A001",
    "cve_id": "CVE-2024-1234",
    "severity": "High",
    "description": "Remote code execution in OpenSSL",
    "detected_date": "2024-01-10",
    "status": "Open"
  }
]
```

### Compliance CSV
```
asset_id,framework,control_id,compliant,last_checked,notes
A001,CIS,CIS-1.1,Yes,2024-01-15,Inventory up to date
```

## Generated Report Sheets

| Sheet             | Contents                                           |
|-------------------|---------------------------------------------------|
| KPI Dashboard     | Asset pivot, vulnerability severity chart, compliance % |
| Patch Compliance  | Per-asset open vuln count + patch status flag      |
| Assets Inventory  | Full asset list                                    |
| Vulnerabilities   | All CVEs with colour-coded severity                |
| Compliance Status | Controls compliance with pass/fail highlighting    |

## Running Tests

```bash
python tests/test_project1.py
```

Expected: **7 tests, 0 failures**

## Impact

- Achieves 100% visibility for security audits
- Eliminates manual spreadsheet tracking
- Supports multiple compliance frameworks (CIS, NIST, ISO 27001)
- Reduces patch management review time significantly
