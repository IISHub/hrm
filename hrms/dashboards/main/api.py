from hrms.napsa_client.main import NapsaClient
import frappe




NAPSA_CLIENT_INSTANCE = NapsaClient()

@frappe.whitelist(allow_guest=False, methods=["GET"])
def summary():
    try:
        total_employees = frappe.db.count("Employee")
        active_count = frappe.db.count("Employee", {"status": "Active"})
        inactive_count = frappe.db.count("Employee", {"status": "Inactive"})
        on_leave_count = frappe.db.count("Employee", {"status": "On Leave"})

        data = {
            "total": total_employees,
            "active": active_count,
            "inactive": inactive_count,
            "onLeave": on_leave_count
        }

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Employee statistics fetched successfully",
            data=data,
            status_code=200,
            http_status=200
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Employee Stats Error")
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=str(e),
            status_code=500,
            http_status=500
        )
