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
DEBUG = False

def debug_log(message):
    if DEBUG:
        print(f"[DEBUG {datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {message}")

# Initialize databases
def init_main_db():
    with sqlite3.connect(MAIN_DB_FILE) as conn:
        cursor = conn.cursor()
        
        # Create employee_info table
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

        # Create facility_workstations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facility_workstations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workstation TEXT UNIQUE,
                availableStations INTEGER,
                eligibleList TEXT
            )
        """)

        # Create productionProcesses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productionProcesses (
                Product TEXT PRIMARY KEY,
                Processes TEXT
            )
        """)
        
        conn.commit()

def init_tracking_db():
    with sqlite3.connect(TRACKING_DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracking_data (
                containerID INTEGER,
                orderNumber TEXT,
                leadBarcode TEXT,
                isoBarcode TEXT UNIQUE,
                history TEXT
            )
        """)
        # Enable WAL mode for concurrent reads
        cursor.execute("PRAGMA journal_mode=WAL")
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

# Start worker thread
Thread(target=tracking_worker, daemon=True).start()

class SimpleHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Override to add more detailed logging"""
        debug_log(f"[HTTP] {self.address_string()} - {format%args}")

    def enqueue_tracking_job(self, job_func):
        tracking_queue.put(job_func)
        debug_log(f"[QUEUE] Enqueued job {job_func.__name__}, queue size={tracking_queue.qsize()}")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "success", "queued": True}).encode("utf-8"))

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed_path.query)
        
        debug_log(f"[GET] Path: '{parsed_path.path}', Query: {query}")

        # ---- Main DB: Employees ----
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

        # ---- Main DB: Facility Workstations ----
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

        # ---- Tracking DB Read-Only ----
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

        # ---- Tracking DB Write via GET (enqueue job) ----
        elif parsed_path.path == "/api/orderTrack":
            debug_log("[GET] Order tracking request")
            containerID = query.get("containerID", [None])[0]
            orderNumber = query.get("orderNumber", [None])[0]
            isoBarcode = query.get("isoBarcode", [None])[0]
            leadBarcode = query.get("leadBarcode", [None])[0]
            workstation = query.get("workstation", [None])[0] or ""
            employeeName = query.get("employeeName", [None])[0] or ""

            def job(cursor):
                nonlocal containerID, orderNumber, isoBarcode, leadBarcode, workstation, employeeName
                if containerID is not None:
                    try:
                        containerID = int(containerID)
                    except ValueError:
                        containerID = None
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

                if isoBarcode:
                    cursor.execute("SELECT containerID, orderNumber, leadBarcode, history FROM tracking_data WHERE isoBarcode = ?", (isoBarcode,))
                    row = cursor.fetchone()
                    if row:
                        containerID_existing, orderNumber_existing, leadBarcode_existing, history_existing = row
                        containerID_to_update = containerID if containerID is not None else containerID_existing
                        orderNumber_to_update = orderNumber if orderNumber else orderNumber_existing
                        leadBarcode_to_update = leadBarcode if leadBarcode else leadBarcode_existing
                        updated_history = append_history(history_existing, new_history_entry)
                        cursor.execute("""
                            UPDATE tracking_data
                            SET history = ?, containerID = ?, orderNumber = ?, leadBarcode = ?
                            WHERE isoBarcode = ?
                        """, (updated_history, containerID_to_update, orderNumber_to_update, leadBarcode_to_update, isoBarcode))
                    else:
                        cursor.execute("""
                            INSERT INTO tracking_data (containerID, orderNumber, leadBarcode, isoBarcode, history)
                            VALUES (?, ?, ?, ?, ?)
                        """, (containerID, orderNumber, leadBarcode, isoBarcode, new_history_entry))

                if leadBarcode:
                    cursor.execute("SELECT isoBarcode, containerID, orderNumber, history FROM tracking_data WHERE leadBarcode = ?", (leadBarcode,))
                    rows = cursor.fetchall()
                    for iso, container_existing, order_existing, history_existing in rows:
                        container_to_update = containerID if containerID is not None else container_existing
                        order_to_update = orderNumber if orderNumber else order_existing
                        updated_history = append_history(history_existing, new_history_entry)
                        cursor.execute("UPDATE tracking_data SET history = ?, containerID = ?, orderNumber = ? WHERE isoBarcode = ?", (updated_history, container_to_update, order_to_update, iso))

                if not isoBarcode and not leadBarcode and orderNumber:
                    cursor.execute("SELECT isoBarcode, containerID, leadBarcode, history FROM tracking_data WHERE orderNumber = ?", (orderNumber,))
                    rows = cursor.fetchall()
                    for iso, container_existing, lead_existing, history_existing in rows:
                        container_to_update = containerID if containerID is not None else container_existing
                        lead_to_update = leadBarcode if leadBarcode else lead_existing
                        updated_history = append_history(history_existing, new_history_entry)
                        cursor.execute("UPDATE tracking_data SET history = ?, containerID = ?, leadBarcode = ? WHERE isoBarcode = ?", (updated_history, container_to_update, lead_to_update, iso))

            self.enqueue_tracking_job(job)
            return

        # ---- Move Container (tracking update) ----
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

        else:
            debug_log(f"[GET] 404 - Unknown path: '{parsed_path.path}'")
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Request Not Found")
            return

        # ---- Send JSON Response ----
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode("utf-8"))

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        debug_log(f"[POST] ============ NEW POST REQUEST ============")
        debug_log(f"[POST] Path: '{parsed_path.path}'")
        debug_log(f"[POST] Headers: {dict(self.headers)}")
        
        # Read and parse JSON body
        content_length = int(self.headers.get('Content-Length', 0))
        debug_log(f"[POST] Content-Length: {content_length}")
        
        if content_length == 0:
            debug_log("[POST] ERROR: No body data")
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
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
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": f"Invalid JSON: {str(e)}"}).encode("utf-8"))
            return

        # Path matching with debug
        debug_log(f"[POST] Starting path matching...")

        # ---------------- /api/addOrUpdateEmployee ----------------
        if parsed_path.path == "/api/addOrUpdateEmployee":
            debug_log("[POST] Matched: /api/addOrUpdateEmployee")
            employee_name = data.get("employeeName")
            password = data.get("password")
            hourly_rate = data.get("hourlyRate")
            workstation_list = data.get("workstations", [])

            if not employee_name:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
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
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "message": f"Employee '{employee_name}' added/updated"}).encode("utf-8"))
                return

            except Exception as e:
                debug_log(f"[POST] ERROR in addOrUpdateEmployee: {e}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
                return

        # ---------------- /api/loggedin ----------------
        elif parsed_path.path == "/api/loggedin":
            debug_log("[POST] Matched: /api/loggedin")
            debug_log(f"[POST] Data keys: {list(data.keys())}")
            
            employee_name = data.get("employeeName")
            debug_log(f"[POST] Employee name: '{employee_name}'")
            
            if not employee_name:
                debug_log("[POST] ERROR: No employeeName in request")
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
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
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": f"Internal server error: {str(e)}"
                }).encode("utf-8"))
                return

        # ---------------- /api/loggedOut ----------------
        elif parsed_path.path == "/api/loggedOut":
            debug_log("[POST] Matched: /api/loggedOut")
            employee_name = data.get("employeeName")
            
            if not employee_name:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
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
                self.end_headers()
                self.wfile.write(json.dumps(response).encode("utf-8"))
                return

            except Exception as e:
                debug_log(f"[POST] ERROR in loggedOut: {e}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
                return

        # ---------------- /api/getEmployeeStartTime ----------------
        elif parsed_path.path == "/api/getEmployeeStartTime":
            debug_log("[POST] Matched: /api/getEmployeeStartTime")
            employee_name = data.get("employeeName")
            
            if not employee_name:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
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
                self.end_headers()
                self.wfile.write(json.dumps(response).encode("utf-8"))
                return

            except Exception as e:
                debug_log(f"[POST] ERROR in getEmployeeStartTime: {e}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
                return

        # ---------------- /api/logEmployeeTime ----------------
        elif parsed_path.path == "/api/logEmployeeTime":
            debug_log("[POST] Matched: /api/logEmployeeTime")
            employee_name = data.get("employeeName")
            start_time_str = data.get("start_time")
            end_time_str = data.get("end_time")

            if not employee_name or not start_time_str or not end_time_str:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
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
                self.end_headers()
                self.wfile.write(json.dumps(response).encode("utf-8"))

            except Exception as e:
                debug_log(f"[POST] ERROR in logEmployeeTime: {e}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
            
        # ---------------- /api/removeWorkstation ----------------
        elif parsed_path.path == "/api/removeWorkstation":
            debug_log("[POST] Matched: /api/removeWorkstation")
            employee_name = data.get("employeeName")
            workstation_name = data.get("workstationName")

            if not employee_name or not workstation_name:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
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
                self.end_headers()
                self.wfile.write(json.dumps(response).encode("utf-8"))
                return

            except Exception as e:
                debug_log(f"[POST] ERROR in removeWorkstation: {e}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": str(e)
                }).encode("utf-8"))
                return

        # ---------------- /api/removeEmployee ----------------
        elif parsed_path.path == "/api/removeEmployee":
            debug_log("[POST] Matched: /api/removeEmployee")
            employee_name = data.get("employeeName")

            if not employee_name:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
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
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "message": f"Employee '{employee_name}' removed"}).encode("utf-8"))
                return

            except Exception as e:
                debug_log(f"[POST] ERROR in removeEmployee: {e}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
                return

        # ---------------- /api/getEmployeeLoginState ----------------
        elif parsed_path.path == "/api/getEmployeeLoginState":
            debug_log("[POST] Matched: /api/getEmployeeLoginState")

            employee_name = data.get("employeeName")

            if not employee_name:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
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
                self.end_headers()
                self.wfile.write(json.dumps(response).encode("utf-8"))
                return

            except Exception as e:
                debug_log(f"[POST] ERROR in getEmployeeLoginState: {e}")
                debug_log(traceback.format_exc())
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": str(e)
                }).encode("utf-8"))
                return

        # ---------------- /api/getTrackingHistory ----------------
        elif parsed_path.path == "/api/getTrackingHistory":
            debug_log("[POST] Matched: /api/getTrackingHistory")

            # Extract identifiers from POST JSON body
            order_number = data.get("orderNumber")
            lead_barcode = data.get("leadBarcode")
            iso_barcode = data.get("isoBarcode")

            if not (order_number or lead_barcode or iso_barcode):
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
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

                # ISO Barcode lookup (unique)
                if iso_barcode:
                    cursor.execute("SELECT history, isoBarcode FROM tracking_data WHERE isoBarcode = ?", (iso_barcode,))
                    row = cursor.fetchone()
                    if row and row[0]:
                        # Prepend isoBarcode to each entry
                        history_rows.append([row[1]] + row[0].strip().split("\n"))

                # Lead Barcode lookup (may have multiple)
                if lead_barcode:
                    cursor.execute("SELECT history, isoBarcode FROM tracking_data WHERE leadBarcode = ?", (lead_barcode,))
                    for row in cursor.fetchall():
                        if row[0]:
                            history_rows.append([row[1]] + row[0].strip().split("\n"))

                # Order Number lookup (may have multiple)
                if order_number:
                    cursor.execute("SELECT history, isoBarcode FROM tracking_data WHERE orderNumber = ?", (order_number,))
                    for row in cursor.fetchall():
                        if row[0]:
                            history_rows.append([row[1]] + row[0].strip().split("\n"))

                conn.close()

                response = {
                    "status": "success",
                    "history": history_rows  # 2D list of history entries including isoBarcode
                }

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode("utf-8"))

            except Exception as e:
                debug_log(f"[POST] ERROR in getTrackingHistory: {e}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": str(e)
                }).encode("utf-8"))
            return




        # ---------------- Fallback for other POST paths ----------------
        else:
            debug_log(f"[POST] ERROR: No matching endpoint for path '{parsed_path.path}'")
            debug_log(f"[POST] Available endpoints: /api/addOrUpdateEmployee, /api/loggedin, /api/loggedOut, etc.")
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "error",
                "message": f"Endpoint '{parsed_path.path}' not found"
            }).encode("utf-8"))
            return


def run():
    server = ThreadingHTTPServer((HOST, PORT), SimpleHandler)
    print(f"[SERVER] Threaded Server running on http://{HOST}:{PORT}")
    print(f"[SERVER] Debug mode: {DEBUG}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[SERVER] Server stopped.")
        server.server_close()


if __name__ == "__main__":
    run()
