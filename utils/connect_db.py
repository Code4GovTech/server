import psycopg2,os

def connect_db():
    """Function to create and return database connection and cursor."""
    dbname = os.getenv('DB_NAME')
    user = os.getenv('DB_USER')
    host = os.getenv('DB_HOST')
    password = os.getenv('DB_PASSWORD')
    
    conn_str = f"dbname='{dbname}' user='{user}' host='{host}' password='{password}'"
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    return conn, cur