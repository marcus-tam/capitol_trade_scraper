import pandas as pd
import os
import psycopg2


cleaned_trades_df = pd.DataFrame()

# Load PostgreSQL connection details from docker-compose.yml environment variables
postgres_user = os.getenv('POSTGRES_USER', 'myuser')
postgres_password = os.getenv('POSTGRES_PASSWORD', 'mypassword')
postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
postgres_port = os.getenv('POSTGRES_PORT', '5432')
postgres_db = os.getenv('POSTGRES_DB', 'mydb')

from sqlalchemy import create_engine

engine = create_engine(f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}")

cleaned_trades_df.to_sql('capitol_trades', engine, if_exists='replace', index=False)