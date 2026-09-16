from pathlib import Path
import pandas as pd
from ydata_profiling import ProfileReport

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "raw" / "store-data.csv"
OUTPUT = ROOT / "reports" / "eda_report.html"

def make_profiling_report():
    df = pd.read_csv(DATA, encoding='latin-1')
    profile = ProfileReport(df, title="EDA Report", explorative=True)
    OUTPUT.parent.mkdir(exist_ok=True)
    profile.to_file(OUTPUT)
    print(f"Wrote {OUTPUT}")

if __name__ == "__main__":
    make_profiling_report()
