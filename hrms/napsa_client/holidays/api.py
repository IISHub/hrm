from hrms.napsa_client.employee.api import NapsaClient
from frappe.utils import now_datetime
from datetime import date, datetime
from frappe import _
import frappe

NAPSA_CLIENT_INSTANCE = NapsaClient()

def get_next_custom_id():
    last_id = frappe.db.sql(
        """
        SELECT MAX(custom_id)
        FROM `tabHoliday List`
        """,
        as_list=True
    )[0][0]
    try:
        last_id = int(last_id)
    except (TypeError, ValueError):
        last_id = 0

    return last_id + 1


def is_holiday_range_taken(from_date, to_date):
    return frappe.db.exists(
        "Holiday List",
        {
            "from_date": ["<=", to_date],
            "to_date": [">=", from_date]
        }
    )



@frappe.whitelist(allow_guest=False, methods=["POST"])
def create_holiday():
    data = frappe.local.form_dict

    name = data.get("name")
    from_date = data.get("fromDate")
    to_date = data.get("toDate")

    if not name:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message="Holiday name is required",
            data=[],
            status_code=400,
            http_status=400
        )

    if not from_date or not to_date:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message="From date and To date are required",
            data=[],
            status_code=400,
            http_status=400
        )

    try:
        from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date()
        to_date_obj = datetime.strptime(to_date, "%Y-%m-%d").date()
    except ValueError:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message="Invalid date format. Use YYYY-MM-DD",
            data=[],
            status_code=400,
            http_status=400
        )
        
    total_days = (to_date_obj - from_date_obj).days + 1
    today = date.today()
    if from_date_obj < today:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Cannot create holiday in the past",
            data=[],
            status_code=400
        )
        
    MAX_DAYS = 30
    if total_days > MAX_DAYS:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"Holiday cannot exceed {MAX_DAYS} days",
            data=[],
            status_code=400
        )
        
    if from_date_obj.year != to_date_obj.year:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Holiday must be within the same year",
            data=[],
            status_code=400
        )



    if from_date_obj > to_date_obj:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message="From date cannot be after To date",
            data=[],
            status_code=400,
            http_status=400
        )

    if is_holiday_range_taken(from_date_obj, to_date_obj):
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Selected dates overlap with an existing holiday",
            data=[],
            status_code=400,
            http_status=400
        )

    if frappe.db.exists("Holiday List", {"holiday_list_name": name}):
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Holiday list with this name already exists",
            data=[],
            status_code=400,
            http_status=400
        )

    total_days = (to_date_obj - from_date_obj).days + 1
    next_custom_id = get_next_custom_id()

    doc = frappe.get_doc({
        "doctype": "Holiday List",
        "custom_id": next_custom_id,
        "holiday_list_name": name,
        "from_date": from_date,
        "to_date": to_date,
        "total_holidays": total_days,
        "year": now_datetime().year
    })

    doc.insert()
    frappe.db.commit()

    return NAPSA_CLIENT_INSTANCE.send_response(
        status="success",
        message="Holiday created successfully",
        data={
            "name": doc.name,
            "id": doc.custom_id
        },
        status_code=201
    )


@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_holidays():
    args = frappe.local.form_dict
    page = int(args.get("page", 1))
    page_size = int(args.get("page_size", 10))
    start = (page - 1) * page_size

    total = frappe.db.count("Holiday List")

    holidays = frappe.get_all(
        "Holiday List",
        fields=[
            "name",
            "custom_id",
            "holiday_list_name",
            "from_date",
            "to_date"
        ],
        order_by="custom_id desc",
        start=start,
        page_length=page_size
    )

    return NAPSA_CLIENT_INSTANCE.send_response(
        status="success",
        message="Holidays fetched",
        data={
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size,
                "has_next": start + page_size < total,
                "has_prev": page > 1
            },
            "holidays": [
                {
                    "id": h.custom_id,
                    "name": h.name,
                    "fromDate": str(h.from_date),
                    "toDate": str(h.to_date)
                } for h in holidays
            ]
        },
        status_code=200
    )



@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_holiday_by_custom_id(custom_id):
    doc_name = frappe.db.get_value(
        "Holiday List",
        {"custom_id": custom_id},
        "name"
    )

    if not doc_name:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Holiday not found",
            data=[],
            status_code=404
        )

    doc = frappe.get_doc("Holiday List", doc_name)

    return NAPSA_CLIENT_INSTANCE.send_response(
        status="success",
        message="Holiday fetched",
        data=doc.as_dict(),
        status_code=200
    )


@frappe.whitelist(allow_guest=False, methods=["PUT"])
def update_holiday():
    data = frappe.local.form_dict
    custom_id = data.get("id")
    
    if not custom_id:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Holiday ID is required",
            data=[],
            status_code=400,
            http_status=400
        )
    doc_name = frappe.db.get_value(
        "Holiday List",
        {"custom_id": custom_id},
        "name"
    )

    if not doc_name:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Holiday not found",
            data=[],
            status_code=404
        )

    
    doc = frappe.get_doc("Holiday List", doc_name)

    if data.get("name"):
        doc.holiday_list_name = data.get("name")

    if data.get("fromDate"):
        doc.from_date = data.get("fromDate")

    if data.get("toDate"):
        doc.to_date = data.get("toDate")

    if doc.from_date and doc.to_date:
        doc.total_holidays = (
            datetime.strptime(str(doc.to_date), "%Y-%m-%d").date()
            - datetime.strptime(str(doc.from_date), "%Y-%m-%d").date()
        ).days + 1

    doc.save()
    frappe.db.commit()

    return NAPSA_CLIENT_INSTANCE.send_response(
        status="success",
        message="Holiday updated successfully",
        data=[],
        status_code=200
    )


@frappe.whitelist(allow_guest=False, methods=["DELETE"])
def delete_holiday():
    data = frappe.local.form_dict
    custom_id = data.get("id")
    
    doc_name = frappe.db.get_value(
        "Holiday List",
        {"custom_id": custom_id},
        "name"
    )

    if not doc_name:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Holiday not found",
            data=[],
            http_status=404,
            status_code=404
        )

    frappe.delete_doc("Holiday List", doc_name)
    frappe.db.commit()

    return NAPSA_CLIENT_INSTANCE.send_response(
        status="success",
        message="Holiday deleted successfully",
        data=None,
        status_code=200,
        http_status=200
    )
