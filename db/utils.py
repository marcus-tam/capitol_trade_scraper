import psycopg2

def connect():
    conn = psycopg2.connect(
        dbname="mydb",
        user="myuser",
        password="mypassword",
        host="localhost",
        port="5432"
    )

    return conn

def close(conn):
    conn.close()


def get_last_row():
    conn = connect()

    cursor = conn.cursor()

    query = """
    SELECT * FROM capitol_trades
    ORDER BY published_datetime DESC, id
    LIMIT 1;
    """
    cursor.execute(query)
    last_row = cursor.fetchone()

    cursor.close()

    close(conn)

    return last_row
