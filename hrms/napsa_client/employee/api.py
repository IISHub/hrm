from hrms.napsa_client.main import NapsaClient
from urllib.parse import urljoin
from frappe import _
import frappe



NAPSA_CLIENT_INSTANCE = NapsaClient()


@frappe.whitelist()
def create_employee():
    return NAPSA_CLIENT_INSTANCE.send_response(
        status="success",
        message="API create reserved",
        status_code=200,
        http_status=200
    )


@frappe.whitelist()
def get_all_employees():
    data = []
    return NAPSA_CLIENT_INSTANCE.send_response(
        
        status="success",
        message="API fetch all employees reserved",
        data=data,
        status_code=200,
        http_status=200
    )
@frappe.whitelist()
def get_employee():
    data = frappe.form_dict
    employee_id = data.get("id")
    
    if not employee_id:
        NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Employee id required",
            status_code=400,
            http_status=400
        )
    return NAPSA_CLIENT_INSTANCE.send_response(
        status="success",
        message=f"API fetch employee {employee_id} reserved",
        status_code=200,
        http_status=200
    )


@frappe.whitelist()
def update_employee():
    data = frappe.form_dict
    employee_id = data.get("id")
    
    if not employee_id:
        NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Employee id required",
            status_code=400,
            http_status=400
        )
    return NAPSA_CLIENT_INSTANCE.send_response(
        status="success",
        message=f"API update employee {employee_id} reserved",
        status_code=200,
        http_status=200
    )


@frappe.whitelist()
def delete_employee():
    data = frappe.form_dict
    employee_id = data.get("id")
    
    if not employee_id:
        NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Employee id required",
            status_code=400,
            http_status=400
        )
    return NAPSA_CLIENT_INSTANCE.send_response(
        status="success",
        message=f"API delete employee {employee_id} reserved",
        status_code=200,
        http_status=200
    )
