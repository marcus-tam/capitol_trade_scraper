import os
import pandas as pd
import psycopg2
from decimal import Decimal

# Load PostgreSQL connection details
postgres_user = os.getenv('POSTGRES_USER', 'myuser')
postgres_password = os.getenv('POSTGRES_PASSWORD', 'mypassword')
postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
postgres_port = os.getenv('POSTGRES_PORT', '5432')
postgres_db = os.getenv('POSTGRES_DB', 'mydb')

# Read CSV
cleaned_trades_df = pd.read_csv("cleaned_trades.csv")
cleaned_trades_df.drop(axis=1, columns=['Unnamed: 0'], inplace=True)

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=postgres_db,
    user=postgres_user,
    password=postgres_password,
    host=postgres_host,
    port=postgres_port
)
cur = conn.cursor()

# Insert each row using the stored function
for _, row in cleaned_trades_df.iterrows():
    stock_price = row.get('stock_price', None)

    # Convert stock_price to Decimal to match PostgreSQL DECIMAL(10,2)
    if stock_price is not None:
        stock_price = Decimal(str(stock_price))  # Ensures correct type

    cur.execute("""
        SELECT insert_capitol_trade(
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """, (
        row['politician'],
        row['party'],
        row['traded_company_name'],
        row.get('traded_company_ticker', None),  # Handle NULL values
        row['trade_filed_date'],
        row['trade_owner'],
        row['trade_type'],
        row['trade_size'],
        stock_price,  # Now correctly formatted as DECIMAL
        row['published_datetime'],
        row['traded_datetime'],
        row.get('trade_id', None)  # Handle NULL values
    ))

# Commit changes and close connection
conn.commit()
cur.close()
conn.close()
