import psycopg2
def db_connection():
    try:
        conn = psycopg2.connect(
            database = "mydb",
            user = "group14",
            password = "1234",
            host = "localhost",
            port = "5433"
        )
        print("Kết nối thành công")
        return conn
    except Exception as e:
        print(f"Lỗi kết nối {e}")
        return None