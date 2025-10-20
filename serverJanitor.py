import sqlite3
from datetime import datetime, timedelta

# === CONFIGURATION ===
DB_PATH = "trackingData.db"     # <-- Change this to your SQLite file path
TABLE_NAME = "tracking_data"   # <-- Change this to your table name
HISTORY_COLUMN = "history"       # <-- Change this to your history column name

# === MAIN SCRIPT ===
def main():
    conn = sqlite3.connect(DB_PATH, isolation_level="EXCLUSIVE")  # Lock DB for this session
    c = conn.cursor()

    # Start an exclusive transaction
    c.execute("BEGIN EXCLUSIVE TRANSACTION;")

    # Fetch all rows (adjust columns if needed)
    c.execute(f"SELECT rowid, {HISTORY_COLUMN} FROM {TABLE_NAME}")
    rows = c.fetchall()

    deleted_count = 0
    now = datetime.utcnow()
    cutoff = now - timedelta(days=3)

    for rowid, history in rows:
        if not history or not isinstance(history, str):
            continue

        # Split into non-empty lines
        lines = [line.strip() for line in history.splitlines() if line.strip()]
        if not lines:
            continue

        last_line = lines[-1]
        # Extract timestamp from the start of the last line
        timestamp_str = last_line.split(" | ", 1)[0].strip()

        try:
            timestamp = datetime.fromisoformat(timestamp_str)
        except ValueError:
            # Skip lines that don't start with valid timestamps
            continue

        if timestamp < cutoff:
            c.execute(f"DELETE FROM {TABLE_NAME} WHERE rowid = ?", (rowid,))
            deleted_count += 1

    conn.commit()
    conn.close()

    print(f"✅ Deleted {deleted_count} rows with last activity older than 3 days.")

if __name__ == "__main__":
    main()
