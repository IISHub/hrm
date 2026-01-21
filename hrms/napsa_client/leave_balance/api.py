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

    page = int(data.get("page", 1))
    page_size = int(data.get("pageSize", 10))

    if not employeeId:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message="employeeId is required",
            data=[],
            status_code=400,
            http_status=400
        )

    employee = frappe.db.get_value("Employee", {"custom_id": employeeId}, "name")
    if not employee:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message="Employee not found",
            data=[],
            status_code=404,
            http_status=404
        )
    if not from_date or not to_date:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message="fromDate and toDate are required",
            data=[],
            status_code=400,
            http_status=400
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

    for lt in leave_types:
        leave_type = lt.name

        allocated_before = frappe.db.sql("""
            SELECT IFNULL(SUM(total_leaves_allocated), 0)
            FROM `tabLeave Allocation`
            WHERE employee = %s
              AND leave_type = %s
              AND from_date < %s
              AND docstatus = 1
        """, (employee, leave_type, from_date))[0][0]

        used_before = frappe.db.sql("""
            SELECT IFNULL(SUM(total_leave_days), 0)
            FROM `tabLeave Application`
            WHERE employee = %s
              AND leave_type = %s
              AND to_date < %s
              AND status = 'Approved'
              AND docstatus = 1
        """, (employee, leave_type, from_date))[0][0]

        opening_balance = allocated_before - used_before

        allocated = frappe.db.sql("""
            SELECT IFNULL(SUM(total_leaves_allocated), 0)
            FROM `tabLeave Allocation`
            WHERE employee = %s
              AND leave_type = %s
              AND from_date BETWEEN %s AND %s
              AND docstatus = 1
        """, (employee, leave_type, from_date, to_date))[0][0]

        taken = frappe.db.sql("""
            SELECT IFNULL(SUM(total_leave_days), 0)
            FROM `tabLeave Application`
            WHERE employee = %s
              AND leave_type = %s
              AND from_date BETWEEN %s AND %s
              AND status = 'Approved'
              AND docstatus = 1
        """, (employee, leave_type, from_date, to_date))[0][0]

        expired = 0  

        closing_balance = opening_balance + allocated - taken - expired

        result.append({
            "leaveType": leave_type,
            "employeeId": employee,
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
                "pageSize": page_size,
                "totalRecords": total_records,
                "totalPages": total_pages,
                "hasNext": page < total_pages,
                "hasPrev": page > 1
            },
            "leaveBalances": result
        },
        status_code=200
    )
