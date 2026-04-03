from hrms.napsa_client.main import NapsaClient
from datetime import datetime
import frappe


NAPSA_CLIENT_INSTANCE = NapsaClient()


@frappe.whitelist(allow_guest=False, methods=["POST"])
def terminate_contract():
    data = frappe.form_dict
    contract_name = data.get("contractName")
    termination_date_str = data.get("terminationDate")
    
    if not contract_name:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Contract name is required.",
            http_status=400,
            status_code=400
        )
    
    if not termination_date_str:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Termination date is required.",
            http_status=400,
            status_code=400
        )
    
    try:
        termination_date = datetime.strptime(termination_date_str, "%Y-%m-%d").date()
    except ValueError:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Termination date must be in YYYY-MM-DD format.",
            http_status=400,
            status_code=400
        )
    
    try:
        contract = frappe.get_doc("Contract", contract_name)
        if contract.status != "Active":
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message=f"Contract {contract_name} is not active.",
                http_status=400,
                status_code=400
            )
        
        if contract.start_date and termination_date < contract.start_date:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Termination date cannot be before contract start date.",
                http_status=400,
                status_code=400
            )
        
        contract.status = "Inactive"
        contract.end_date = termination_date
        contract.end_date = termination_date
        contract.save()

        frappe.db.set_value("Contract", contract.name, "status", "Inactive")
        frappe.db.commit()
        
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            status_code=200,
            http_status=200,
            message=f"Contract {contract_name} terminated successfully."
        )
    
    except frappe.DoesNotExistError:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"No contract found with name {contract_name}.",
            http_status=404,
            status_code=404
        )
    
    except Exception as e:
        frappe.log_error(
            title="Contract Termination Error",
            message=frappe.get_traceback()
        )
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"Failed to terminate contract: {str(e)}",
            http_status=500,
            status_code=500
        )
        
        
@frappe.whitelist(allow_guest=False, methods=["POST"])
def create_new_contract():
    data = frappe.form_dict

    employee_id = data.get("employeeId")
    contract_type = data.get("contractType")
    start_date_str = data.get("startDate")
    end_date_str = data.get("endDate")

    if not employee_id:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Employee ID is required.",
            http_status=400,
            status_code=400
        )

    if not contract_type:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Contract type is required.",
            http_status=400,
            status_code=400
        )

    if not start_date_str:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Start date is required.",
            http_status=400,
            status_code=400
        )

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = (
            datetime.strptime(end_date_str, "%Y-%m-%d").date()
            if end_date_str else None
        )
    except ValueError:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Dates must be in YYYY-MM-DD format.",
            http_status=400,
            status_code=400
        )

    try:
        employee = frappe.get_doc("Employee", employee_id)

        # CHECK ACTIVE CONTRACT FIRST
        active_contract = frappe.db.exists(
            "Contract",
            {
                "party_name": employee.name,
                "status": "Active"
            }
        )

        if active_contract:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="An active contract already exists for this employee. Please terminate the current contract first.",
                http_status=400,
                status_code=400
            )

        contract = frappe.get_doc({
            "doctype": "Contract",
            "party_type": "Employee",
            "party_name": employee.name,
            "party_full_name": f"{employee.first_name} {employee.last_name}",
            "contract_type": contract_type,
            "start_date": start_date,
            "end_date": end_date
        })

        contract.insert(ignore_permissions=True)

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Contract created successfully.",
            data={
                "contractName": contract.name
            }
        )

    except Exception as e:
        frappe.log_error(
            title="Create Contract Error",
            message=frappe.get_traceback()
        )

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"Failed to create contract: {str(e)}",
            http_status=500,
            status_code=500
        )