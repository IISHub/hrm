from hrms.napsa_client.main import NapsaClient
from frappe import _
import frappe

NAPSA_CLIENT_INSTANCE = NapsaClient()

@frappe.whitelist(allow_guest=False, methods=["GET"])
def designations():
    try:
        designations = frappe.get_all(
            "Designation",
            fields=["name"]
        )

        # Convert all designation names to uppercase
        for d in designations:
            d["name"] = d["name"].upper() if d.get("name") else d.get("name")

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Designations fetched successfully",
            data=designations,
            status_code=200,
            http_status=200
        )

    except Exception as e:
        frappe.log_error(
            title="Get Designations Failed",
            message=frappe.get_traceback()
        )

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"Failed to fetch designations: {str(e)}",
            data=[],
            status_code=500,
            http_status=500
        )