from hrms.napsa_client.main import NapsaClient
import frappe

NAPSA_CLIENT_INSTANCE = NapsaClient()

company = frappe.conf.default_company
from hrms.napsa_client.main import NapsaClient
import frappe

NAPSA_CLIENT_INSTANCE = NapsaClient()

company = frappe.conf.default_company

@frappe.whitelist(allow_guest=False)
def create_department(company=company):
    data = frappe.form_dict
    department_name = data.get("department_name")
    try:
        if not department_name:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Department name must not be null",
                status_code=400,
                http_status=400,
            )

        doc = frappe.get_doc({
            "doctype": "Department",
            "department_name": department_name,
            "company": company or frappe.defaults.get_user_default("Company")
        })

        doc.insert()
        frappe.db.commit()

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Department created successfully",
            data={"name": doc.name},
            status_code=200,
            http_status=200,
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create Department Error")

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message=str(e),
            status_code=500,
            http_status=500,
        )

@frappe.whitelist(allow_guest=False)
def get_departments(company=None):
    try:
        company = company or frappe.conf.default_company

        data = frappe.get_all(
            "Department",
            filters={"company": company},
            fields=["name", "department_name", "company"]
        )

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Departments fetched successfully",
            data=data,
            status_code=200,
            http_status=200,
        )

    except Exception as e:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message=str(e),
            status_code=500,
            http_status=500,
        )

@frappe.whitelist(allow_guest=False)
def update_department(company=None):
    data = frappe.form_dict
    name = data.get("name")
    department_name = data.get("department_name")
    try:
        if not name:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Department name is required",
                status_code=400,
                http_status=400,
            )

        doc = frappe.get_doc("Department", name)

        if department_name:
            doc.department_name = department_name

        if company:
            doc.company = company

        doc.save()
        frappe.db.commit()

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Department updated successfully",
            status_code=200,
            http_status=200,
        )

    except frappe.DoesNotExistError:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Department not found",
            status_code=404,
            http_status=404,
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Update Department Error")

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message=str(e),
            status_code=500,
            http_status=500,
        )


@frappe.whitelist(allow_guest=False)
def get_departments(company=None):
    try:
        company = company or frappe.conf.default_company or frappe.defaults.get_user_default("Company")

        data = frappe.get_all(
            "Department",
            filters={"company": company},
            fields=["name", "department_name", "company"]
        )

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Departments fetched successfully",
            data=data,
            status_code=200,
            http_status=200,
        )

    except Exception as e:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message=str(e),
            status_code=500,
            http_status=500,
        )
        
    
@frappe.whitelist(allow_guest=False)
def update_department(name=None, department_name=None, company=None):
    try:
        if not name:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Department name is required",
                status_code=400,
                http_status=400,
            )

        current_company = company or frappe.conf.default_company or frappe.defaults.get_user_default("Company")

        doc = frappe.get_doc("Department", name)

        if doc.company != current_company:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Cannot update department from another company",
                status_code=403,
                http_status=403,
            )

        if department_name:
            doc.department_name = department_name

        doc.save()
        frappe.db.commit()

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Department updated successfully",
            status_code=200,
            http_status=200,
        )

    except frappe.DoesNotExistError:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Department not found",
            status_code=404,
            http_status=404,
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Update Department Error")

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message=str(e),
            status_code=500,
            http_status=500,
        )

@frappe.whitelist(allow_guest=False)
def delete_department(company=None):
    data = frappe.form_dict
    name = data.get("name")
    try:
        if not name:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Department name is required",
                status_code=400,
                http_status=400,
            )

        company = company or frappe.conf.default_company or frappe.defaults.get_user_default("Company")

        doc = frappe.get_doc("Department", name)
        if doc.company != company:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Cannot delete department from another company",
                status_code=403,
                http_status=403,
            )

        frappe.delete_doc("Department", name)
        frappe.db.commit()

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Department deleted successfully",
            status_code=200,
            http_status=200,
        )

    except frappe.DoesNotExistError:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Department not found",
            status_code=404,
            http_status=404,
        )

    except Exception as e:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message=str(e),
            status_code=500,
            http_status=500,
        )