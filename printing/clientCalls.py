import requests
from dataclasses import dataclass
from typing import List
import json
from datetime import datetime

target_ip = "192.168.111.184"

@dataclass
class Employee:
    id: int
    employeeName: str
    password: str
    hourlyRate: float

def fetch_all_employees(server_ip=target_ip, port=8080) -> List[Employee]:
    url = f"http://{server_ip}:{port}/api/employees"
    try:
        response = requests.get(url, timeout=10)  
        response.raise_for_status()  

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

def send_print_data(containerID=None, orderNumber=None, leadBarcode=None, isoBarcode=None,
                    workstation=None, employeeName=None, prodType=None, size=None, itemNum=None,
                    server_ip=target_ip, port=8080):
    base_url = f"http://{server_ip}:{port}"
    params = {
        "containerID": containerID,
        "orderNumber": orderNumber,
        "leadBarcode": leadBarcode,
        "isoBarcode": isoBarcode,
        "workstation": workstation,
        "employeeName": employeeName,
        "prodType": prodType,
        "size": size,
        "itemNum": itemNum
    }

    try:
        resp = requests.get(f"{base_url}/api/receivePrintData", params=params)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}


def fetch_next_container_id(server_ip=target_ip, port=8080):
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

def fetch_employee_times(employee_name, server_ip=target_ip, port=8080):
    """
    Fetch both start_time and end_time for the given employee from the server.
    Returns a tuple of datetime objects (start_time, end_time) or (None, None) if not set.
    """

    url = f"http://{server_ip}:{port}/api/getEmployeeTimes"
    payload = {"employeeName": employee_name}

    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "success":
            start_time_str = data.get("start_time")
            end_time_str = data.get("end_time")

            start_dt = (
                datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
                if start_time_str else None
            )
            end_dt = (
                datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
                if end_time_str else None
            )

            if start_dt or end_dt:
                return start_dt, end_dt
            else:
                print(f"[Client] Employee '{employee_name}' has no start/end times set.")
                return None, None
        else:
            print(f"[Client] Error: {data.get('message')}")
            return None, None

    except requests.exceptions.RequestException as e:
        print(f"[Client] Connection error: {e}")
        return None, None

def log_employee_time(employeeName: str, start_time: datetime, end_time: datetime,
                      server_ip=target_ip, port=8080):
    if not employeeName or not start_time or not end_time:
        return {"status": "error", "message": "employeeName, start_time, and end_time are required"}

    url = f"http://{server_ip}:{port}/api/logEmployeeTime"

    payload = {
        "employeeName": employeeName,
        "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}



