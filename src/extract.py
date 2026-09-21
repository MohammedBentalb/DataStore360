import pandas as pd
from sqlalchemy import text

from src.config import RAW_CSV, STAGING_TABLE, STAGING_SCHEMA
from src.db import get_engine

def load_csv_to_staging(path: str = RAW_CSV):
    df = pd.read_csv(path, encoding="latin-1")
    engine = get_engine()
    # tan sowel ossam;
    with engine.begin() as con:
        con.execute(text("TRUNCATE staging.superstore_raw"))
    df.to_sql(
        STAGING_TABLE,
        engine,
        schema=STAGING_SCHEMA,
        index=False,
        if_exists="append",
    )