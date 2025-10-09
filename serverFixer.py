import sqlite3
from threading import Lock

DB_FILE = "trackingData.db"
db_lock = Lock()

def add_itemNum_column():
    with db_lock:  # Lock the DB to prevent concurrent writes
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        try:
            # Add the itemNum column if it doesn't already exist
            cursor.execute("PRAGMA table_info(tracking_data)")
            columns = [row[1] for row in cursor.fetchall()]
            if "itemNum" not in columns:
                cursor.execute("ALTER TABLE tracking_data ADD COLUMN itemNum INTEGER")
                print("Column 'itemNum' added successfully.")
            else:
                print("Column 'itemNum' already exists.")
            conn.commit()
        except Exception as e:
            print(f"Error adding column: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    add_itemNum_column()
