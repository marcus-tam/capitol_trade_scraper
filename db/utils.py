import psycopg2


class DatabaseConnector:
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.conn = None

    def connect(self):
        """Establish a database connection."""
        if self.conn is None:
            self.conn = psycopg2.connect(
                dbname=self.database,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
        return self

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def get_last_row(self):
        """Retrieve the last row from the capitol_trades table."""
        if self.conn is None:
            self.connect()

        cursor = self.conn.cursor()
        query = """
        SELECT * FROM capitol_trades
        ORDER BY published_datetime DESC, id
        LIMIT 1;
        """
        cursor.execute(query)
        last_row = cursor.fetchone()
        cursor.close()

        return last_row


"""
Usage:

# Example usage
if __name__ == "__main__":
    db = DatabaseConnector(host="localhost", database="mydb", user="myuser", password="mypassword", port=5432)
    db.connect()
    last_row = db.get_last_row()
    print("Last row:", last_row)
    db.close()

"""