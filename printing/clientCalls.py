import requests
from dataclasses import dataclass
from typing import List, Optional
import json
from datetime import datetime

TARGET_IP = "192.168.111.230"

# Define an Employee dataclass
@dataclass
class Employee:
    id: int
    employeeName: str
    password: str
    hourlyRate: float

def loggedIn(employeeName: str, server_ip=TARGET_IP, port=8080):
    if not employeeName:
        return {"status": "error", "message": "employeeName is required"}

    url = f"http://{server_ip}:{port}/api/loggedin"
    payload = {
        "status": "LoggedIn",
        "employeeName": employeeName
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()  # Return server response as JSON
    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON response from server"}

def get_employee_login_state(employeeName: str, server_ip=TARGET_IP, port=8080):
    if not employeeName:
        return {"status": "error", "message": "employeeName is required"}

    url = f"http://{server_ip}:{port}/api/getEmployeeLoginState"
    payload = {"employeeName": employeeName}

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()

        data = response.json()
        return data

    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON response from server"}

def loggedOut(employeeName: str, server_ip=TARGET_IP, port=8080):
    if not employeeName:
        return {"status": "error", "message": "employeeName is required"}

    url = f"http://{server_ip}:{port}/api/loggedOut"
    payload = {
        "status": "LoggedOut",
        "employeeName": employeeName
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()  # Return server response as JSON
    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON response from server"}

def fetch_all_employees(server_ip=TARGET_IP, port=8080) -> List[Employee]:
    url = f"http://{server_ip}:{port}/api/employees"
    try:
        response = requests.get(url, timeout=10)  # Add timeout to prevent indefinite hang
        response.raise_for_status()  # Raise an error for HTTP errors

        data = response.json()

        if data.get("status") != "success":
            return []

        employee_list = []
        for emp in data.get("employees", []):
            employee_list.append(Employee(
                id=emp.get("id"),
                employeeName=emp.get("employeeName"),
                password=emp.get("password"),
                hourlyRate=emp.get("hourlyRate")
            ))

        return employee_list

    except requests.RequestException:
        return []

def fetch_employee_start_time(employee_name: str, server_ip=TARGET_IP, port=8080) -> Optional[str]:
    url = f"http://{server_ip}:{port}/api/getEmployeeStartTime"
    payload = {"employeeName": employee_name}
    
    try:
        response = requests.post(url, json=payload, timeout=10)  # POST since server expects data
        response.raise_for_status()

        data = response.json()

        if data.get("status") != "success":
            return None

        return data.get("start_time")

    except requests.RequestException:
        return None

def log_employee_time(employee_name: str, start_time: datetime, end_time: datetime,
                      server_ip=TARGET_IP, port=8080):
    """
    Sends a POST request to log an employee's start and end time.
    """
    if not employee_name:
        return {"status": "error", "message": "employee_name is required"}

    url = f"http://{server_ip}:{port}/api/logEmployeeTime"

    payload = {
        "employeeName": employee_name,
        "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}
    except ValueError:
        return {"status": "error", "message": "Invalid JSON response from server"}


def removeWorkstation(employee_name: str, workstation_name: str,
                      server_ip: str = TARGET_IP, port: int = 8080):
    
    url = f"http://{server_ip}:{port}/api/removeWorkstation"
    payload = {
        "employeeName": employee_name,
        "workstationName": workstation_name
    }

    try:
        resp = requests.post(url, json=payload, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "success":
            print(f"[WARN] Server returned error: {data}")
        else:
            print(f"[INFO] Successfully removed '{employee_name}' from '{workstation_name}'")
        return data
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to call removeWorkstation: {e}")
        return {"status": "error", "message": str(e)}

def add_or_update_employee(employeeName, password=None, hourlyRate=None, workstation_list=None,
                           server_ip=TARGET_IP, port=8080):
    """
    Sends a POST request to the server to add or update an employee.
    """
    if not employeeName:
        return {"status": "error", "message": "employeeName is required"}

    url = f"http://{server_ip}:{port}/api/addOrUpdateEmployee"
    
    # Prepare JSON payload
    payload = {
        "employeeName": employeeName,
        "password": password,
        "hourlyRate": hourlyRate,
        "workstations": workstation_list or []
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        resp_json = response.json()
        return resp_json

    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}
    except json.JSONDecodeError as e:
        return {"status": "error", "message": "Invalid JSON response from server"}


def fetch_next_container_id(server_ip=TARGET_IP, port=8080):
    url = f"http://{server_ip}:{port}/api/nextContainerID"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "success":
            return data.get("nextContainerID")
        else:
            print(f"Server error: {data.get('message')}")
            return None

    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

def remove_employee(employeeName, server_ip=TARGET_IP, port=8080):
    """
    Request server to remove an employee by name. Server handles table updates.
    """
    if not employeeName:
        return {"status": "error", "message": "No employee name provided"}

    url = f"http://{server_ip}:{port}/api/removeEmployee"
    try:
        resp = requests.post(url, json={"employeeName": employeeName})
        resp.raise_for_status()
        return resp.json()

    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}


def get_facility_workstations(server_ip=TARGET_IP, port=8080):
    workstations = []
    availableStations = []
    eligibleList = []

    url = f"http://{server_ip}:{port}/api/facilityWorkstations"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        # Expecting data to contain keys: workstations, availableStations, eligibleList
        workstations = data.get("workstations") or []
        availableStations = data.get("availableStations") or []
        eligibleList = data.get("eligibleList") or []

    except requests.RequestException as e:
        print(f"[ERROR] Could not fetch facility workstations: {e}")
    except ValueError as e:
        # JSON decoding error
        print(f"[ERROR] Invalid JSON response: {e}")

    return workstations, availableStations, eligibleList


def send_tracking_data(containerID, orderNumber, leadBarcode, isoBarcode, workstation, employeeName,
                       itemNum, prodType, server_ip=TARGET_IP, port=8080):
    base_url = f"http://{server_ip}:{port}"
    params = {
        "containerID": containerID,
        "orderNumber": orderNumber,
        "leadBarcode": leadBarcode,
        "isoBarcode": isoBarcode,
        "workstation": workstation,
        "employeeName": employeeName,
        "itemNum": itemNum,
        "prodType": prodType
    }

    try:
        resp = requests.get(f"{base_url}/api/orderTrack", params=params)
        resp.raise_for_status()
        return resp.json()

    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}

def move_container(leadBarcode=None, isoBarcode=None, workstation="", employeeName="",
                   server_ip=TARGET_IP, port=8080):

    base_url = f"http://{server_ip}:{port}"
    params = {
        "leadBarcode": leadBarcode,
        "isoBarcode": isoBarcode,
        "workstation": workstation,
        "employeeName": employeeName
    }

    try:
        resp = requests.get(f"{base_url}/api/moveContainer", params=params)
        resp.raise_for_status()
        return resp.json()

    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}

def fetch_facility_workstations(server_ip=TARGET_IP, port=8080):
    url = f"http://{server_ip}:{port}/api/facilityWorkstations"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Extract the lists
        workstations = data.get("workstations", [])
        availableStations = data.get("availableStations", [])
        eligibleList = data.get("eligibleList", [])

        return workstations, availableStations, eligibleList

    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return [], [], []
