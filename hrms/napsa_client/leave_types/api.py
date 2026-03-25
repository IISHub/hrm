from hrms.napsa_client.employee.api import NapsaClient
import frappe
from datetime import datetime

NAPSA_CLIENT_INSTANCE = NapsaClient()


def _convert_boolean(value):
    """Convert string or other input to boolean."""
    if isinstance(value, str):
        return value.lower() == "true"
    return bool(value)


def _convert_int(value, default=0):
    """Convert string/None to int safely."""
    if value in (None, ""):
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def _convert_float(value, default=0.0):
    """Convert string/None to float safely."""
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


@frappe.whitelist(allow_guest=False, methods=["POST"])
def create_leave_type():
    """Create a new Leave Type safely"""
    data = frappe.local.form_dict

    # Required field
    leave_type_name = data.get("leaveTypeName")
    if not leave_type_name:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Leave Type Name is required",
            status_code=400,
            http_status=400
        )

    # Check if Leave Type already exists
    if frappe.db.exists("Leave Type", leave_type_name):
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Leave Type already exists",
            status_code=409,
            http_status=409
        )

    # Numeric fields
    max_leaves_allowed = _convert_float(data.get("maxAllocation", 0))
    applicable_after = _convert_int(data.get("allowAfterDays", 0))
    max_continuous_days_allowed = _convert_int(data.get("maxConsecutiveLeaves", 0))
    maximum_carry_forwarded_leaves = _convert_float(data.get("maximumCarryForwardedLeaves", 0))
    expire_carry_forwarded_leaves_after_days = _convert_int(data.get("expireCarryForwardedLeavesAfterDays", 0))
    max_encashable_leaves = _convert_int(data.get("maxEncashableLeaves", 0))
    non_encashable_leaves = _convert_int(data.get("nonEncashableLeaves", 0))
    fraction_of_daily_salary_per_leave = _convert_float(data.get("fractionOfDailySalaryPerLeave", 0.0))

    # Boolean fields
    is_carry_forward = _convert_boolean(data.get("isCarryForward", False))
    is_lwp = _convert_boolean(data.get("isLeaveWithoutPay", False))
    is_ppl = _convert_boolean(data.get("isPartiallyPaid", False))
    is_optional_leave = _convert_boolean(data.get("isOptionalLeave", False))
    allow_negative = _convert_boolean(data.get("allowNegativeBalance", False))
    allow_over_allocation = _convert_boolean(data.get("allowOverAllocation", False))
    include_holiday = _convert_boolean(data.get("includeHolidaysInLeaves", False))
    is_compensatory = _convert_boolean(data.get("isCompensatory", False))
    allow_encashment = _convert_boolean(data.get("allowEncashment", False))
    is_earned_leave = _convert_boolean(data.get("isEarnedLeave", False))

    # Optional string fields
    earning_component = data.get("earningComponent", None)
    earned_leave_frequency = data.get("earnedLeaveFrequency", None)
    allocate_on_day = data.get("allocateOnDay", None)
    rounding = data.get("rounding", None)

    try:
        doc = frappe.get_doc({
            "doctype": "Leave Type",
            "leave_type_name": leave_type_name,
            "max_leaves_allowed": max_leaves_allowed,
            "applicable_after": applicable_after,
            "max_continuous_days_allowed": max_continuous_days_allowed,
            "maximum_carry_forwarded_leaves": maximum_carry_forwarded_leaves,
            "expire_carry_forwarded_leaves_after_days": expire_carry_forwarded_leaves_after_days,
            "max_encashable_leaves": max_encashable_leaves,
            "non_encashable_leaves": non_encashable_leaves,
            "fraction_of_daily_salary_per_leave": fraction_of_daily_salary_per_leave,
            "is_carry_forward": is_carry_forward,
            "is_lwp": is_lwp,
            "is_ppl": is_ppl,
            "is_optional_leave": is_optional_leave,
            "allow_negative": allow_negative,
            "allow_over_allocation": allow_over_allocation,
            "include_holiday": include_holiday,
            "is_compensatory": is_compensatory,
            "allow_encashment": allow_encashment,
            "is_earned_leave": is_earned_leave,
            "earning_component": earning_component,
            "earned_leave_frequency": earned_leave_frequency,
            "allocate_on_day": allocate_on_day,
            "rounding": rounding
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Leave Type created successfully",
            status_code=201,
            http_status=201
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create Leave Type Error")
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message=str(e),
            status_code=500,
            http_status=500
        )

@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_leave_type():
    """Get a single Leave Type by name"""
    data = frappe.local.form_dict
    name = data.get("name")

    if not name:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Leave Type name is required",
            status_code=400,
            http_status=400
        )

    try:
        doc = frappe.get_doc("Leave Type", name)
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            data={
                "name": doc.name,
                "leave_type_name": doc.leave_type_name,
                "max_leaves_allowed": doc.max_leaves_allowed,
                "applicable_after": doc.applicable_after,
                "max_continuous_days_allowed": doc.max_continuous_days_allowed,
                "is_carry_forward": doc.is_carry_forward,
                "is_lwp": doc.is_lwp,
                "is_ppl": doc.is_ppl,
                "is_optional_leave": doc.is_optional_leave,
                "allow_negative": doc.allow_negative,
                "allow_over_allocation": doc.allow_over_allocation,
                "include_holiday": doc.include_holiday,
                "is_compensatory": doc.is_compensatory
            },
            status_code=200,
            http_status=200
        )
    except frappe.DoesNotExistError:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Leave Type not found",
            status_code=404,
            http_status=404
        )
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Leave Type Error")
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message=str(e),
            status_code=500,
            http_status=500
        )



