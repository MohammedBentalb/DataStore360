CREATE SCHEMA IF NOT EXISTS core;

CREATE TABLE IF NOT EXISTS core.customers(
    customerid TEXT PRIMARY KEY,
    customername TEXT NOT NULL,
    Segment TEXT,
    country TEXT,
    city TEXT,
    state TEXT,
    postal_code TEXT,
    region TEXT
);

CREATE TABLE IF NOT EXISTS core.products(
    productid TEXT PRIMARY KEY,
    category TEXT,
    subcategory TEXT,
    productname TEXT
);

CREATE TABLE IF NOT EXISTS core.orders(
    rowid INT PRIMARY KEY,
    orderid TEXT NOT NULL,
    customerid TEXT NOT NULL REFERENCES core.customers(customerid),
    productid TEXT NOT NULL REFERENCES core.products(productid),
    orderdate DATE,
    shipdate DATE,
    shipmode TEXT,
    sales NUMERIC,
    quantity INT,
    discount NUMERIC,
    profit NUMERIC,
    deliverytime INT,
    profit_margin NUMERIC
);