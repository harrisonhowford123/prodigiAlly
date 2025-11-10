from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import urllib.parse
import json
import sqlite3
from threading import Lock, Thread
from datetime import datetime
from queue import Queue
import time
import traceback

HOST = "0.0.0.0"
PORT = 8080

# Database files
MAIN_DB_FILE = "prodigiAllyDatabase.db"
TRACKING_DB_FILE = "trackingData.db"

# Locks for main DB
db_lock_main = Lock()

# Queue for tracking DB write requests
tracking_queue = Queue()

# Debug flag - set to True for verbose logging
DEBUG = True

def debug_log(message):
    if DEBUG:
        print(f"[DEBUG {datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {message}")

# Initialize databases
def init_main_db():
    with sqlite3.connect(MAIN_DB_FILE) as conn:
        cursor = conn.cursor()
        
        # ---- Employee Info ----
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employee_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employeeName TEXT UNIQUE,
                password TEXT,
                hourlyRate REAL,
                start_time DATETIME,
                end_time DATETIME,
                loggedIn INTEGER DEFAULT 0
            )
        """)

        # ---- Facility Workstations ----
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facility_workstations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workstation TEXT UNIQUE,
                availableStations INTEGER,
                eligibleList TEXT
            )
        """)

        # ---- Production Processes ----
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productionProcesses (
                Product TEXT PRIMARY KEY,
                Processes TEXT
            )
        """)

        # ---- Product Codes ----
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_codes (
                prod_type TEXT PRIMARY KEY,
                worksheetRef TEXT
            )
        """)

        # ---- Employees Tasks ----
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS EmployeesTasks (
                employeeName TEXT NOT NULL,
                liveTask TEXT,
                status TEXT,
                isobarcode TEXT
            )
        """)

        # ---- Manual Tasks ----
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS manualTasks (
                task_names TEXT
            )
        """)

        conn.commit()


