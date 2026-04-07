import frappe


def createEmploymentContract(employee, EmployeeType, contractStartDate, contractEndDate, contractTerms):
    try:
        contract = frappe.get_doc({
            "doctype": "Contract",
            "party_type": "Employee",
            "party_name": employee.name,
            "party_full_name": f"{employee.first_name} {employee.last_name}",
            "status": "Active",
            "is_signed": 1,
            "party_user": frappe.session.user,
            "start_date": contractStartDate,
            "end_date": contractEndDate,
            "contract_terms": contractTerms,
        })

        contract.insert(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "contract_name": contract.name
        }

    except frappe.ValidationError as e:
        frappe.log_error(
            title="Contract Validation Error",
            message=frappe.get_traceback()
        )
        return {
            "status": "fail",
            "message": f"Validation error: {str(e)}"
        }

    except Exception as e:
        frappe.log_error(
            title="Contract Creation Error",
            message=frappe.get_traceback()
        )
        return {
            "status": "fail",
            "message": f"Failed to create contract: {str(e)}"
        }