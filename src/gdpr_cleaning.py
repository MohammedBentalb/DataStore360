from operator import index
from pathlib import Path

import pandas as pd
import hashlib

from sqlalchemy import text

from src.config import STAGING_SCHEMA_TABLE, CLEANED_CSV
from src.db import get_engine


def parse_numeric(df: pd.DataFrame):
    for col in ['Sales', 'Quantity', 'Discount', 'Profit', "Row ID"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# starting with parsing dates
def parse_dates(original: pd.DataFrame):
    cols = ['Order Date', 'Ship Date']
    original[cols] = original[cols].apply(pd.to_datetime, format="mixed")

# %%
#drop duplicates
def remove_duplicates(original: pd.DataFrame):
    original.drop_duplicates(inplace=True)

# %%
def normalize_text(original :pd.DataFrame, column: str):
    original[column] = original[column].str.title().str.strip()

# %%
def correct_segment(original : pd.DataFrame):
    corr = {"Consumer" : "Consumer", "Consumerr" : "Consumer", "Corporate" : "Corporate", "Corporrate" : "Corporate"}
    original['Segment'] = original['Segment'].replace(corr)

# %%
def drop_wrong_discounts(original : pd.DataFrame):
    original.drop(original[original['Discount'] > 1].index, inplace=True)
    original.reset_index(drop=True ,inplace=True)

# %%
#khass nhandli mode khawi, dates khawin

def handle_null_mode(original: pd.DataFrame):
    # fill from the same command mode
    m = original['Ship Mode'].isna()
    f = original.dropna(subset='Ship Mode').groupby('Order ID')['Ship Mode'].agg(lambda x: x.mode()[0])
    original.loc[m, 'Ship Mode'] = original.loc[m, 'Order ID'].map(f)

    # fill from same product mean mode
    m = original['Ship Mode'].isna()
    g = original[~m].groupby('Product ID')['Ship Mode'].agg(lambda x: x.mode()[0])
    original.loc[m, 'Ship Mode'] = original.loc[original['Ship Mode'].isna(), 'Product ID'].map(g)

    ## 2 rows shato ndir fihom lmode
    original['Ship Mode'] = original['Ship Mode'].fillna(original['Ship Mode'].mode()[0])

# %%
def fix_ship_dates(original: pd.DataFrame):
    # maks so i filder only good columns to derive correct info from
    mask = (original['Ship Date'].notna()) & (original['Ship Date'] >= original['Order Date'])
    original['Duration'] = (original.loc[mask, 'Ship Date'] - original.loc[mask, 'Order Date']).dt.days
    mode_duration = original.dropna(subset='Duration').groupby('Ship Mode')['Duration'].agg(lambda x : x.mode()[0])
    original['Duration'] = original['Ship Mode'].map(mode_duration)

    mask = (original['Ship Date'].isna()) | (original['Ship Date'] < original['Order Date'])
    original.loc[mask, 'Ship Date'] = original.loc[mask, 'Order Date'] + pd.to_timedelta(original['Duration'], unit="D")

# %%
def fill_postal_code(original : pd.DataFrame):
    postal_mode = original.dropna(subset='Postal Code').groupby('City')['Postal Code'].agg(lambda x : x.mode()[0].split(".")[0])
    original.loc[original['Postal Code'].isna(), 'Postal Code'] = original.loc[original['Postal Code'].isna(), 'City'].map(postal_mode)

# %%
def add_unit_price(original : pd.DataFrame):
    #calculate the unit price for those that have sales abd g=have quantity, but for those who havv above 1m or sales or don't have sales
    data = original[(original['Sales'] > 0) | (original['Sales'] != 1131924.0) | (original['Sales'].notnull())]
    data = data[(original['Quantity'] > 0)]
    original['Unit Price'] = ((data['Sales'] / (1 - data['Discount'])) / data['Quantity'])

    #mode of the quanity by product
    holder = original.dropna(subset='Unit Price').groupby('Product Name')['Unit Price'].agg(lambda x : x.mode()[0])
    mask = original['Unit Price'].isna()
    original.loc[mask, 'Unit Price'] = original.loc[mask, 'Product Name'].map(holder)


    holder2 = original.dropna(subset='Unit Price').groupby('Sub-Category')['Unit Price'].agg(lambda x : x.mean())
    mask = original['Unit Price'].isna()
    original.loc[mask, 'Unit Price'] = original.loc[mask, 'Sub-Category'].map(holder2)
    original.drop(original[original['Quantity'].isna()].index, inplace=True)
    original.reset_index(drop=True, inplace=True)

# %%
def quantity_mode(original: pd.DataFrame):
    res = original.dropna(subset='Quantity').groupby('Product Name')['Quantity'].agg(lambda x : x.mode()[0])
    original.loc[original['Quantity'].isna(), 'Quantity'] = original.loc[original['Quantity'].isna(), "Product Name"].map(res)

# %%
def handle_1m_sales(original: pd.DataFrame):
    mask = original['Sales'] == 1131924.0
    wrong_sales = original[mask]
    for index in wrong_sales.index:
        product_id = original.loc[index, 'Product ID']
        quantity = original.loc[index, 'Quantity']
        discount = original.loc[index, 'Discount']

        mask2 = ~mask & (original['Product ID'] == product_id)
        data = original[mask2]
        if len(data) == 0 or quantity <= 0:
            continue

        unit_price = (data['Sales'] / (1 - data['Discount'])).sum() / data['Quantity'].sum() #hadi 9bel mandir func dyal price
        original.loc[index, 'Sales'] = unit_price * quantity * (1 - discount)
    original.drop(original[original['Sales'] == 1131924.0].index, inplace=True)
    original.reset_index(drop=True, inplace=True)

# %%
def handle_null_sales(original : pd.DataFrame):
    mask = (original['Sales'].isna()) & (original['Quantity'] > 0)
    original.loc[mask, "Sales"] = original.loc[mask, 'Unit Price'] * original.loc[mask, 'Quantity'] * (1 - original.loc[mask, 'Discount'])

# %%
def create_profit_margin(original):
    original['Profit Margin'] = original['Profit'] / original['Sales']

# %%
def handle_null_costumer_names(original: pd.DataFrame):
    mask = original['Customer Name'].isna()
    data = original.dropna(subset='Customer Name').groupby('Customer ID')['Customer Name'].first()
    original.loc[mask, 'Customer Name'] = original.loc[mask, 'Customer ID'].map(data)
    original.drop(original[original['Customer Name'].isna()].index, inplace=True)
    original.reset_index(inplace=True, drop=True)

# %%
def anonymize_names(original: pd.DataFrame):
    original['Customer Name'] = original['Customer Name'].apply(lambda x : hashlib.sha256(x.encode()).hexdigest())

# %%
def remove_duplicated_rows(original: pd.DataFrame):
    original.drop_duplicates(inplace=True, subset='Row ID')
    original.reset_index(drop=True, inplace=True)

def clean_df(df: pd.DataFrame):
    df = df.copy()
    parse_numeric(df)
    parse_dates(df)
    remove_duplicates(df)

    for col in ['Category', 'Sub-Category', 'Customer Name', 'Product Name', 'City', 'State']:
        normalize_text(df, col)

    correct_segment(df)
    drop_wrong_discounts(df)
    handle_null_mode(df)
    fix_ship_dates(df)
    fill_postal_code(df)
    add_unit_price(df)
    quantity_mode(df)
    handle_1m_sales(df)
    handle_null_sales(df)
    create_profit_margin(df)
    handle_null_costumer_names(df)
    anonymize_names(df)
    remove_duplicates(df)
    remove_duplicated_rows(df)

    return df

def run_clean(source_table: str = STAGING_SCHEMA_TABLE, dist_path = CLEANED_CSV):
    engine = get_engine()
    df = pd.read_sql(text(f"SELECT * FROM {source_table}"), engine)
    clean = clean_df(df)

    dist_path = Path(dist_path)
    dist_path.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(dist_path, index=False)

    print('cleaning sff')