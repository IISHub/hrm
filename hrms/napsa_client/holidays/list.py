from hrms.napsa_client.employee.api import NapsaClient
import frappe
from datetime import datetime
import json

NAPSA_CLIENT_INSTANCE = NapsaClient()

@frappe.whitelist(allow_guest=False, methods=["POST"])
def create_holiday_list():
    data = frappe.local.form_dict

    name = data.get("name")
    from_date = data.get("fromDate")
    to_date = data.get("toDate")
    holidays = data.get("holidays")

    company = NAPSA_CLIENT_INSTANCE.GetCompany()

    if not name:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Holiday list name is required",
            status_code=400,
            http_status=400
        )

    if not company:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Company is required",
            status_code=400,
            http_status=400
        )

    if not from_date or not to_date:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="From date and To date are required",
            status_code=400,
            http_status=400
        )

    try:
        from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
        to_date = datetime.strptime(to_date, "%Y-%m-%d").date()

        if frappe.db.exists("Holiday List", name):
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Holiday List already exists",
                status_code=409,
                http_status=409
            )

        doc = frappe.get_doc({
            "doctype": "Holiday List",
            "holiday_list_name": name,
            "company": company,
            "from_date": from_date,
            "to_date": to_date
        })

        if holidays:
            if isinstance(holidays, str):
                holidays = json.loads(holidays)

            for h in holidays:
                if h.get("holiday_date"):
                    doc.append("holidays", {
                        "holiday_date": h.get("holiday_date"),
                        "description": h.get("description")
                    })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Holiday List created successfully",
            status_code=201,
            http_status=201
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create Holiday List Error")

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message=str(e),
            status_code=500,
            http_status=500
        )

@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_holiday_list():
    
    data = frappe.local.form_dict
    name = data.get("name")
    if not name:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Holiday list name is required",
            status_code=400,
            http_status=400
        )

    try:
        doc = frappe.get_doc("Holiday List", name)

        holidays = [
            {
                "holiday_date": h.holiday_date,
                "description": h.description
            }
            for h in doc.holidays
        ]

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            data={
                "name": doc.name,
                "company": doc.company,
                "from_date": doc.from_date,
                "to_date": doc.to_date,
                "holidays": holidays
            },
            status_code=200,
            http_status=200
        )

    except frappe.DoesNotExistError:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Holiday List not found",
            status_code=404,
            http_status=404
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Holiday List Error")

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message=str(e),
            status_code=500,
            http_status=500
        )


@frappe.whitelist()
def update_holiday_list():
    data = frappe.local.form_dict

    name = data.get("name")
    company = data.get("company")
    from_date = data.get("fromDate")
    to_date = data.get("toDate")
    holidays = data.get("holidays")

    if not name:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Holiday list name is required",
            status_code=400,
            http_status=400
        )

    try:
        doc = frappe.get_doc("Holiday List", name)

        # Update company
        if company:
            if not frappe.db.exists("Company", company):
                return NAPSA_CLIENT_INSTANCE.send_response(
                    status="fail",
                    message="Invalid Company",
                    status_code=404,
                    http_status=404
                )
            doc.company = company

        # Update dates
        if from_date:
            doc.from_date = datetime.strptime(from_date, "%Y-%m-%d").date()

        if to_date:
            doc.to_date = datetime.strptime(to_date, "%Y-%m-%d").date()

        # Replace holidays
        if holidays is not None:
            if isinstance(holidays, str):
                holidays = json.loads(holidays)

            doc.set("holidays", [])

            for h in holidays:
                if h.get("holiday_date"):
                    doc.append("holidays", {
                        "holiday_date": h.get("holiday_date"),
                        "description": h.get("description")
                    })

        doc.save(ignore_permissions=True)
        frappe.db.commit()

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Holiday List updated successfully",
            data={
                "name": doc.name,
                "company": doc.company
            },
            status_code=200,
            http_status=200
        )

    except frappe.DoesNotExistError:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Holiday List not found",
            status_code=404,
            http_status=404
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Update Holiday List Error")

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message=str(e),
            status_code=500,
            http_status=500
        )


@frappe.whitelist()
def delete_holiday_list():
    data = frappe.local.form_dict
    name = data.get("name")

    if not name:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Holiday list name is required",
            status_code=400,
            http_status=400
        )

    try:
        if not frappe.db.exists("Holiday List", name):
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Holiday List not found",
                status_code=404,
                http_status=404
            )

        frappe.delete_doc("Holiday List", name, ignore_permissions=True)
        frappe.db.commit()

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Holiday List deleted successfully",
            status_code=200,
            http_status=200
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Delete Holiday List Error")

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message=str(e),
            status_code=500,
            http_status=500
        )