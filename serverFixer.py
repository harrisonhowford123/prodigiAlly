import sqlite3
from threading import Lock

DB_FILE = "trackingData.db"
db_lock = Lock()

def merge_tracking_duplicates():
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")  # safe for concurrent writes

        # Find isoBarcodes that have duplicates
        cursor.execute("""
            SELECT isoBarcode
            FROM tracking_data
            GROUP BY isoBarcode
            HAVING COUNT(*) > 1
        """)
        duplicates = [row[0] for row in cursor.fetchall()]
        print(f"Found {len(duplicates)} duplicate isoBarcodes.")

        for iso in duplicates:
            cursor.execute("""
                SELECT containerID, orderNumber, leadBarcode, history
                FROM tracking_data
                WHERE isoBarcode = ?
            """, (iso,))
            rows = cursor.fetchall()

            if not rows:
                continue

            # Merge fields
            containerID = next((r[0] for r in rows if r[0] is not None), None)
            orderNumber = next((r[1] for r in rows if r[1] is not None), None)
            leadBarcode = next((r[2] for r in rows if r[2] is not None), None)

            # Merge history, remove duplicate lines
            history_lines = []
            for r in rows:
                if r[3]:
                    for line in r[3].split("\n"):
                        if line not in history_lines:
                            history_lines.append(line)
            merged_history = "\n".join(history_lines)

            # Delete old rows
            cursor.execute("DELETE FROM tracking_data WHERE isoBarcode = ?", (iso,))

            # Insert merged row
            cursor.execute("""
                INSERT INTO tracking_data (isoBarcode, containerID, orderNumber, leadBarcode, history)
                VALUES (?, ?, ?, ?, ?)
            """, (iso, containerID, orderNumber, leadBarcode, merged_history))

            print(f"Merged isoBarcode {iso} into single entry.")

        conn.commit()
        conn.close()
        print("Merge complete.")

if __name__ == "__main__":
    merge_tracking_duplicates()
