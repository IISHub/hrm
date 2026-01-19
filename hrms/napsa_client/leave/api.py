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
from frappe.utils import getdate, date_diff, nowdate

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



@frappe.whitelist(allow_guest=False)
def get_all_leaves():
    args = frappe.request.args

    try:
        page = int(args.get("page", 0))
        page_size = int(args.get("page_size", 0))
    except (TypeError, ValueError):
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Page and page_size must be integers",
            status_code=400,
            http_status=400
        )

    if page <= 0:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Page parameter must be a positive integer",
            status_code=400,
            http_status=400
        )

    if page_size <= 0:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Page size parameter must be a positive integer",
            status_code=400,
            http_status=400
        )

    start = (page - 1) * page_size
    total = frappe.db.count("Leave Application")

    leaves = frappe.get_all(
        "Leave Application",
        fields=[
            "name",
            "employee",
            "employee_name",
            "department",
            "leave_type",
            "from_date",
            "to_date",
            "total_leave_days",
            "half_day",
            "status",
            "posting_date"
        ],
        order_by="posting_date desc",
        start=start,
        page_length=page_size
    )

    data = []
    
    for leave in leaves:
        department_name = frappe.db.get_value(
            "Department",
            leave.department,
            "department_name"
        ) or ""
        data.append({
            "leaveId": leave.name,
            "employee": {
                "employeeId": leave.employee,
                "employeeName": leave.employee_name,
                "department": department_name
            },
            "leaveType": {
                "name": leave.leave_type
            },
            "duration": {
                "fromDate": leave.from_date,
                "toDate": leave.to_date,
                "totalDays": leave.total_leave_days,
                "isHalfDay": bool(leave.half_day)
            },
            "status": leave.status.upper(),
            "appliedOn": leave.posting_date
        })

    total_pages = (total + page_size - 1) // page_size

    return NAPSA_CLIENT_INSTANCE.send_response_list(
        status="success",
        message="Leaves fetched successfully",
        data={
            "leaves": data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        },
        status_code=200,
        http_status=200
    )



@frappe.whitelist()
def get_leave_balances():
    args = frappe.request.args
    employeeId = args.get("employeeId")
    leaveYear = args.get("leaveYear")

    try:
        if not employeeId:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="employeeId is required",
                status_code=400,
                http_status=400
            )

        if not leaveYear:
            leaveYear = str(nowdate().split("-")[0])

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

        employee_doc = frappe.get_doc("Employee", employee_name)

        year_start = f"{leaveYear}-01-01"
        year_end = f"{leaveYear}-12-31"

        allocations = frappe.get_all("Leave Allocation", filters={
            "employee": employee_name,
            "docstatus": 1,
            "from_date": ["between", [year_start, year_end]]
        }, fields=["name", "leave_type", "new_leaves_allocated", "from_date", "to_date", "carry_forward", "carry_forwarded_leaves_count"])

        balances = []

        for alloc in allocations:
            total = alloc.new_leaves_allocated

            used = frappe.db.sql("""
                SELECT IFNULL(SUM(total_leave_days),0)
                FROM `tabLeave Application`
                WHERE employee=%s
                AND leave_type=%s
                AND status='Approved'
                AND docstatus=1
                AND from_date >= %s
                AND to_date <= %s
            """, (employee_name, alloc.leave_type, alloc.from_date, alloc.to_date))[0][0]

            pending = frappe.db.sql("""
                SELECT IFNULL(SUM(total_leave_days),0)
                FROM `tabLeave Application`
                WHERE employee=%s
                AND leave_type=%s
                AND status='Open'
                AND docstatus=0
                AND from_date >= %s
                AND to_date <= %s
            """, (employee_name, alloc.leave_type, alloc.from_date, alloc.to_date))[0][0]

            available = total - (used + pending)

            balances.append({
                "leaveType": {"name": alloc.leave_type},
                "total": total,
                "used": used,
                "pending": pending,
                "available": available,
                "carryForward": alloc.carry_forward,
                "carryForwardLimit": alloc.carry_forward_limit
            })

        last_updated = frappe.utils.now_datetime()

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            data={
                "employeeId": employeeId,
                "employeeName": employee_doc.employee_name,
                "leaveYear": leaveYear,
                "balances": balances,
                "lastUpdated": last_updated
            },
            status_code=200,
            http_status=200
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Leave Balance Error")
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=str(e),
            status_code=500,
            http_status=500
        )



@frappe.whitelist(allow_guest=False, methods=["POST"])
def update_leave_status():
    data = frappe.form_dict
    leave_id = data.get("leaveId")
    new_status = data.get("status")

    if not leave_id:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="leaveId is required",
            status_code=400,
            http_status=400
        )

    if not new_status:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="status is required",
            status_code=400,
            http_status=400
        )

    valid_status = ["Open", "Approved", "Rejected", "Cancelled"]

    if new_status not in valid_status:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"Invalid status. Allowed values: {', '.join(valid_status)}",
            status_code=400,
            http_status=400
        )

    try:
        leave_doc = frappe.get_doc("Leave Application", leave_id)

        leave_doc.status = new_status
        leave_doc.save()
        frappe.db.commit()

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Leave status updated successfully",
            data={
                "leaveId": leave_id,
                "newStatus": new_status
            },
            status_code=200,
            http_status=200
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Update Leave Status Error")
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=str(e),
            status_code=500,
            http_status=500
        )
