from hrms.napsa_client.employee.api import NapsaClient
from frappe.utils import getdate, date_diff
from frappe.utils import now_datetime, getdate
from datetime import datetime
import frappe

NAPSA_CLIENT_INSTANCE = NapsaClient()


@frappe.whitelist(allow_guest=False, methods=["POST"])
def create_leave_allocation():
    data = frappe.local.form_dict

    employeeId = data.get("employeeId")
    leave_type = data.get("leaveType")
    from_date = data.get("fromDate")
    to_date = data.get("toDate")

    if not employeeId:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail", message="Employee ID is required", status_code=400, http_status=400
        )
        
    employee = frappe.db.get_value("Employee", {"custom_id": employeeId}, "name")

    if not employee:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail", message="Employee not found", status_code=404, http_status=404
        )

    ALLOWED_LEAVE_TYPES = NAPSA_CLIENT_INSTANCE.getAllAllowedLeaveTypes()
    
    if leave_type not in ALLOWED_LEAVE_TYPES:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"Invalid leave type. Allowed types: {', '.join(ALLOWED_LEAVE_TYPES)}",
            status_code=400,
            http_status=400
        )
        
    if not from_date or not to_date:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail", message="From date and To date leaves are required", status_code=400, http_status=400
        )
        
    if from_date > to_date:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail", message="From date cannot be after To date", status_code=400, http_status=400
        )
    
    

    from_date = getdate(from_date)
    to_date = getdate(to_date)   
    allocation_days = date_diff(to_date, from_date) + 1

    try:
        from_date = getdate(from_date)
        to_date = getdate(to_date)
        overlapping_record = frappe.db.exists("Leave Allocation", {
            "employee": employee,
            "leave_type": leave_type,
            "docstatus": ["<", 2], 
            "from_date": ["<=", to_date],
            "to_date": [">=", from_date]
        })

        if overlapping_record:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message=f"An allocation ({overlapping_record}) already exists for this period.",
                status_code=400,
                http_status=400
            )


        doc = frappe.get_doc({
            "doctype": "Leave Allocation",
            "employee": employee,
            "leave_type": leave_type,
            "from_date": from_date,
            "to_date": to_date,
            "new_leaves_allocated": float(allocation_days)
        })

        doc.insert(ignore_permissions=True)
        doc.submit()
        
        frappe.db.commit()

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Leave allocation created successfully",
            data=[],
            status_code=201,
            http_status=201
        )

    except Exception as e:
        frappe.db.rollback()
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message=str(e),
            status_code=500
        )
@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_leave_allocations_by_employee_id():
    args = frappe.local.form_dict
    employee = args.get("employee")
    page = int(args.get("page", 1))
    page_size = int(args.get("page_size", 10))
    start = (page - 1) * page_size

    employeeId = args.get("employeeId")
    
    if not employeeId:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Employee ID is required",
            data=[],
            status_code=400,
            http_status=400
        )
        
    if not page_size:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Page size is required",
            data=[],
            status_code=400,
            http_status=400
        )
        
    if not page_size:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Page size is required",
            data=[],
            status_code=400,
            http_status=400
        )

    employee = frappe.db.get_value("Employee", {"custom_id": employeeId}, "name")
    if not employee:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Employee not found",
            data=[],
            status_code=404,
            http_status=404
        )

    filters = {}
    if employee:
        filters["employee"] = employee

    total = frappe.db.count("Leave Allocation", filters=filters)

    raw_allocations = frappe.get_all(
        "Leave Allocation",
        filters=filters,
        fields=[
            "name",            
            "employee",       
            "leave_type",
            "from_date",      
            "to_date",
            "total_leaves_allocated",
            "unused_leaves"
        ],
        order_by="creation desc",
        start=start,
        page_length=page_size
    )

    formatted_allocations = []
    for d in raw_allocations:
        formatted_allocations.append({
            "id": d.get("name"),
            "leaveType": d.get("leave_type"),
            "fromDate": d.get("from_date"),
            "toDate": d.get("to_date"),
            "totalLeavesAllocated": d.get("total_leaves_allocated"),
            "unusedLeaves": d.get("unused_leaves")
        })

    return NAPSA_CLIENT_INSTANCE.send_response(
        status="success",
        message="Leave allocations fetched",
        data={
            "pagination": {
                "page": page,
                "pageSize": page_size,
                "total": total,
                "totalPages": (total + page_size - 1) // page_size,
                "hasNext": start + page_size < total,
                "hasPrev": page > 1
            },
            "allocations": formatted_allocations
        },
        status_code=200
    )



@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_all_leave_allocations():
    args = frappe.local.form_dict

    page = int(args.get("page", 1))
    page_size = int(args.get("page_size", 10))
    start = (page - 1) * page_size

    if page < 1 or page_size < 1:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Invalid pagination parameters",
            data=[],
            status_code=400,
            http_status=400
        )

    filters = {}
    leave_type = args.get("leaveType")
    employee_id = args.get("employeeId")

    if employee_id:
        employee = frappe.db.get_value("Employee", {"custom_id": employee_id}, "name")
        if not employee:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Employee not found",
                data=[],
                status_code=404,
                http_status=404
            )
        filters["employee"] = employee

    if leave_type:
        filters["leave_type"] = leave_type

    total = frappe.db.count("Leave Allocation", filters=filters)

    allocations = frappe.get_all(
        "Leave Allocation",
        filters=filters,
        fields=[
            "name",
            "employee",
            "leave_type",
            "from_date",
            "to_date",
            "total_leaves_allocated",
            "unused_leaves",
            "creation"
        ],
        order_by="creation desc",
        start=start,
        page_length=page_size
    )

    formatted_allocations = [
        {
            "id": a.name,
            "employeeNumber": a.employee,
            "leaveType": a.leave_type,
            "fromDate": a.from_date,
            "toDate": a.to_date,
            "totalLeavesAllocated": a.total_leaves_allocated,
            "unusedLeaves": a.unused_leaves
        }
        for a in allocations
    ]

    return NAPSA_CLIENT_INSTANCE.send_response(
        status="success",
        message="Leave allocations fetched successfully",
        data={
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size,
                "has_next": start + page_size < total,
                "has_prev": page > 1
            },
            "allocations": formatted_allocations
        },
        status_code=200
    )

