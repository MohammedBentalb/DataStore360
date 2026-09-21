CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE IF NOT EXISTS staging.superstore_raw(
    "Row ID" INT,
    "Order ID" TEXT,
    "Order Date" TEXT,
    "Ship Date" TEXT,
    "Ship Mode" TEXT,
    "Customer ID" TEXT,
    "Customer Name" TEXT,
    "Segment" TEXT,
    "Country" TEXT,
    "Region" TEXT,
    "State" TEXT,
    "City" TEXT,
    "Postal Code" TEXT,
    "Product ID" TEXT,
    "Product Name" TEXT,
    "Category" TEXT,
    "Sub-Category" TEXT,
    "Sales" TEXT,
    "Quantity" TEXT,
    "Discount" TEXT,
    "Profit" TEXT
);