def init_tracking_db():
    with sqlite3.connect(TRACKING_DB_FILE) as conn:
        cursor = conn.cursor()

        # Create table if it doesn't exist (including new columns)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracking_data (
                containerID INTEGER,
                orderNumber TEXT,
                leadBarcode TEXT,
                isoBarcode TEXT UNIQUE,
                history TEXT,
                itemNum INTEGER,
                prodType TEXT,
                size TEXT
            )
        """)

        conn.commit()

init_main_db()
init_tracking_db()

# Worker thread for processing tracking DB queue
def tracking_worker():
    while True:
        if tracking_queue.empty():
            time.sleep(0.1)
            continue
        batch = []
        while not tracking_queue.empty():
            batch.append(tracking_queue.get())
        batch_start = datetime.now()
        debug_log(f"[QUEUE] Processing batch of {len(batch)} items")
        conn = sqlite3.connect(TRACKING_DB_FILE)
        cursor = conn.cursor()
        for job in batch:
            start_time = datetime.now()
            try:
                job(cursor)
            except Exception as e:
                debug_log(f"[QUEUE] Error processing job: {e}")
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            debug_log(f"[QUEUE] Finished job {job.__name__}, duration={duration:.4f}s")
        conn.commit()
        conn.close()
        batch_end = datetime.now()
        batch_duration = (batch_end - batch_start).total_seconds()
        debug_log(f"[QUEUE] Finished batch, duration={batch_duration:.4f}s")

Thread(target=tracking_worker, daemon=True).start()

class SimpleHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        debug_log(f"[HTTP] {self.address_string()} - {format%args}")

    def send_cors_headers(self):
        """Send CORS headers to allow cross-origin requests"""
        self.send_header("Access-Control-Allow-Origin", "https://pro.oneflowcloud.com")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
        self.send_header("Access-Control-Max-Age", "86400")

    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def enqueue_tracking_job(self, job_func):
        tracking_queue.put(job_func)
        debug_log(f"[QUEUE] Enqueued job {job_func.__name__}, queue size={tracking_queue.qsize()}")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({"status": "success", "queued": True}).encode("utf-8"))

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed_path.query)
        
        debug_log(f"[GET] Path: '{parsed_path.path}', Query: {query}")

        if parsed_path.path == "/api/employees":
            debug_log("[GET] Fetching employees")
            with db_lock_main:
                conn = sqlite3.connect(MAIN_DB_FILE)
                cursor = conn.cursor()
                cursor.execute("SELECT id, employeeName, password, hourlyRate FROM employee_info")
                rows = cursor.fetchall()
                conn.close()
            response = {
                "status": "success",
                "employees": [{"id": r[0], "employeeName": r[1], "password": r[2], "hourlyRate": r[3]} for r in rows]
            }
            debug_log(f"[GET] Returning {len(rows)} employees")

        elif parsed_path.path == "/api/manualTasks":
            debug_log("[GET] Fetching manual tasks")
            try:
                # No db_lock needed; simple read
                conn = sqlite3.connect(MAIN_DB_FILE, uri=True, timeout=5, check_same_thread=False)
                cursor = conn.cursor()
                cursor.execute("SELECT task_names FROM manualTasks")
                rows = cursor.fetchall()
                conn.close()

                # Extract task names as strings
                tasks = [r[0] for r in rows if r[0] is not None]

                response = {
                    "status": "success",
                    "tasks": tasks
                }
                debug_log(f"[GET] Returning {len(tasks)} manual tasks")
            except Exception as e:
                debug_log(f"[GET] Error fetching manual tasks: {e}")
                response = {
                    "status": "error",
                    "message": str(e)
                }

        elif parsed_path.path == "/api/employeesTasks":
            debug_log("[GET] Fetching employees tasks")
            try:
                conn = sqlite3.connect(MAIN_DB_FILE)
                cursor = conn.cursor()
                cursor.execute("SELECT employeeName, liveTask, status, isobarcode FROM EmployeesTasks")
                rows = cursor.fetchall()
                conn.close()

                # Convert to 2D list format - now includes isobarcode
                tasks_list = [[r[0], r[1], r[2], r[3]] for r in rows]

                response = {
                    "status": "success",
                    "tasks": tasks_list
                }
                debug_log(f"[GET] Returning {len(tasks_list)} employee tasks")

            except Exception as e:
                debug_log(f"[GET] Error fetching employees tasks: {e}")
                response = {
                    "status": "error",
                    "message": str(e)
                }

        elif parsed_path.path == "/api/pulseEmployees":
            debug_log("[GET] Fetching employees with Pulse access")
            try:
                with db_lock_main:
                    conn = sqlite3.connect(MAIN_DB_FILE)
                    cursor = conn.cursor()

                    # Select employees with non-null pulseAccess that contains 'Pulse'
                    cursor.execute("""
                        SELECT id, employeeName, password, pulseAccess
                        FROM employee_info
                        WHERE pulseAccess IS NOT NULL
                    """)
                    rows = cursor.fetchall()
                    conn.close()

                employees = []
                for r in rows:
                    # Safely parse pulseAccess JSON, default to empty list if invalid
                    try:
                        access_list = json.loads(r[3]) if r[3] else []
                    except Exception as e:
                        debug_log(f"Failed to parse pulseAccess for employee {r[1]}: {e}")
                        access_list = []

                    # Only include employees that actually have "Pulse" in the list
                    if "Pulse" in access_list:
                        employees.append({
                            "id": r[0],
                            "employeeName": r[1],
                            "password": r[2],
                            "pulseAccess": access_list
                        })

                response = {
                    "status": "success",
                    "employees": employees
                }
                debug_log(f"[GET] Returning {len(employees)} employees with Pulse access")

            except Exception as e:
                debug_log(f"[GET] Error fetching Pulse employees: {e}")
                response = {
                    "status": "error",
                    "message": str(e)
                }

        elif parsed_path.path == "/api/facilityWorkstations":
            debug_log("[GET] Fetching facility workstations")
            with db_lock_main:
                conn = sqlite3.connect(MAIN_DB_FILE)
                cursor = conn.cursor()
                cursor.execute("SELECT workstation, availableStations, eligibleList FROM facility_workstations")
                rows = cursor.fetchall()
                conn.close()

            workstations, availableStations, eligibleList = [], [], []

            for r in rows:
                ws_name = r[0] if r[0] is not None else ""
                workstations.append(ws_name)
                available = r[1] if r[1] is not None else ""
                availableStations.append(available)
                try:
                    eligible = json.loads(r[2]) if r[2] else []
                except (json.JSONDecodeError, TypeError):
                    eligible = []
                if not isinstance(eligible, (list, tuple)):
                    eligible = []
                eligibleList.append(eligible)

            response = {
                "status": "success",
                "workstations": workstations,
                "availableStations": availableStations,
                "eligibleList": eligibleList
            }
            debug_log(f"[GET] Returning {len(workstations)} workstations")

        elif parsed_path.path == "/api/nextContainerID":
            debug_log("[GET] Getting next container ID")
            conn = sqlite3.connect(TRACKING_DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tracking_data")
            total = cursor.fetchone()[0]
            if total == 0:
                next_id = 1
            else:
                cursor.execute("""
                    SELECT MIN(t1.containerID + 1) AS nextID
                    FROM tracking_data t1
                    LEFT JOIN tracking_data t2
                      ON t2.containerID = t1.containerID + 1
                    WHERE t2.containerID IS NULL
                """)
                row = cursor.fetchone()
                next_id = row[0] if row[0] else None
                if next_id is None:
                    cursor.execute("SELECT MAX(containerID) FROM tracking_data")
                    max_id = cursor.fetchone()[0]
                    next_id = (max_id or 0) + 1
            conn.close()
            response = {"status": "success", "nextContainerID": next_id}
            debug_log(f"[GET] Next container ID: {next_id}")

        elif parsed_path.path == "/api/orderTrack":
            debug_log("[GET] Order tracking request")

            # --- Parse query parameters ---
            containerID = query.get("containerID", [None])[0]
            orderNumber = query.get("orderNumber", [None])[0]
            isoBarcode = query.get("isoBarcode", [None])[0]
            leadBarcode = query.get("leadBarcode", [None])[0]
            workstation = query.get("workstation", [None])[0] or ""
            employeeName = query.get("employeeName", [None])[0] or ""

            # Item number and product type
            try:
                itemNum_str = query.get("itemNum", [None])[0]
                itemNum = int(itemNum_str) if itemNum_str is not None else None
                prodType = query.get("prodType", [None])[0] or None
            except Exception:
                itemNum = None
                prodType = None

            def job(cursor):
                nonlocal containerID, orderNumber, isoBarcode, leadBarcode, workstation, employeeName, itemNum, prodType

                # Normalize containerID to int
                if containerID is not None:
                    try:
                        containerID = int(containerID)
                    except ValueError:
                        containerID = None

                # Create history entry
                new_history_entry = f"{datetime.now().replace(second=0, microsecond=0).isoformat()} | {workstation} | {employeeName}"

                # --- Helper: append history ---
                def append_history(existing_history, new_line):
                    if not existing_history or existing_history.strip() == "":
                        return new_line
                    lines = existing_history.strip().split("\n")

                    def strip_timestamp(line):
                        parts = line.split(" | ", 1)
                        return parts[1] if len(parts) > 1 else line

                    if strip_timestamp(lines[-1]) != strip_timestamp(new_line):
                        lines.append(new_line)
                    return "\n".join(lines)

                # --- ISO barcode branch ---
                if isoBarcode:
                    debug_log(f"[ISO] Processing isoBarcode={isoBarcode}")
                    cursor.execute(
                        "SELECT containerID, orderNumber, leadBarcode, history FROM tracking_data WHERE isoBarcode = ?",
                        (isoBarcode,)
                    )
                    row = cursor.fetchone()

                    if row:
                        # Exact isoBarcode match
                        debug_log(f"[ISO] Found existing row for isoBarcode={isoBarcode}")
                        container_existing, orderNumber_existing, lead_existing, history_existing = row
                        container_to_use = containerID if containerID is not None else container_existing
                        order_to_use = orderNumber if orderNumber else orderNumber_existing
                        lead_to_use = leadBarcode if leadBarcode else lead_existing
                        updated_history = append_history(history_existing, new_history_entry)

                        cursor.execute("""
                            UPDATE tracking_data
                            SET history = ?, containerID = ?, orderNumber = ?, leadBarcode = ?, prodType = ?
                            WHERE isoBarcode = ?
                        """, (updated_history, container_to_use, order_to_use, lead_to_use, prodType, isoBarcode))
                        debug_log(f"[ISO] Updated row for isoBarcode={isoBarcode}")

                    else:
                        # No isoBarcode match → try orderNumber match
                        debug_log(f"[ISO] No existing row for isoBarcode={isoBarcode}, trying orderNumber match")
                        cursor.execute("""
                            SELECT rowid, prodType, containerID, leadBarcode, history
                            FROM tracking_data
                            WHERE orderNumber = ? AND isoBarcode IS NULL
                        """, (orderNumber,))
                        rows = cursor.fetchall()

                        # Step 1: Find row with matching prodType
                        matching_row = next((r for r in rows if r[1] == prodType), None)

                        if matching_row:
                            rowid, _, container_existing, lead_existing, history_existing = matching_row
                            debug_log(f"[ISO] Found row with matching prodType for orderNumber={orderNumber}")

                        else:
                            # Step 2: Fallback to row where prodType is NULL
                            null_prod_row = next((r for r in rows if r[1] is None), None)
                            if null_prod_row:
                                rowid, _, container_existing, lead_existing, history_existing = null_prod_row
                                debug_log(f"[ISO] Using row with NULL prodType for orderNumber={orderNumber}")
                            else:
                                # Step 3: No suitable row → insert new
                                rowid = None
                                debug_log(f"[ISO] No matching or NULL prodType row, inserting new for orderNumber={orderNumber}")

                        if rowid:
                            # Update the chosen row
                            container_to_use = containerID if containerID is not None else container_existing
                            lead_to_use = leadBarcode if leadBarcode else lead_existing
                            updated_history = append_history(history_existing, new_history_entry)

                            cursor.execute("""
                                UPDATE tracking_data
                                SET containerID = ?, leadBarcode = ?, isoBarcode = ?, history = ?, prodType = ?
                                WHERE rowid = ?
                            """, (container_to_use, lead_to_use, isoBarcode, updated_history, prodType, rowid))
                            debug_log(f"[ISO] Updated row for isoBarcode={isoBarcode}")
                        else:
                            # Insert new row
                            cursor.execute("""
                                INSERT INTO tracking_data (containerID, orderNumber, leadBarcode, isoBarcode, history, prodType)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (containerID, orderNumber, leadBarcode, isoBarcode, new_history_entry, prodType))
                            debug_log(f"[ISO] Inserted new row for isoBarcode={isoBarcode}")

            
                # --- Lead barcode branch ---
                if leadBarcode:
                    debug_log(f"[Lead] Processing leadBarcode={leadBarcode}")
                    cursor.execute(
                        "SELECT isoBarcode, containerID, orderNumber, history FROM tracking_data WHERE leadBarcode = ?",
                        (leadBarcode,)
                    )
                    rows = cursor.fetchall()
                    for iso, container_existing, order_existing, history_existing in rows:
                        container_to_use = containerID if containerID is not None else container_existing
                        order_to_use = orderNumber if orderNumber else order_existing
                        updated_history = append_history(history_existing, new_history_entry)
                        cursor.execute(
                            "UPDATE tracking_data SET history = ?, containerID = ?, orderNumber = ? WHERE isoBarcode = ?",
                            (updated_history, container_to_use, order_to_use, iso)
                        )
                        debug_log(f"[Lead] Updated row for isoBarcode={iso}")

                # --- Order-number-only branch ---
                if not isoBarcode and not leadBarcode and containerID:
                    debug_log(f"[OrderOnly] Processing orderNumber={orderNumber}")

                    # --- Step 0: Normalize prodType ---
                    try:
                        with sqlite3.connect(MAIN_DB_FILE, uri=True, timeout=5, check_same_thread=False) as conn_readonly:
                            conn_readonly.execute("PRAGMA query_only = 1")  # Read-only mode
                            cursor_readonly = conn_readonly.cursor()
                            cursor_readonly.execute("""
                                SELECT worksheetRef
                                FROM product_codes
                                WHERE prod_type = ?
                                LIMIT 1
                            """, (prodType,))
                            result = cursor_readonly.fetchone()
                            if result and result[0] is not None:
                                old_prodType = prodType
                                prodType = result[0]  # Replace with worksheetRef
                                debug_log(f"[OrderOnly] Normalized prodType '{old_prodType}' -> '{prodType}'")
                            else:
                                # --- Step 0b: Log missing prodType before setting to None ---
                                if prodType:
                                    try:
                                        existing_lines = set()
                                        try:
                                            with open("missing_prodTypes.txt", "r", encoding="utf-8") as f:
                                                existing_lines = set(line.strip() for line in f if line.strip())
                                        except FileNotFoundError:
                                            pass  # file doesn't exist yet

                                        if prodType not in existing_lines:
                                            with open("missing_prodTypes.txt", "a", encoding="utf-8") as f:
                                                f.write(prodType + "\n")
                                            debug_log(f"[OrderOnly] Logged missing prodType: '{prodType}'")
                                    except Exception as e:
                                        debug_log(f"[OrderOnly] Failed to log missing prodType '{prodType}': {e}")

                                prodType = None
                                debug_log(f"[OrderOnly] prodType not found in product_codes, set to None")
                    except Exception as e:
                        debug_log(f"[OrderOnly] Failed to normalize prodType '{prodType}': {e}")
                        prodType = None

                    # --- Step 1: Find rows with orderNumber and itemNum IS NULL ---
                    cursor.execute("""
                        SELECT rowid, prodType, history
                        FROM tracking_data
                        WHERE orderNumber = ? AND itemNum IS NULL
                    """, (orderNumber,))
                    rows = cursor.fetchall()

                    if rows:
                        # Step 2: Check for a row with matching prodType
                        matching_row = next((r for r in rows if r[1] == prodType), None)
                        if matching_row:
                            rowid, _, history_existing = matching_row
                            updated_history = append_history(history_existing, new_history_entry)
                            if prodType is not None:
                                cursor.execute("""
                                    UPDATE tracking_data
                                    SET containerID = ?, itemNum = ?, history = ?, prodType = ?
                                    WHERE rowid = ?
                                """, (containerID, itemNum, updated_history, prodType, rowid))
                            else:
                                cursor.execute("""
                                    UPDATE tracking_data
                                    SET containerID = ?, itemNum = ?, history = ?
                                    WHERE rowid = ?
                                """, (containerID, itemNum, updated_history, rowid))
                            cursor.connection.commit()
                            debug_log(f"[OrderOnly] Updated row with matching prodType for orderNumber={orderNumber}")
                        else:
                            # Step 3: Update first row with differing prodType
                            differing_row = rows[0]
                            rowid, _, history_existing = differing_row
                            updated_history = append_history(history_existing, new_history_entry)
                            if prodType is not None:
                                cursor.execute("""
                                    UPDATE tracking_data
                                    SET containerID = ?, itemNum = ?, history = ?, prodType = ?
                                    WHERE rowid = ?
                                """, (containerID, itemNum, updated_history, prodType, rowid))
                            else:
                                cursor.execute("""
                                    UPDATE tracking_data
                                    SET containerID = ?, itemNum = ?, history = ?
                                    WHERE rowid = ?
                                """, (containerID, itemNum, updated_history, rowid))
                            cursor.connection.commit()
                            debug_log(f"[OrderOnly] Updated row with differing prodType for orderNumber={orderNumber}")
                    else:
                        # Step 4: Insert new row
                        if prodType is not None:
                            cursor.execute("""
                                INSERT INTO tracking_data (containerID, orderNumber, itemNum, prodType, history)
                                VALUES (?, ?, ?, ?, ?)
                            """, (containerID, orderNumber, itemNum, prodType, new_history_entry))
                        else:
                            cursor.execute("""
                                INSERT INTO tracking_data (containerID, orderNumber, itemNum, history)
                                VALUES (?, ?, ?, ?)
                            """, (containerID, orderNumber, itemNum, new_history_entry))
                        cursor.connection.commit()
                        debug_log(f"[OrderOnly] Inserted new row for orderNumber={orderNumber}")

            self.enqueue_tracking_job(job)
            return

        elif parsed_path.path == "/api/receivePrintData":
            debug_log("[GET] Print data received")

            # --- Parse query parameters ---
            containerID = query.get("containerID", [None])[0]
            orderNumber = query.get("orderNumber", [None])[0]
            leadBarcode = query.get("leadBarcode", [None])[0]
            isoBarcode = query.get("isoBarcode", [None])[0]
            workstation = query.get("workstation", [None])[0] or ""
            employeeName = query.get("employeeName", [None])[0] or ""
            prodType = query.get("prodType", [None])[0] or None
            size = query.get("size", [None])[0] or None
            itemNum = query.get("itemNum", [None])[0] or None

            debug_log(f"[RECEIVE] containerID={containerID}, orderNumber={orderNumber}, leadBarcode={leadBarcode}, isoBarcode={isoBarcode}, prodType={prodType}, size={size}, itemNum={itemNum}")

            def job(cursor):
                nonlocal isoBarcode, workstation, employeeName, containerID, orderNumber, leadBarcode, prodType, size, itemNum

                # Create history entry (copied from orderTrack logic)
                new_history_entry = f"{datetime.now().replace(second=0, microsecond=0).isoformat()} | {workstation} | {employeeName}"

                def append_history(existing_history, new_line):
                    if not existing_history or existing_history.strip() == "":
                        return new_line
                    lines = existing_history.strip().split("\n")

                    def strip_timestamp(line):
                        parts = line.split(" | ", 1)
                        return parts[1] if len(parts) > 1 else line

                    if strip_timestamp(lines[-1]) != strip_timestamp(new_line):
                        lines.append(new_line)
                    return "\n".join(lines)

                # --- If containerID is provided, update matching order with NULL containerID ---
                if containerID is not None and orderNumber is not None:
                    cursor.execute(
                        """
                        SELECT rowid, history FROM tracking_data
                        WHERE orderNumber = ? AND containerID IS NULL
                        ORDER BY rowid ASC LIMIT 1
                        """,
                        (orderNumber,)
                    )
                    row = cursor.fetchone()

                    if row:
                        rowid, history_existing = row
                        updated_history = append_history(history_existing, new_history_entry)

                        cursor.execute(
                            """
                            UPDATE tracking_data
                            SET containerID = ?, itemNum = ?, history = ?
                            WHERE rowid = ?
                            """,
                            (containerID, itemNum, updated_history, rowid)
                        )
                        debug_log(f"[RECEIVE] Attached containerID={containerID} and itemNum={itemNum} to existing order={orderNumber}.")
                        return
                    else:
                        # Create new row if no matching order with NULL containerID
                        cursor.execute(
                            """
                            INSERT INTO tracking_data (containerID, orderNumber, itemNum, history)
                            VALUES (?, ?, ?, ?)
                            """,
                            (containerID, orderNumber, itemNum, new_history_entry)
                        )
                        debug_log(f"[RECEIVE] Created new row for orderNumber={orderNumber} with containerID={containerID} and itemNum={itemNum}.")
                        return

                if isoBarcode:
                    cursor.execute("SELECT containerID, orderNumber, leadBarcode, prodType, size, history FROM tracking_data WHERE isoBarcode = ?", (isoBarcode,))
                    existing = cursor.fetchone()

                    if existing:
                        container_existing, order_existing, lead_existing, prod_existing, size_existing, history_existing = existing
                        updated_history = append_history(history_existing, new_history_entry)

                        # Preserve existing containerID if new one is None
                        container_to_use = containerID if containerID is not None else container_existing
                        order_to_use = orderNumber if orderNumber else order_existing
                        lead_to_use = leadBarcode if leadBarcode else lead_existing
                        prod_to_use = prodType if prodType else prod_existing
                        size_to_use = size if size else size_existing

                        cursor.execute(
                            """
                            UPDATE tracking_data
                            SET history = ?, containerID = ?, orderNumber = ?, leadBarcode = ?, prodType = ?, size = ?
                            WHERE isoBarcode = ?
                            """,
                            (updated_history, container_to_use, order_to_use, lead_to_use, prod_to_use, size_to_use, isoBarcode)
                        )
                        debug_log(f"[RECEIVE] Updated row for isoBarcode={isoBarcode} with preserved existing values when new ones are missing.")
                    else:
                        # Insert new row if ISO does not exist
                        cursor.execute(
                            """
                            INSERT INTO tracking_data (containerID, orderNumber, leadBarcode, isoBarcode, prodType, size, history)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            """,
                            (containerID, orderNumber, leadBarcode, isoBarcode, prodType, size, new_history_entry)
                        )
                        debug_log(f"[RECEIVE] Inserted new row for isoBarcode={isoBarcode}.")

            self.enqueue_tracking_job(job)
            return



        elif parsed_path.path == "/api/moveContainer":
            debug_log("[GET] Move container request")
            isoBarcode = query.get("isoBarcode", [None])[0]
            leadBarcode = query.get("leadBarcode", [None])[0]
            workstation = query.get("workstation", [None])[0] or ""
            employeeName = query.get("employeeName", [None])[0] or ""

            def job(cursor):
                new_history_entry = f"{datetime.now().replace(second=0, microsecond=0).isoformat()} | {workstation} | {employeeName}"
                def append_history(existing_history, new_line):
                    if not existing_history or existing_history.strip() == "":
                        return new_line
                    lines = existing_history.strip().split("\n")
                    def strip_timestamp(line):
                        parts = line.split(" | ", 1)
                        return parts[1] if len(parts) > 1 else line
                    if strip_timestamp(lines[-1]) != strip_timestamp(new_line):
                        lines.append(new_line)
                    return "\n".join(lines)

                containerID = None
                if isoBarcode:
                    cursor.execute("SELECT containerID FROM tracking_data WHERE isoBarcode = ?", (isoBarcode,))
                    row = cursor.fetchone()
                    if row:
                        containerID = row[0]
                if not containerID and leadBarcode:
                    cursor.execute("SELECT containerID FROM tracking_data WHERE leadBarcode = ?", (leadBarcode,))
                    row = cursor.fetchone()
                    if row:
                        containerID = row[0]

                if containerID:
                    cursor.execute("SELECT isoBarcode, history FROM tracking_data WHERE containerID = ?", (containerID,))
                    rows = cursor.fetchall()
                    for iso, history_existing in rows:
                        updated_history = append_history(history_existing, new_history_entry)
                        cursor.execute("UPDATE tracking_data SET history = ? WHERE isoBarcode = ?", (updated_history, iso))

            self.enqueue_tracking_job(job)
            return

        elif parsed_path.path == "/api/fetchProdCodes":
            debug_log("[GET] Fetching product codes")
            try:
                with db_lock_main:
                    conn = sqlite3.connect(MAIN_DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("SELECT prod_type FROM product_codes")
                    rows = cursor.fetchall()
                    conn.close()

                prod_codes = [r[0] for r in rows]
                response = {"status": "success", "prodCodes": prod_codes}

                debug_log(f"[GET] Returning {len(prod_codes)} product codes")

            except Exception as e:
                debug_log(f"[GET] ERROR in fetchProdCodes: {e}")
                response = {"status": "error", "message": str(e)}

        else:
            debug_log(f"[GET] 404 - Unknown path: '{parsed_path.path}'")
            self.send_response(404)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(b"Request Not Found")
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(response).encode("utf-8"))

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        debug_log(f"[POST] ============ NEW POST REQUEST ============")
        debug_log(f"[POST] Path: '{parsed_path.path}'")
        debug_log(f"[POST] Headers: {dict(self.headers)}")
        
        content_length = int(self.headers.get('Content-Length', 0))
        debug_log(f"[POST] Content-Length: {content_length}")
        
        if content_length == 0:
            debug_log("[POST] ERROR: No body data")
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": "No data provided"}).encode("utf-8"))
            return
        
        post_data = self.rfile.read(content_length)
        debug_log(f"[POST] Raw body: {post_data}")
        
        try:
            data = json.loads(post_data)
            debug_log(f"[POST] Parsed JSON: {data}")
        except Exception as e:
            debug_log(f"[POST] ERROR: Failed to parse JSON - {e}")
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": f"Invalid JSON: {str(e)}"}).encode("utf-8"))
            return

        debug_log(f"[POST] Starting path matching...")

        if parsed_path.path == "/api/addOrUpdateEmployee":
            debug_log("[POST] Matched: /api/addOrUpdateEmployee")
            employee_name = data.get("employeeName")
            password = data.get("password")
            hourly_rate = data.get("hourlyRate")
            workstation_list = data.get("workstations", [])

            if not employee_name:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": "employeeName is required"}).encode("utf-8"))
                return

            try:
                with db_lock_main:
                    conn = sqlite3.connect(MAIN_DB_FILE)
                    cursor = conn.cursor()

                    cursor.execute("SELECT id FROM employee_info WHERE employeeName = ?", (employee_name,))
                    row = cursor.fetchone()
                    if row:
                        update_fields = []
                        params = []
                        if password is not None:
                            update_fields.append("password = ?")
                            params.append(password)
                        if hourly_rate is not None:
                            update_fields.append("hourlyRate = ?")
                            params.append(hourly_rate)
                        if update_fields:
                            sql = f"UPDATE employee_info SET {', '.join(update_fields)} WHERE employeeName = ?"
                            params.append(employee_name)
                            cursor.execute(sql, tuple(params))
                    else:
                        cursor.execute(
                            "INSERT INTO employee_info (employeeName, password, hourlyRate) VALUES (?, ?, ?)",
                            (employee_name, password, hourly_rate)
                        )

                    if workstation_list:
                        cursor.execute("SELECT id, workstation, eligibleList FROM facility_workstations")
                        rows = cursor.fetchall()
                        for row_id, workstation_name, eligible_json in rows:
                            if workstation_name in workstation_list:
                                try:
                                    eligible_list = json.loads(eligible_json) if eligible_json else []
                                except json.JSONDecodeError:
                                    eligible_list = []
                                if employee_name not in eligible_list:
                                    eligible_list.append(employee_name)
                                    cursor.execute(
                                        "UPDATE facility_workstations SET eligibleList = ? WHERE id = ?",
                                        (json.dumps(eligible_list), row_id)
                                    )

                    conn.commit()
                    conn.close()

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "message": f"Employee '{employee_name}' added/updated"}).encode("utf-8"))
                return

            except Exception as e:
                debug_log(f"[POST] ERROR in addOrUpdateEmployee: {e}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
                return

        elif parsed_path.path == "/api/updateEmployeeTask":
            debug_log("[POST] Matched: /api/updateEmployeeTask")
            
            employee_name = data.get("employeeName")
            live_task = data.get("liveTask")
            status = data.get("status")
            isobarcode = data.get("isobarcode")
            erase = data.get("erase", False)

            if not employee_name:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": "employeeName is required"
                }).encode("utf-8"))
                return

            try:
                with db_lock_main:
                    conn = sqlite3.connect(MAIN_DB_FILE)
                    cursor = conn.cursor()

                    if erase:
                        if live_task:
                            # Delete ONLY the first matching task for this employee
                            cursor.execute("""
                                DELETE FROM EmployeesTasks 
                                WHERE rowid = (
                                    SELECT rowid FROM EmployeesTasks 
                                    WHERE employeeName = ? AND liveTask = ? 
                                    LIMIT 1
                                )
                            """, (employee_name, live_task))
                            debug_log(f"[POST] Deleted one task for employee '{employee_name}': {live_task}")
                            message = f"Task deleted for employee '{employee_name}'"
                        else:
                            # Delete ALL tasks for this employee (if no liveTask specified)
                            cursor.execute(
                                "DELETE FROM EmployeesTasks WHERE employeeName = ?",
                                (employee_name,)
                            )
                            debug_log(f"[POST] Deleted all tasks for employee '{employee_name}'")
                            message = f"All tasks deleted for employee '{employee_name}'"
                    else:
                        # Check if task exists with matching isobarcode
                        if isobarcode:
                            cursor.execute("""
                                SELECT rowid FROM EmployeesTasks 
                                WHERE isobarcode = ?
                            """, (isobarcode,))
                            existing_row = cursor.fetchone()
                            
                            if existing_row:
                                # UPDATE existing task (regardless of employee)
                                cursor.execute("""
                                    UPDATE EmployeesTasks 
                                    SET employeeName = ?, liveTask = ?, status = ?
                                    WHERE isobarcode = ?
                                """, (employee_name, live_task, status, isobarcode))
                                debug_log(f"[POST] Updated task with barcode {isobarcode}: employee={employee_name}, task={live_task}, status={status}")
                                message = f"Task updated for barcode {isobarcode}"
                            else:
                                # INSERT new task
                                cursor.execute(
                                    "INSERT INTO EmployeesTasks (employeeName, liveTask, status, isobarcode) VALUES (?, ?, ?, ?)",
                                    (employee_name, live_task, status, isobarcode)
                                )
                                debug_log(f"[POST] Inserted new task for employee '{employee_name}': {live_task} | Barcode: {isobarcode}")
                                message = f"Task created for employee '{employee_name}'"

                        else:
                            # No isobarcode provided - always INSERT
                            cursor.execute(
                                "INSERT INTO EmployeesTasks (employeeName, liveTask, status, isobarcode) VALUES (?, ?, ?, ?)",
                                (employee_name, live_task, status, isobarcode)
                            )
                            debug_log(f"[POST] Inserted new task for employee '{employee_name}': {live_task}")
                            message = f"Task created for employee '{employee_name}'"

                    conn.commit()
                    conn.close()

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "success",
                    "message": message
                }).encode("utf-8"))
                return

            except Exception as e:
                debug_log(f"[POST] ERROR in updateEmployeeTask: {e}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": str(e)
                }).encode("utf-8"))
                return

        elif parsed_path.path == "/api/loggedin":
            debug_log("[POST] Matched: /api/loggedin")
            debug_log(f"[POST] Data keys: {list(data.keys())}")
            
            employee_name = data.get("employeeName")
            debug_log(f"[POST] Employee name: '{employee_name}'")
            
            if not employee_name:
                debug_log("[POST] ERROR: No employeeName in request")
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": "employeeName is required"
                }).encode("utf-8"))
                return

            try:
                with db_lock_main:
                    conn = sqlite3.connect(MAIN_DB_FILE)
                    cursor = conn.cursor()

                    debug_log(f"[POST] Checking if employee '{employee_name}' exists...")
                    cursor.execute("SELECT id FROM employee_info WHERE employeeName = ?", (employee_name,))
                    row = cursor.fetchone()
                    
                    if not row:
                        conn.close()
                        debug_log(f"[POST] Employee '{employee_name}' not found in database")
                        self.send_response(404)
                        self.send_header("Content-Type", "application/json")
                        self.send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            "status": "error",
                            "message": f"Employee '{employee_name}' not found"
                        }).encode("utf-8"))
                        return

                    debug_log(f"[POST] Employee found with ID: {row[0]}")
                    debug_log(f"[POST] Updating loggedIn to 1 for '{employee_name}'")
                    
                    cursor.execute(
                        "UPDATE employee_info SET loggedIn = 1 WHERE employeeName = ?",
                        (employee_name,)
                    )
                    conn.commit()
                    conn.close()
                    
                    debug_log(f"[POST] Successfully logged in '{employee_name}'")

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "success",
                    "message": f"Employee '{employee_name}' logged in successfully"
                }).encode("utf-8"))
                return

            except Exception as e:
                debug_log(f"[POST] ERROR in loggedin: {e}")
                debug_log(f"[POST] Traceback: {traceback.format_exc()}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": f"Internal server error: {str(e)}"
                }).encode("utf-8"))
                return

        elif parsed_path.path == "/api/editTasks":
            debug_log("[POST] Matched: /api/editTasks")
            
            task_name = data.get("taskName")
            edit_flag = data.get("editFlag")

            if not task_name or not isinstance(edit_flag, bool):
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": "taskName (string) and editFlag (boolean) are required"
                }).encode("utf-8"))
                return

            try:
                with db_lock_main:
                    conn = sqlite3.connect(MAIN_DB_FILE)
                    cursor = conn.cursor()

                    if edit_flag:  # Add task if not exists
                        cursor.execute("SELECT 1 FROM manualTasks WHERE task_names = ?", (task_name,))
                        if not cursor.fetchone():
                            cursor.execute("INSERT INTO manualTasks (task_names) VALUES (?)", (task_name,))
                            debug_log(f"[POST] Added new task: {task_name}")
                        else:
                            debug_log(f"[POST] Task '{task_name}' already exists, skipping insert")
                    else:  # Delete task if exists
                        cursor.execute("DELETE FROM manualTasks WHERE task_names = ?", (task_name,))
                        debug_log(f"[POST] Deleted task: {task_name}")

                    conn.commit()
                    conn.close()

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "success",
                    "message": f"Task '{task_name}' {'added' if edit_flag else 'deleted'} successfully"
                }).encode("utf-8"))
                return

            except Exception as e:
                debug_log(f"[POST] ERROR in editTasks: {e}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": f"Internal server error: {str(e)}"
                }).encode("utf-8"))
                return


        elif parsed_path.path == "/api/loggedOut":
            debug_log("[POST] Matched: /api/loggedOut")
            employee_name = data.get("employeeName")
            
            if not employee_name:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": "employeeName is required"}).encode("utf-8"))
                return

            try:
                with db_lock_main:
                    conn = sqlite3.connect(MAIN_DB_FILE)
                    cursor = conn.cursor()
                    
                    debug_log(f"[POST] Checking if employee '{employee_name}' exists...")
                    cursor.execute("SELECT id FROM employee_info WHERE employeeName = ?", (employee_name,))
                    row = cursor.fetchone()
                    
                    if not row:
                        conn.close()
                        debug_log(f"[POST] Employee '{employee_name}' not found")
                        response = {"status": "error", "message": f"Employee '{employee_name}' not found"}
                    else:
                        debug_log(f"[POST] Updating loggedIn to 0 for '{employee_name}'")
                        cursor.execute(
                            "UPDATE employee_info SET loggedIn = 0 WHERE employeeName = ?",
                            (employee_name,)
                        )
                        conn.commit()
                        conn.close()
                        response = {"status": "success", "message": f"Employee '{employee_name}' logged out successfully"}
                        debug_log(f"[POST] Successfully logged out '{employee_name}'")

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(response).encode("utf-8"))
                return

            except Exception as e:
                debug_log(f"[POST] ERROR in loggedOut: {e}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
                return

        elif parsed_path.path == "/api/getEmployeeStartTime":
            debug_log("[POST] Matched: /api/getEmployeeStartTime")
            employee_name = data.get("employeeName")
            
            if not employee_name:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": "No employeeName provided"
                }).encode("utf-8"))
                return

            try:
                with db_lock_main:
                    conn = sqlite3.connect(MAIN_DB_FILE)
                    cursor = conn.cursor()

                    cursor.execute(
                        "SELECT start_time FROM employee_info WHERE employeeName = ?",
                        (employee_name,)
                    )
                    row = cursor.fetchone()
                    conn.close()

                if row and row[0]:
                    response = {"status": "success", "start_time": row[0]}
                elif row:
                    response = {"status": "success", "start_time": None}
                else:
                    response = {"status": "error", "message": f"Employee '{employee_name}' not found"}

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(response).encode("utf-8"))
                return

            except Exception as e:
                debug_log(f"[POST] ERROR in getEmployeeStartTime: {e}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
                return

        elif parsed_path.path == "/api/logEmployeeTime":
            debug_log("[POST] Matched: /api/logEmployeeTime")
            employee_name = data.get("employeeName")
            start_time_str = data.get("start_time")
            end_time_str = data.get("end_time")

            if not employee_name or not start_time_str or not end_time_str:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": "employeeName, start_time, and end_time are required"
                }).encode("utf-8"))
                return

            try:
                start_dt = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
                end_dt = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": "start_time and end_time must be in 'YYYY-MM-DD HH:MM:SS' format"
                }).encode("utf-8"))
                return

            try:
                with db_lock_main:
                    conn = sqlite3.connect(MAIN_DB_FILE)
                    cursor = conn.cursor()

                    cursor.execute("SELECT id FROM employee_info WHERE employeeName = ?", (employee_name,))
                    row = cursor.fetchone()
                    if row:
                        cursor.execute(
                            "UPDATE employee_info SET start_time = ?, end_time = ? WHERE employeeName = ?",
                            (start_time_str, end_time_str, employee_name)
                        )
                        conn.commit()
                        response = {"status": "success", "message": f"Updated '{employee_name}' start and end times"}
                    else:
                        response = {"status": "error", "message": f"Employee '{employee_name}' not found"}

                    conn.close()

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(response).encode("utf-8"))

            except Exception as e:
                debug_log(f"[POST] ERROR in logEmployeeTime: {e}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
            
        elif parsed_path.path == "/api/removeWorkstation":
            debug_log("[POST] Matched: /api/removeWorkstation")
            employee_name = data.get("employeeName")
            workstation_name = data.get("workstationName")

            if not employee_name or not workstation_name:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": "Both employeeName and workstationName are required"
                }).encode("utf-8"))
                return

            try:
                with db_lock_main:
                    conn = sqlite3.connect(MAIN_DB_FILE)
                    cursor = conn.cursor()

                    cursor.execute(
                        "SELECT id, eligibleList FROM facility_workstations WHERE workstation = ?",
                        (workstation_name,)
                    )
                    row = cursor.fetchone()
                    if row:
                        row_id, eligible_json = row
                        try:
                            eligible_list = json.loads(eligible_json) if eligible_json else []
                        except json.JSONDecodeError:
                            eligible_list = []

                        if employee_name in eligible_list:
                            eligible_list.remove(employee_name)
                            cursor.execute(
                                "UPDATE facility_workstations SET eligibleList = ? WHERE id = ?",
                                (json.dumps(eligible_list), row_id)
                            )
                            conn.commit()
                            response = {
                                "status": "success",
                                "message": f"Employee '{employee_name}' removed from '{workstation_name}'"
                            }
                        else:
                            response = {
                                "status": "success",
                                "message": f"Employee '{employee_name}' was not assigned to '{workstation_name}'"
                            }
                    else:
                        response = {
                            "status": "error",
                            "message": f"Workstation '{workstation_name}' not found"
                        }

                    conn.close()

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(response).encode("utf-8"))
                return

            except Exception as e:
                debug_log(f"[POST] ERROR in removeWorkstation: {e}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": str(e)
                }).encode("utf-8"))
                return

        elif parsed_path.path == "/api/removeEmployee":
            debug_log("[POST] Matched: /api/removeEmployee")
            employee_name = data.get("employeeName")

            if not employee_name:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": "No employee name provided"}).encode("utf-8"))
                return

            try:
                with db_lock_main:
                    conn = sqlite3.connect(MAIN_DB_FILE)
                    cursor = conn.cursor()

                    cursor.execute("DELETE FROM employee_info WHERE employeeName = ?", (employee_name,))

                    cursor.execute("SELECT id, eligibleList FROM facility_workstations")
                    rows = cursor.fetchall()
                    for row_id, eligible_json in rows:
                        if eligible_json:
                            try:
                                eligible_list = json.loads(eligible_json)
                            except json.JSONDecodeError:
                                eligible_list = []
                            if employee_name in eligible_list:
                                eligible_list.remove(employee_name)
                                cursor.execute(
                                    "UPDATE facility_workstations SET eligibleList = ? WHERE id = ?",
                                    (json.dumps(eligible_list), row_id)
                                )

                    conn.commit()
                    conn.close()

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "message": f"Employee '{employee_name}' removed"}).encode("utf-8"))
                return

            except Exception as e:
                debug_log(f"[POST] ERROR in removeEmployee: {e}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
                return

        elif parsed_path.path == "/api/getEmployeeLoginState":
            debug_log("[POST] Matched: /api/getEmployeeLoginState")

            employee_name = data.get("employeeName")

            if not employee_name:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": "employeeName is required"
                }).encode("utf-8"))
                return

            try:
                with db_lock_main:
                    conn = sqlite3.connect(MAIN_DB_FILE)
                    cursor = conn.cursor()

                    cursor.execute(
                        "SELECT loggedIn FROM employee_info WHERE employeeName = ?",
                        (employee_name,)
                    )
                    row = cursor.fetchone()
                    conn.close()

                if row is None:
                    debug_log(f"[POST] Employee '{employee_name}' not found")
                    self.send_response(404)
                    self.send_header("Content-Type", "application/json")
                    self.send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "status": "error",
                        "message": f"Employee '{employee_name}' not found"
                    }).encode("utf-8"))
                    return

                logged_in_state = row[0]
                debug_log(f"[POST] Employee '{employee_name}' loggedIn={logged_in_state}")

                response = {
                    "status": "success",
                    "employeeName": employee_name,
                    "loggedIn": bool(logged_in_state)
                }

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(response).encode("utf-8"))
                return

            except Exception as e:
                debug_log(f"[POST] ERROR in getEmployeeLoginState: {e}")
                debug_log(traceback.format_exc())
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": str(e)
                }).encode("utf-8"))
                return

        elif parsed_path.path == "/api/getTrackingHistory":
            debug_log("[POST] Matched: /api/getTrackingHistory")

            order_number = data.get("orderNumber")
            lead_barcode = data.get("leadBarcode")
            iso_barcode = data.get("isoBarcode")

            if not (order_number or lead_barcode or iso_barcode):
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": "Must provide at least one of orderNumber, leadBarcode, or isoBarcode"
                }).encode("utf-8"))
                return

            try:
                conn = sqlite3.connect(TRACKING_DB_FILE)
                cursor = conn.cursor()

                history_rows = []

                if iso_barcode:
                    cursor.execute("SELECT containerID, isoBarcode, history FROM tracking_data WHERE isoBarcode = ?", (iso_barcode,))
                    row = cursor.fetchone()
                    if row and row[2]:
                        # row[0] = containerID, row[1] = iso, row[2] = history
                        history_rows.append([row[0], row[1]] + row[2].strip().split("\n"))

                if lead_barcode:
                    cursor.execute("SELECT containerID, isoBarcode, history FROM tracking_data WHERE leadBarcode = ?", (lead_barcode,))
                    for row in cursor.fetchall():
                        if row[2]:
                            history_rows.append([row[0], row[1]] + row[2].strip().split("\n"))

                if order_number:
                    cursor.execute("SELECT containerID, isoBarcode, history FROM tracking_data WHERE orderNumber = ?", (order_number,))
                    for row in cursor.fetchall():
                        if row[2]:
                            history_rows.append([row[0], row[1]] + row[2].strip().split("\n"))


                conn.close()

                response = {
                    "status": "success",
                    "history": history_rows
                }

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(response).encode("utf-8"))

            except Exception as e:
                debug_log(f"[POST] ERROR in getTrackingHistory: {e}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": str(e)
                }).encode("utf-8"))
            return

        else:
            debug_log(f"[POST] ERROR: No matching endpoint for path '{parsed_path.path}'")
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "error",
                "message": f"Endpoint '{parsed_path.path}' not found"
            }).encode("utf-8"))
            return


def run():
    server = ThreadingHTTPServer((HOST, PORT), SimpleHandler)
    print(f"[SERVER] Threaded Server running on http://{HOST}:{PORT}")
    print(f"[SERVER] CORS enabled for https://pro.oneflowcloud.com")
    print(f"[SERVER] Debug mode: {DEBUG}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[SERVER] Server stopped.")
        server.server_close()


if __name__ == "__main__":
    run()
