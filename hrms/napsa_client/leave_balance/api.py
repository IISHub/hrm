from hrms.napsa_client.main import NapsaClient
from frappe.utils import getdate, date_diff
from datetime import timedelta
from frappe.utils import cint
from frappe import _
import frappe
import re

NAPSA_CLIENT_INSTANCE = NapsaClient()

@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_employee_leave_balance_report():
    data = frappe.local.form_dict

    employeeId = data.get("employeeId")
    from_date = data.get("fromDate")
    to_date = data.get("toDate")
    page = cint(data.get("page", 1))
    page_size = cint(data.get("page_size", 10))

    if not employeeId:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error", message="employeeId is required", status_code=400
        )

    if not from_date or not to_date:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error", message="fromDate and toDate are required", status_code=400
        )

    employee = frappe.db.get_value("Employee", {"custom_id": employeeId}, "name")
    if not employee:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error", message="Employee not found", status_code=404
        )
    offset = (page - 1) * page_size
    leave_types = frappe.get_all(
        "Leave Type",
        fields=["name"],
        limit_start=offset,
        limit_page_length=page_size
    )
    total_records = frappe.db.count("Leave Type")
    total_pages = (total_records + page_size - 1) // page_size


    result = []
    summary = {
        "totalOpeningBalance": 0.0,
        "totalAllocated": 0.0,
        "totalTaken": 0.0,
        "totalExpired": 0.0,
        "totalClosingBalance": 0.0
    }

    for lt in leave_types:
        leave_type = lt.name

 
        allocated_before = frappe.db.sql("""
            SELECT IFNULL(SUM(total_leaves_allocated), 0)
            FROM `tabLeave Allocation`
            WHERE employee = %s AND leave_type = %s AND from_date < %s AND docstatus = 1
        """, (employee, leave_type, from_date))[0][0]

        used_before = frappe.db.sql("""
            SELECT IFNULL(SUM(total_leave_days), 0)
            FROM `tabLeave Application`
            WHERE employee = %s AND leave_type = %s AND to_date < %s AND status = 'Approved' AND docstatus = 1
        """, (employee, leave_type, from_date))[0][0]

        opening_balance = float(allocated_before - used_before)


        allocated = float(frappe.db.sql("""
            SELECT IFNULL(SUM(total_leaves_allocated), 0)
            FROM `tabLeave Allocation`
            WHERE employee = %s AND leave_type = %s AND from_date BETWEEN %s AND %s AND docstatus = 1
        """, (employee, leave_type, from_date, to_date))[0][0])

        taken = float(frappe.db.sql("""
            SELECT IFNULL(SUM(total_leave_days), 0)
            FROM `tabLeave Application`
            WHERE employee = %s AND leave_type = %s AND (from_date BETWEEN %s AND %s) 
            AND status = 'Approved' AND docstatus = 1
        """, (employee, leave_type, from_date, to_date))[0][0])

        expired = 0.0  
        closing_balance = (opening_balance + allocated) - taken - expired

        summary["totalOpeningBalance"] += opening_balance
        summary["totalAllocated"] += allocated
        summary["totalTaken"] += taken
        summary["totalExpired"] += expired
        summary["totalClosingBalance"] += closing_balance

        result.append({
            "leaveType": leave_type,
            "openingBalance": opening_balance,
            "newLeavesAllocated": allocated,
            "leavesTaken": taken,
            "leavesExpired": expired,
            "closingBalance": closing_balance
        })


    return NAPSA_CLIENT_INSTANCE.send_response_list(
        status="success",
        message="Leave balance report fetched",
        data={
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total_records,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            },
            "summary": summary,
            "leaveBalances": result
        },
        status_code=200
    )