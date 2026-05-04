# aCommerce Data Engineer Quiz

Submission project for the aCommerce Data Engineer quiz. The repository contains two deliverables:

- `1_python_submit`: a Python ETL pipeline that scrapes book data from `http://books.toscrape.com/`, saves raw JSON, filters the data, and writes a CSV result.
- `2_sql_submit`: PostgreSQL DDL, data ingestion script, ER diagram, and analytical SQL queries for monthly promotion sales and FIFO COGS.

## Project Structure

```text
.
├── 1_python_submit/
│   ├── main.py
│   ├── requirements.txt
│   ├── check_imports.py
│   ├── README.md
│   ├── sample/
│   ├── data/
│   │   ├── raw/data.json
│   │   └── transformed/result.csv
│   └── src/
│       ├── config.py
│       ├── framework.py
│       ├── scraper.py
│       └── transformer.py
└── 2_sql_submit/
    ├── 00_Data_Ingestion.py
    ├── 01_ER_Diagram.pdf
    ├── 02_Part1_DDL.sql
    ├── 03_Part2_Monthly_Sales.sql
    └── 04_Part3_FIFO_COGS.sql
```

## Part 1: Python Book Scraping Pipeline

The Python pipeline is started from `1_python_submit/main.py`. It calls `src.framework.flow()`, which runs these steps:

1. `BookScraper` scrapes all paginated book listing pages from `books.toscrape.com`.
2. For each book, the scraper opens the product detail page and collects:
   - UPC
   - Product Type
   - Price excluding tax
   - Price including tax
   - Tax
   - Availability
   - Number of reviews
   - Description
   - Rating
   - Title
3. Raw records are saved to `1_python_submit/data/raw/data.json`.
4. `BookTransformer` streams the JSON file with `ijson`, filters records where:
   - rating is at least 4 stars
   - `Price (incl. tax)` is less than 20
5. Filtered records are written to `1_python_submit/data/transformed/result.csv`.

The included generated output currently contains:

- `data/raw/data.json`: 1000 scraped book records
- `data/transformed/result.csv`: 75 filtered records

### Python Requirements

Install dependencies from `requirements.txt`:

```powershell
cd 1_python_submit
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Required packages:

- `requests`
- `beautifulsoup4`
- `lxml`
- `pandas`
- `ijson`

### Run the Python Pipeline

```powershell
cd 1_python_submit
python main.py
```

Optional output directories can be overridden with environment variables:

```powershell
$env:RAW_DIRECTORY = "data/raw"
$env:TRANSFORMED_DIRECTORY = "data/transformed"
python main.py
```

### Validate Python Imports

```powershell
cd 1_python_submit
python check_imports.py
```

## Part 2: SQL Submission

The SQL deliverable targets PostgreSQL and is located in `2_sql_submit`.

### Files

- `01_ER_Diagram.pdf`: ER diagram artifact for the database model.
- `02_Part1_DDL.sql`: creates the relational schema and indexes.
- `00_Data_Ingestion.py`: loads JSON sample data into PostgreSQL tables.
- `03_Part2_Monthly_Sales.sql`: calculates monthly promotion sales in USD.
- `04_Part3_FIFO_COGS.sql`: calculates COGS per sales order using FIFO matching.

### Database Schema

The DDL creates these core tables:

- `shop`
- `item`
- `promotion`
- `promotion_product`
- `sales_order`
- `sales_order_line`
- `sales_order_line_item`
- `item_receipt`
- `item_receipt_line`
- `daily_usd_exchange_rate`

Indexes are included for common join and filtering fields such as order date, shop, product, item, receipt, and exchange-rate keys.

### SQL Data Ingestion

`00_Data_Ingestion.py` uses `psycopg2` to load source JSON files into PostgreSQL.

Default database connection in the script:

```python
DB_CONFIG = {
    "host": "localhost",
    "dbname": "de_exam",
    "user": "de_user",
    "password": "password",
    "port": 5432
}
```

Before running the ingestion script:

1. Create the PostgreSQL database and user.
2. Run `02_Part1_DDL.sql` against the database.
3. Update `DATA_PATH` in `00_Data_Ingestion.py` so it points to the local folder containing the sample JSON files.
4. Install `psycopg2` if it is not available.

Example:

```powershell
cd 2_sql_submit
pip install psycopg2-binary
python 00_Data_Ingestion.py
```

### Run SQL Files

Example with `psql`:

```powershell
cd 2_sql_submit
psql -h localhost -p 5432 -U de_user -d de_exam -f 02_Part1_DDL.sql
psql -h localhost -p 5432 -U de_user -d de_exam -f 03_Part2_Monthly_Sales.sql
psql -h localhost -p 5432 -U de_user -d de_exam -f 04_Part3_FIFO_COGS.sql
```

## Query Logic Summary

### Monthly Sales by Promotion

`03_Part2_Monthly_Sales.sql`:

- joins sales orders, order lines, promotion products, promotions, and daily exchange rates
- includes only positive sales lines
- checks that the sales timestamp falls within the promotion period
- converts gross amount to USD using the daily exchange rate
- groups by sales month and promotion

### FIFO COGS

`04_Part3_FIFO_COGS.sql`:

- builds cumulative received quantities per item ordered by receipt time
- builds cumulative sold quantities per item ordered by sales order time
- matches overlapping cumulative quantity ranges between receipts and sales
- multiplies matched quantity by receipt unit cost
- returns COGS per sales order

## Notes

- The Python transformer is implemented with streaming JSON parsing, so it does not need to load the full raw JSON file into memory.
- The SQL ingestion script currently contains a machine-specific `DATA_PATH`; update it before running on another machine.
- The generated CSV may contain source-site encoding artifacts such as `Â£` because the scraped source values are preserved as text.
