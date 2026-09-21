import concurrent.futures

import pandas as pd
from sqlalchemy import text

from src.config import STAGING_SCHEMA_TABLE, CLEANED_CSV
from src.db import get_engine

def insert_costumers(df: pd.DataFrame, con):
    customers = df[['Customer ID', 'Customer Name', 'Segment', 'Country', 'City', 'State', 'Postal Code', 'Region']].drop_duplicates(subset="Customer ID").rename(columns={
            'Customer ID': 'customerid',
            'Customer Name': 'customername',
            'Segment': 'segment',
            'Country': 'country',
            'City': 'city',
            'State': 'state',
            'Postal Code': 'postal_code',
            'Region': 'region',
        })

    stmt = text("""
                    INSERT INTO core.customers (customerid, customername, segment, country, city, state, postal_code, region) 
                    VALUES (:customerid, :customername, :segment, :country, :city, :state, :postal_code, :region) 
                    ON CONFLICT (customerid) DO UPDATE SET
                        customername = EXCLUDED.customername,
                        segment = EXCLUDED.segment,
                        country = EXCLUDED.country,
                        city = EXCLUDED.city,
                        state = EXCLUDED.state,
                        postal_code = EXCLUDED.postal_code,
                        region = EXCLUDED.region
                      """)
    con.execute(stmt, customers.to_dict("records"))


def insert_products(df: pd.DataFrame, con):
    products = df[['Product ID', 'Category', 'Sub-Category', 'Product Name']].drop_duplicates(subset='Product ID').rename(columns={
            'Product ID': 'productid',
            'Category': 'category',
            'Sub-Category': 'subcategory',
            'Product Name': 'productname',
        })

    stmt = text("""
            INSERT INTO core.products (productid, productname, category, subcategory)
            Values (:productid, :productname, :category, :subcategory)
            ON CONFLICT (productid) DO UPDATE SET
            category = EXCLUDED.category,
            subcategory = EXCLUDED.subcategory,
            productname = EXCLUDED.productname
            """)
    con.execute(stmt , products.to_dict("records"))


def insert_orders(df: pd.DataFrame, con):
    cols = [
        'rowid', 'orderid', 'customerid', 'productid', 'orderdate', 'shipdate',
        'shipmode', 'sales', 'quantity', 'discount', 'profit', 'deliverytime', 'profit_margin',
    ]

    orders = df.rename(columns={
        'Row ID': 'rowid',
        'Order ID': 'orderid',
        'Customer ID': 'customerid',
        'Product ID': 'productid',
        'Order Date': 'orderdate',
        'Ship Date': 'shipdate',
        'Ship Mode': 'shipmode',
        'Sales': 'sales',
        'Quantity': 'quantity',
        'Discount': 'discount',
        'Profit': 'profit',
        'Duration': 'deliverytime',
        'Profit Margin': 'profit_margin',
    })[cols]

    con.execute(text("DELETE FROM core.orders"))
    stmt = text(f"""
            INSERT INTO core.orders ({','.join(cols)})
            VALUES ({','.join(f':{c}' for c in cols)})
        """)
    con.execute(stmt, orders.to_dict("records"))

def load(df: pd.DataFrame, engine):
    insert_costumers(df, engine)
    insert_products(df, engine)
    insert_orders(df, engine)


def run_load(src: str = CLEANED_CSV, dist: str = "dataset_raw"):
    engine = get_engine()
    df = pd.read_csv(src, encoding='latin-1')
    with engine.begin() as con:
        insert_costumers(df, con)
        insert_products(df, con)
        insert_orders(df, con)