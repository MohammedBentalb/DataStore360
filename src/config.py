import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

RAW_CSV = ROOT / "data" / "raw" / "store-data.csv"
CLEANED_CSV = ROOT / "data" / "cleaned" / "store-data-cleaned.csv"
RAW_REPORT_HTML = ROOT / "reports" / "raw" / "eda_report.html"
CLEAN_REPORT_HTML = ROOT / "reports" / "cleaned" / "eda_report.html"

STAGING_TABLE = "superstore_raw"
STAGING_SCHEMA = "staging"
STAGING_SCHEMA_TABLE = F"{STAGING_SCHEMA}.{STAGING_TABLE}"

