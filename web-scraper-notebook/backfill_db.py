import pandas as pd
import os
import psycopg2
from psycopg2.extras import execute_batch


def get_db_connection():
    """Create database connection using environment variables."""
    postgres_user = os.getenv('POSTGRES_USER', 'myuser')
    postgres_password = os.getenv('POSTGRES_PASSWORD', 'mypassword')
    postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
    postgres_port = os.getenv('POSTGRES_PORT', '5432')
    postgres_db = os.getenv('POSTGRES_DB', 'mydb')

    conn = psycopg2.connect(
        dbname=postgres_db,
        user=postgres_user,
        password=postgres_password,
        host=postgres_host,
        port=postgres_port
    )
    return conn


def process_trades_dataframe(df):
    """Process the trades dataframe and insert into database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Prepare the query for batch execution
    insert_query = """
       SELECT upsert_capitol_trade(
           %s::VARCHAR, %s::VARCHAR, %s::VARCHAR, %s::VARCHAR, %s::DATE,
           %s::VARCHAR, %s::VARCHAR, %s::VARCHAR, 
           NULLIF(%s, 'N/A')::DECIMAL, %s::TIMESTAMP, %s::TIMESTAMP, %s::VARCHAR
       );
       """

    # Prepare data for batch insertion
    data = []


    for _, row in df.iterrows():
        # Convert stock price from string to decimal or None if N/A
        stock_price = row['Stock Price']  # Using index since we know the column position
        if stock_price == 'N/A':
            stock_price = 'N/A'
        else:
            stock_price = stock_price.replace('$', '')
            stock_price = stock_price.replace(',', '')

        # Format dates - assuming the format is 'DD MMM YYYY'
        row['Published Datetime'] = ' '.join(row['Published Datetime'].split(' ')[:3])

        trade_filed_date = pd.to_datetime(row['Trade Filed Date'],dayfirst=True).strftime('%Y-%m-%d')
        published_datetime = pd.to_datetime(row['Published Datetime'],dayfirst=True).strftime('%Y-%m-%d')
        traded_datetime = pd.to_datetime(row['Traded Datetime'],dayfirst=True).strftime('%Y-%m-%d')



        data.append((
            row['Politician'],  # Politician
            row['Party'],  # Party
            row['Traded Company Name'],  # Traded Company Name
            row['Traded Company Ticker'],  # Traded Company Ticker
            trade_filed_date,
            row['Trade Owner'],  # Trade Owner
            row['Trade Type'],  # Trade Type
            row['Trade Size'],  # Trade Size
            stock_price,
            published_datetime,
            traded_datetime,
            row['Trade ID']  # Trade ID
        ))

    try:
        # Execute batch insert
        execute_batch(cursor, insert_query, data, page_size=100)
        conn.commit()
        print(f"Successfully processed {len(data)} trades")

    except Exception as e:
        conn.rollback()
        print(f"Error occurred: {str(e)}")
        raise

    finally:
        cursor.close()
        conn.close()


def main():
    # Load the pickle file
    cleaned_trades_df = pd.read_pickle("cleaned_trades_df__01-18-25.pkl")

    # # Process the dataframe
    process_trades_dataframe(cleaned_trades_df)


if __name__ == "__main__":
    main()