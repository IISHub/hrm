import json
import random
import uuid
from hrms.napsa_client.config.settings import NAPSA_BASE_URL, CLIENT_ID, USERNAME, PASSWORD
from hrms.napsa_client.main import NapsaClient
from hrms.napsa_client.mocks.mock import mock_get_by_nrc
from urllib.parse import urljoin
import requests
from frappe import _
import frappe
import re

NAPSA_CLIENT_INSTANCE = NapsaClient()
from frappe.utils import getdate, date_diff

@frappe.whitelist()
def create_leave_application():
    data = frappe.form_dict

    employeeId = data.get("employeeId")
    leaveType = data.get("leaveType")
    leaveFromDate = data.get("leaveFromDate")
    leaveToDate = data.get("leaveToDate")
    isHalfDay = data.get("isHalfDay")
    leaveReason = data.get("leaveReason")
    leaveStatus = data.get("leaveStatus") or "Pending"
    approverId = "timeastw@gmail.com"

    required_fields = {
        "employeeId": employeeId,
        "leaveType": leaveType,
        "leaveFromDate": leaveFromDate,
        "leaveToDate": leaveToDate,
        "leaveReason": leaveReason,
    }

    missing_fields = [k for k, v in required_fields.items() if not v]

    if missing_fields:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"Missing required fields: {', '.join(missing_fields)}",
            status_code=400,
            http_status=400
        )
        
    allowed_status = ["Open", "Approved", "Rejected", "Cancelled"]

    if leaveStatus not in allowed_status:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Invalid status. Allowed values: Open, Approved, Rejected, Cancelled",
            status_code=400,
            http_status=400
        )
        
    
    allowed_leave_types = [
    "Vacation",
    "Leave Without Pay",
    "Privilege Leave",
    "Sick Leave",
    "Compensatory Off",
    "Casual Leave"
    ]

    if leaveType not in allowed_leave_types:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Invalid Leave Type. Allowed types: Leave Without Pay, Privilege Leave, Sick Leave, Compensatory Off, Casual Leave",
            status_code=400,
            http_status=400
    )


    
  

    employee_name = frappe.db.get_value(
        "Employee",
        {"custom_id": employeeId},
        "name"
    )

    if not employee_name:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Employee not found",
            status_code=404,
            http_status=404
        )

    from_date = getdate(leaveFromDate)
    to_date = getdate(leaveToDate)
    
    existing_leave = frappe.get_all("Leave Application", filters={
        "employee": employee_name,
        "leave_type": leaveType,
        "docstatus": 0,
        "from_date": ["<=", to_date],
        "to_date": [">=", from_date]
    })

    if existing_leave:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Employee already has a leave application for these dates",
            status_code=409,
            http_status=409
    )

    if from_date > to_date:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Leave From Date cannot be later than Leave To Date",
            status_code=400,
            http_status=400
        )

    if isHalfDay and from_date != to_date:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Half-day leave must be for a single day",
            status_code=400,
            http_status=400
        )

    days_requested = date_diff(to_date, from_date) + 1
    if isHalfDay:
        days_requested = 0.5

    try:
        allocation = frappe.get_all("Leave Allocation", filters={
            "employee": employee_name,
            "leave_type": leaveType,
            "docstatus": 1,
            "from_date": ["<=", from_date],
            "to_date": [">=", to_date]
        }, fields=["name"])

        if not allocation:
            alloc_doc = frappe.get_doc({
                "doctype": "Leave Allocation",
                "employee": employee_name,
                "leave_type": leaveType,
                "from_date": from_date,
                "to_date": to_date,
                "new_leaves_allocated": days_requested
            })

            alloc_doc.insert(ignore_permissions=True)
            alloc_doc.submit()
            frappe.db.commit()
            
        leave_doc = frappe.get_doc({
            "doctype": "Leave Application",
            "employee": employee_name,
            "leave_type": leaveType,
            "from_date": from_date,
            "to_date": to_date,
            "half_day": 1 if isHalfDay else 0,
            "description": leaveReason,
            "status": leaveStatus,
            "leave_approver": approverId,
        })

        leave_doc.insert(ignore_permissions=True)
        frappe.flags.ignore_validate = True
        frappe.db.commit()

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Leave application submitted successfully",
            status_code=201,
            http_status=201
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Leave Application Insert Error")
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=str(e),
            status_code=500,
            http_status=500
        )
