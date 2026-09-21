from pathlib import Path
import pandas as pd
from data_profiling import ProfileReport

from src.config import CLEAN_REPORT_HTML, CLEANED_CSV, RAW_CSV, RAW_REPORT_HTML


def make_profiling_report(csv_path=CLEANED_CSV, output=CLEAN_REPORT_HTML, title = "DataStore - Cleaned Dta"):
    df = pd.read_csv(csv_path, encoding='latin-1')
    profile = ProfileReport(df, title= title, explorative=True,
            vars={"num": {"chi_squared_threshold": 0.0},
            "cat": {"chi_squared_threshold": 0.0}},
        )
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    profile.to_file(output)
    print(f"Wrote {output}")

if __name__ == "__main__":
    make_profiling_report(RAW_CSV, RAW_REPORT_HTML)