@frappe.whitelist(allow_guest=False, methods=["PUT", "PATCH"])
def update_leave_type():
    data = frappe.local.form_dict
    name = data.get("name")

    if not name:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Leave Type name is required",
            status_code=400,
            http_status=400
        )

    try:
        doc = frappe.get_doc("Leave Type", name)
        field_map = {
            "leave_type_name": ("leave_type_name", None),
            "maxAllocation": ("max_leaves_allowed", _convert_float),
            "allowAfterDays": ("applicable_after", _convert_int),
            "maxConsecutiveLeaves": ("max_continuous_days_allowed", _convert_int),
            "maximumCarryForwardedLeaves": ("maximum_carry_forwarded_leaves", _convert_float),
            "expireCarryForwardedLeavesAfterDays": ("expire_carry_forwarded_leaves_after_days", _convert_int),
            "maxEncashableLeaves": ("max_encashable_leaves", _convert_int),
            "nonEncashableLeaves": ("non_encashable_leaves", _convert_int),
            "fractionOfDailySalaryPerLeave": ("fraction_of_daily_salary_per_leave", _convert_float),
            "isCarryForward": ("is_carry_forward", _convert_boolean),
            "isLeaveWithoutPay": ("is_lwp", _convert_boolean),
            "isPartiallyPaid": ("is_ppl", _convert_boolean),
            "isOptionalLeave": ("is_optional_leave", _convert_boolean),
            "allowNegativeBalance": ("allow_negative", _convert_boolean),
            "allowOverAllocation": ("allow_over_allocation", _convert_boolean),
            "includeHolidaysInLeaves": ("include_holiday", _convert_boolean),
            "isCompensatory": ("is_compensatory", _convert_boolean),
            "allowEncashment": ("allow_encashment", _convert_boolean),
            "isEarnedLeave": ("is_earned_leave", _convert_boolean),
            "earningComponent": ("earning_component", None),
            "earnedLeaveFrequency": ("earned_leave_frequency", None),
            "allocateOnDay": ("allocate_on_day", None),
            "rounding": ("rounding", None),
        }

        for api_field, (doc_field, converter) in field_map.items():
            if api_field in data:
                value = data[api_field]
                if converter:
                    value = converter(value)
                setattr(doc, doc_field, value)

        doc.save(ignore_permissions=True)
        frappe.db.commit()

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Leave Type updated successfully",
            status_code=200,
            http_status=200
        )

    except frappe.DoesNotExistError:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Leave Type not found",
            status_code=404,
            http_status=404
        )
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Update Leave Type Error")
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message=str(e),
            status_code=500,
            http_status=500
        )

@frappe.whitelist(allow_guest=False, methods=["DELETE"])
def delete_leave_type():
    """Delete a Leave Type"""
    data = frappe.local.form_dict
    name = data.get("name")

    if not name:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Leave Type name is required",
            status_code=400,
            http_status=400
        )

    try:
        if not frappe.db.exists("Leave Type", name):
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Leave Type not found",
                status_code=404,
                http_status=404
            )

        frappe.delete_doc("Leave Type", name, ignore_permissions=True)
        frappe.db.commit()

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Leave Type deleted successfully",
            status_code=200,
            http_status=200
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Delete Leave Type Error")
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message=str(e),
            status_code=500,
            http_status=500
        )


@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_all_leave_types():
    """Fetch all leave types with summary data"""
    try:
        leave_types = frappe.get_all(
            "Leave Type",
            fields=["name", "leave_type_name"]
        )

        data = []
        for lt in leave_types:
            doc = frappe.get_doc("Leave Type", lt.name)
            data.append({
                "name": doc.name,
                "leave_type_name": doc.leave_type_name,
                "max_leaves_allowed": doc.max_leaves_allowed,
                "applicable_after": doc.applicable_after,
                "max_continuous_days_allowed": doc.max_continuous_days_allowed,
                "is_carry_forward": doc.is_carry_forward
            })

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            data=data,
            status_code=200,
            http_status=200
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get All Leave Types Error")
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message=str(e),
            status_code=500,
            http_status=500
        )