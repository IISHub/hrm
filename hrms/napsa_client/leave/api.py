from hrms.napsa_client.main import NapsaClient
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
    approverId = NAPSA_CLIENT_INSTANCE.get_approver_name()

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



@frappe.whitelist(allow_guest=False, methods=["PATCH"])
def update_leave_status():
    data = frappe.form_dict
    leave_id = data.get("leaveId")
    new_status = data.get("status")
    rejectionReason = data.get("rejectionReason")
    
    ALLOWED_STATUSES = ["Approved", "Rejected"]
    
    if not new_status:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="status is required",
            status_code=400,
            http_status=400
        )

    if new_status not in ALLOWED_STATUSES:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"Invalid status. Allowed values: {', '.join(ALLOWED_STATUSES)}",
            status_code=400,
            http_status=400
        )

    if new_status == "Rejected" and not rejectionReason:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="rejectionReason is required when status is Rejected",
            status_code=400,
            http_status=400
        )
    if not leave_id:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="leaveId is required",
            status_code=400,
            http_status=400
        )


    try:
        leave_doc = frappe.get_doc("Leave Application", leave_id)

        leave_doc.status = new_status
        leave_doc.custom_rejection_reason = rejectionReason
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


@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_all_pending_leaves():
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
    total = frappe.db.count(
        "Leave Application",
        filters={
            "status": "Open",
            "docstatus": 0
        }
    )

    pending_leaves = frappe.db.sql("""
        SELECT
            la.name AS leave_id,
            emp.employee_name,
            lt.leave_type_name,
            la.from_date,
            la.to_date,
            la.total_leave_days,
            la.description,
            la.status,
            la.creation
        FROM `tabLeave Application` la
        LEFT JOIN `tabEmployee` emp ON emp.name = la.employee
        LEFT JOIN `tabLeave Type` lt ON lt.name = la.leave_type
        WHERE la.status = 'Open'
        AND la.docstatus = 0
        ORDER BY la.creation DESC
        LIMIT %s OFFSET %s
    """, (page_size, start), as_dict=True)

    leaves = []
    for row in pending_leaves:
        leaves.append({
            "leaveId": row.leave_id,
            "employee": {
                "employeeName": row.employee_name
            },
            "leaveType": {
                "name": row.leave_type_name
            },
            "duration": {
                "fromDate": str(row.from_date),
                "toDate": str(row.to_date),
                "totalDays": row.total_leave_days
            },
            "leaveReason": row.description,
            "status": row.status.upper(),
            "appliedOn": row.creation.strftime("%Y-%m-%d")
        })

    total_pages = (total + page_size - 1) // page_size

    return NAPSA_CLIENT_INSTANCE.send_response_list(
        status="success",
        message="Pending leaves fetched successfully",
        data={
            "leaves": leaves,
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


@frappe.whitelist(allow_guest=False, methods=["PATCH"])
def cancel_leave():
    data = frappe.form_dict
    leave_id = data.get("leaveId")

    if not leave_id:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="leaveId is required",
            status_code=400,
            http_status=400
        )

    try:
        leave_doc = frappe.get_doc("Leave Application", leave_id)

        if leave_doc.docstatus != 0:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Only draft leaves can be cancelled",
                status_code=400,
                http_status=400
            )

        if leave_doc.status != "Open":
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Only OPEN leaves can be cancelled",
                status_code=400,
                http_status=400
            )

        leave_doc.status = "Cancelled"
        leave_doc.save(ignore_permissions=True)
        frappe.db.commit()

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Leave cancelled successfully",
            data={
                "leaveId": leave_id,
                "status": "CANCELLED"
            },
            status_code=200,
            http_status=200
        )

    except frappe.DoesNotExistError:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Leave application not found",
            status_code=404,
            http_status=404
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Cancel Leave Error")
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=str(e),
            status_code=500,
            http_status=500
        )


@frappe.whitelist(allow_guest=False, methods=["PUT"])
def update_leave_application():
    data = frappe.form_dict

    leave_id = data.get("leaveId")
    leaveType = data.get("leaveType")
    leaveFromDate = data.get("leaveFromDate")
    leaveToDate = data.get("leaveToDate")
    isHalfDay = data.get("isHalfDay")
    leaveReason = data.get("leaveReason")

    if not leave_id:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="leaveId is required",
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

    if leaveType: 
        if leaveType not in allowed_leave_types:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Invalid Leave Type",
                status_code=400,
                http_status=400
            )

    try:
        leave_doc = frappe.get_doc("Leave Application", leave_id)
        if leave_doc.status != "Open":
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Only OPEN leaves can be updated",
                status_code=400,
                http_status=400
            )

        from_date = getdate(leaveFromDate)
        to_date = getdate(leaveToDate)

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
        existing_leave = frappe.get_all(
            "Leave Application",
            filters={
                "employee": leave_doc.employee,
                "name": ["!=", leave_id],
                "docstatus": 0,
                "from_date": ["<=", to_date],
                "to_date": [">=", from_date]
            }
        )

        if existing_leave:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Employee already has a leave application for these dates",
                status_code=409,
                http_status=409
            )

        leave_doc.leave_type = leaveType
        leave_doc.from_date = from_date
        leave_doc.to_date = to_date
        leave_doc.half_day = 1 if isHalfDay else 0
        leave_doc.description = leaveReason

        leave_doc.save(ignore_permissions=True)
        frappe.db.commit()

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Leave application updated successfully",
            data={
                "leaveId": leave_id
            },
            status_code=200,
            http_status=200
        )

    except frappe.DoesNotExistError:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Leave application not found",
            status_code=404,
            http_status=404
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Leave Application Update Error")
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=str(e),
            status_code=500,
            http_status=500
        )
