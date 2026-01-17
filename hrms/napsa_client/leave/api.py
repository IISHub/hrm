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
    approverId = data.get("approverId")

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

    from_date = frappe.utils.getdate(leaveFromDate)
    to_date = frappe.utils.getdate(leaveToDate)

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


    approver_name = None
    if approverId:
        approver_name = frappe.db.get_value(
            "Employee",
            {"custom_id": approverId},
            "name"
        )

        if not approver_name:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Approver not found",
                status_code=404,
                http_status=404
            )

    try:
        leave_doc = frappe.get_doc({
            "doctype": "Leave Application",
            "employee": employee_name,
            "leave_type": leaveType,
            "from_date": from_date,
            "to_date": to_date,
            "half_day": 1 if isHalfDay else 0,
            "description": leaveReason,
            "status": leaveStatus,
            "leave_approver": approver_name,
        })

        leave_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Leave application submitted successfully",
            data={
                "leave_id": leave_doc.name,
                "status": leave_doc.status
            },
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
