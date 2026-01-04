import json
import random
import uuid
from hrms.napsa_client.config.settings import NAPSA_BASE_URL, CLIENT_ID, USERNAME, PASSWORD
from hrms.napsa_client.main import NapsaClient
from hrms.napsa_client.mocks.mock import mock_get_by_nrc
from urllib.parse import urljoin
import requests
from frappe import _
import frappe
import re

NAPSA_CLIENT_INSTANCE = NapsaClient()



def generate_numeric_id(length=12):
    first_digit = random.randint(1, 9)
    remaining_digits = ''.join(str(random.randint(0, 9)) for _ in range(length - 1))
    return str(first_digit) + remaining_digits
 

@frappe.whitelist()
def get_napsa_member(use_mock=False):
    nrc = frappe.form_dict.get("nrc")

    if not nrc:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Member NRC must not be empty",
            status_code=400,
            http_status=400
        )

    if use_mock:
        data = {
            "ssn": "SSN123456",
            "firstName": "John",
            "lastName": "Doe",
            "nrc": nrc,
            "gender": "M"
        }
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Member fetched successfully",
            data=data,
            status_code=200,
            http_status=200
        )

    try:
        token = NAPSA_CLIENT_INSTANCE.get_saved_token()
        if not token:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Authentication token not found",
                status_code=401,
                http_status=401
            )

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        url = urljoin(
            NAPSA_BASE_URL,
            f"icare-thirdparty-returns/memberKycNrc?nrc={nrc}"
        )

        res = requests.get(url, headers=headers, timeout=50)
        data = res.json()
        print("NAPSA Member Response:", data)
        status_code = int(data.get("statusCode", res.status_code))
        member_data = data.get("data")

        if status_code != 200:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message=data.get("message", "Error fetching member details"),
                status_code=status_code,
                http_status=status_code
            )

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Member details retrieved successfully",
            data=member_data,
            status_code=200,
            http_status=200
        )

    except requests.exceptions.RequestException as e:
        frappe.log_error(frappe.get_traceback(), "NAPSA API Request Error")
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Failed to communicate with NAPSA service",
            status_code=500,
            http_status=500
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "NAPSA Member Fetch Error")
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="An unexpected error occurred",
            status_code=500,
            http_status=500
        )



@frappe.whitelist()
def get_napsa_member_current_year_ceiling():
    try:
        token = NAPSA_CLIENT_INSTANCE.get_saved_token()
        if not token:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Authentication token not found",
                status_code=401,
                http_status=401
            )

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        url = urljoin(
            NAPSA_BASE_URL,
            "icare-thirdparty-returns/ceilingValue"
        )

        res = requests.get(url, headers=headers, timeout=50)
        data = res.json()

        status_code = int(data.get("statusCode", res.status_code))
        ceiling_data = data.get("data")

        if status_code != 200:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message=data.get("message", "Failed to fetch ceiling value"),
                status_code=status_code,
                http_status=status_code
            )

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Ceiling value retrieved successfully",
            data=ceiling_data,
            status_code=200,
            http_status=200
        )

    except requests.exceptions.RequestException:
        frappe.log_error(
            frappe.get_traceback(),
            "NAPSA Ceiling API Request Error"
        )
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Failed to communicate with NAPSA service",
            status_code=500,
            http_status=500
        )

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "NAPSA Ceiling Fetch Error"
        )
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="An unexpected error occurred",
            status_code=500,
            http_status=500
        )



@frappe.whitelist()
def get_napsa_member_ssn(use_mock=False):
    ssn = frappe.form_dict.get("ssn")

    if not ssn:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Member SSN must not be empty",
            status_code=400,
            http_status=400
        )


    if use_mock:
        data = {
            "ssn": ssn,
            "firstName": "Jane",
            "lastName": "Doe",
            "nrc": "123456/78/9",
            "gender": "F"
        }
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Member fetched successfully",
            data=data,
            status_code=200,
            http_status=200
        )

    try:
        token = NAPSA_CLIENT_INSTANCE.get_saved_token()
        if not token:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Authentication token not found",
                status_code=401,
                http_status=401
            )

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        url = urljoin(
            NAPSA_BASE_URL,
            f"icare-thirdparty-returns/memberKyc/{ssn}"
        )

        res = requests.get(url, headers=headers, timeout=50)
        data = res.json()

        status_code = int(data.get("statusCode", res.status_code))
        member_data = data.get("data")

        if status_code != 200:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message=data.get("message", "Error fetching member details"),
                status_code=status_code,
                http_status=status_code
            )

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Member details retrieved successfully",
            data=member_data,
            status_code=200,
            http_status=200
        )

    except requests.exceptions.RequestException:
        frappe.log_error(
            frappe.get_traceback(),
            "NAPSA SSN API Request Error"
        )
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Failed to communicate with NAPSA service",
            status_code=500,
            http_status=500
        )

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "NAPSA SSN Fetch Error"
        )
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="An unexpected error occurred",
            status_code=500,
            http_status=500
        )



@frappe.whitelist()
def submit_napsa_member_single_return():
    payload_fields = {
        "year": frappe.form_dict.get("year"),
        "month": frappe.form_dict.get("month"),
        "ssn": frappe.form_dict.get("ssn"),
        "nrc": frappe.form_dict.get("nrc"),
        "surname": frappe.form_dict.get("surname"),
        "firstName": frappe.form_dict.get("firstName"),
        "dob": frappe.form_dict.get("dob"),
        "employeeGrossPay": frappe.form_dict.get("employeeGrossPay"),
        "employerShare": frappe.form_dict.get("employerShare"),
        "employeeShare": frappe.form_dict.get("employeeShare"),
    }

    required_fields = {
        "year": "Year is required",
        "month": "Month is required",
        "ssn": "SSN is required",
        "nrc": "NRC is required",
        "surname": "Surname is required",
        "firstName": "First Name is required",
        "dob": "DOB is required",
        "employeeGrossPay": "Employee Gross Pay is required",
        "employeeShare": "Employee Share is required",
        "employerShare": "Employer Share is required",
    }

    for field, error_message in required_fields.items():
        if not payload_fields.get(field):
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message=error_message,
                status_code=400,
                http_status=400
            )


    token = NAPSA_CLIENT_INSTANCE.get_saved_token()
    if not token:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Authentication token not found",
            status_code=401,
            http_status=401
        )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "returnReference": generate_numeric_id(),
        "employerAccountNumber": NAPSA_CLIENT_INSTANCE.get_employeer_account(),
        **payload_fields
    }

    url = urljoin(
        NAPSA_BASE_URL,
        "icare-thirdparty-returns/employerReturn"
    )

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=50)
        data = res.json()
        print("NAPSA Submit Return Response:", data)

        status_code = int(data.get("statusCode", res.status_code))

        if status_code != 200:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message=data.get("errors"),
                status_code=status_code,
                http_status=status_code
            )

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Return submitted successfully",
            data=data.get("data"),
            status_code=200,
            http_status=200
        )

    except requests.exceptions.RequestException:
        frappe.log_error(
            frappe.get_traceback(),
            "NAPSA Submit Single Return API Error"
        )
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Failed to communicate with NAPSA service",
            status_code=500,
            http_status=500
        )

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "NAPSA Submit Single Return Error"
        )
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="An unexpected error occurred",
            status_code=500,
            http_status=500
        )



@frappe.whitelist()
def napsa_member_return_status():
    return_reference = frappe.form_dict.get("returnReference")

    if not return_reference:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Return reference is required",
            status_code=400,
            http_status=400
        )

    try:
        token = NAPSA_CLIENT_INSTANCE.get_saved_token()
        if not token:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Authentication token not found",
                status_code=401,
                http_status=401
            )

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        url = urljoin(
            NAPSA_BASE_URL,
            "icare-thirdparty-returns/queryReturnStatus"
        )

        res = requests.get(
            url,
            headers=headers,
            params={"returnReference": return_reference},
            timeout=50
        )

        data = res.json()
        print("NAPSA Return Status Response:", data)
        status_code = int(data.get("statusCode", res.status_code))

        if status_code != 200:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message=data.get("message", "Failed to fetch return status"),
                status_code=status_code,
                http_status=status_code
            )

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Return status retrieved successfully",
            data=data.get("data"),
            status_code=200,
            http_status=200
        )

    except requests.exceptions.RequestException:
        frappe.log_error(
            frappe.get_traceback(),
            "NAPSA Return Status API Error"
        )
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Failed to communicate with NAPSA service",
            status_code=500,
            http_status=500
        )

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "NAPSA Return Status Fetch Error"
        )
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="An unexpected error occurred",
            status_code=500,
            http_status=500
        )



@frappe.whitelist()
def submit_napsa_member_topup():
    returnReference = frappe.form_dict.get("returnReference")
    year = frappe.form_dict.get("year")
    month = frappe.form_dict.get("month")
    ssn = frappe.form_dict.get("ssn")
    nrc = frappe.form_dict.get("nrc")
    surname = frappe.form_dict.get("surname")
    firstName = frappe.form_dict.get("firstName")
    dob = frappe.form_dict.get("dob")
    employeeGrossPay = frappe.form_dict.get("employeeGrossPay")
    employerShare = frappe.form_dict.get("employerShare")
    employeeShare = frappe.form_dict.get("employeeShare")
    
    if not year:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Year is required",
            status_code=400,
            http_status=400
        )
    if not month:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Month is required",
            status_code=400,
            http_status=400
        )
    
    if not ssn:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="SSN is required",
            status_code=400,
            http_status=400
        )
    if not nrc:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="NRC is required",
            status_code=400,
            http_status=400
        )
    
    
    if not surname:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Surname is required",
            status_code=400,
            http_status=400
        )
    
    if not firstName:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="First Name is required",
            status_code=400,
            http_status=400
        )
    
    if not employeeGrossPay:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Employee Gross Pay is required",
            status_code=400,
            http_status=400
        )
    
    
    if not employeeShare:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Empliyee Share is required",
            status_code=400,
            http_status=400
        )
        
    if not year:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Year is required",
            status_code=400,
            http_status=400
        )
    if not dob:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="DOB is required",
            status_code=400,
            http_status=400
        )
    if not year:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Year is required",
            status_code=400,
            http_status=400
        )
    if not returnReference:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Reference Number is required",
            status_code=400,
            http_status=400
        )
    
    if not employerShare:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Employer Share is required",
            status_code=400,
            http_status=400
        )
        
    token = NAPSA_CLIENT_INSTANCE.get_saved_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = urljoin(NAPSA_BASE_URL, f"icare-thirdparty-returns/employerReturnTopUpReturn")
    payload = {
        "returnReference": generate_numeric_id(),
        "employerAccountNumber": NAPSA_CLIENT_INSTANCE.get_employeer_account(),
        "year": year,
        "month": month,
        "ssn": ssn,
        "nrc": nrc,
        "surname": surname,
        "firstName": firstName,
        "dob": dob,
        "employeeGrossPay": employeeGrossPay,
        "employerShare": employerShare,
        "employeeShare": employeeShare
        }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=50)
        res.raise_for_status()

        return res.json()
    except requests.HTTPError as e:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"Failed to fetch member: {str(e)}",
            status_code=res.status_code if 'res' in locals() else 500,
            http_status=res.status_code if 'res' in locals() else 500
        )
    except Exception as e:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"An error occurred: {str(e)}",
            status_code=500,
            http_status=500
        ) 




@frappe.whitelist()
def submit_napsa_member_bulk_return():
    returns_raw = frappe.form_dict.get("returns")

    if not returns_raw:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="'returns' field is required for bulk submission",
            status_code=400,
            http_status=400
        )

    try:
        returns_list = frappe.parse_json(returns_raw)
    except Exception:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Invalid JSON format for 'returns'",
            status_code=400,
            http_status=400
        )

    if not isinstance(returns_list, list) or not returns_list:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="'returns' must be a non-empty list",
            status_code=400,
            http_status=400
        )
    token = NAPSA_CLIENT_INSTANCE.get_saved_token()
    if not token:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Authentication token not found",
            status_code=401,
            http_status=401
        )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    employer_account = NAPSA_CLIENT_INSTANCE.get_employeer_account()


    for item in returns_list:
        if not isinstance(item, dict):
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Each return item must be an object",
                status_code=400,
                http_status=400
            )
        item["employerAccountNumber"] = employer_account


    payload = {
        "returnReference": generate_numeric_id(),
        "requestCallBackUrl": (
            "http://41.60.191.7:8081/"
            "api/method/hrms.napsa_client.member.api.napsa_callback"
        ),
        "returns": returns_list
    }

    url = urljoin(
        NAPSA_BASE_URL,
        "icare-thirdparty-returns/bulkEmployerReturns"
    )


    try:
        res = requests.post(url, headers=headers, json=payload, timeout=50)
        data = res.json()
        print("NAPSA Bulk Return Submission Response:", data)

        status_code = int(data.get("statusCode", res.status_code))

        if status_code != 200:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message=data.get("message", "Bulk return submission failed"),
                status_code=status_code,
                http_status=status_code
            )

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Bulk return submitted successfully",
            data=data.get("data"),
            status_code=200,
            http_status=200
        )

    except requests.exceptions.RequestException:
        frappe.log_error(
            frappe.get_traceback(),
            "NAPSA Bulk Return API Error"
        )
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Failed to communicate with NAPSA service",
            status_code=500,
            http_status=500
        )

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "NAPSA Bulk Return Error"
        )
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="An unexpected error occurred",
            status_code=500,
            http_status=500
        )

@frappe.whitelist(allow_guest=True)
def napsa_callback():
    try:
        if frappe.request.method == "POST":
            data = frappe.request.get_data(as_text=True)
            try:
                data = json.loads(data)
            except Exception:
                data = frappe.local.form_dict  
        else:
            data = frappe.local.form_dict

        print("=== Callback Data Received ===")
        print(json.dumps(data, indent=2))
        print(json.dumps(data, indent=2), "NAPSA Callback Data")

        return {
            "status": "success",
            "message": "Callback received successfully",
            "data": data
        }

    except Exception as e:
        frappe.log_error(str(e), "NAPSA Callback Error")
        return {
            "status": "error",
            "message": str(e)
        }



@frappe.whitelist()
def get_napsa_member_full_details(use_mock=True):

    nrc = frappe.form_dict.get("nrc")
    ssn = frappe.form_dict.get("ssn")

    if not nrc and not ssn:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Either NRC or SSN is required",
            status_code=400,
            http_status=400
        )

    if use_mock:
        try:
            response = requests.get(
                f"http://0.0.0.0:9950/api/v1/kyc/?nrc={nrc}",
                timeout=10
            )
        except requests.RequestException as e:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="KYC service unavailable",
                status_code=503,
                http_status=503
            )

        try:
            payload = response.json()
        except ValueError:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Invalid response from KYC service",
                status_code=502,
                http_status=502
            )

        if not payload.get("success"):
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message=payload.get("message", "Employee not found"),
                status_code=404,
                http_status=404
            )

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Member retrieved successfully",
            data=payload.get("data"),
            status_code=200,
            http_status=200
        )


    try:

        token = NAPSA_CLIENT_INSTANCE.get_saved_token()
        if not token:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Authentication token not found",
                status_code=401,
                http_status=401
            )

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        if nrc:
            member_url = urljoin(
                NAPSA_BASE_URL,
                f"icare-thirdparty-returns/memberKycNrc?nrc={nrc}"
            )
        else:
            member_url = urljoin(
                NAPSA_BASE_URL,
                f"icare-thirdparty-returns/memberKyc/{ssn}"
            )

        member_res = requests.get(member_url, headers=headers, timeout=50)
        print("NAPSA Member Full Details Response:", member_res.json())
        member_data = member_res.json().get("data")
        
        member_status_code = int(member_res.json().get("statusCode", member_res.status_code))

        if member_status_code != 200 or not member_data:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message=member_res.json().get("message", "Error fetching member details"),
                status_code=member_status_code,
                http_status=member_status_code
            )
        member_data["dob"] = "23/03/1970"

        ceiling_url = urljoin(NAPSA_BASE_URL, "icare-thirdparty-returns/ceilingValue")
        ceiling_res = requests.get(ceiling_url, headers=headers, timeout=50)
        ceiling_data = ceiling_res.json().get("data")
        ceiling_status_code = int(ceiling_res.json().get("statusCode", ceiling_res.status_code))

        if ceiling_status_code != 200 or not ceiling_data:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message=ceiling_res.json().get("message", "Error fetching ceiling value"),
                status_code=ceiling_status_code,
                http_status=ceiling_status_code
            )

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Member details and ceiling retrieved successfully",
            data={"member": member_data, "ceiling": ceiling_data},
            status_code=200,
            http_status=200
        )

    except requests.exceptions.RequestException as e:
        frappe.log_error(frappe.get_traceback(), "NAPSA Combined API Request Error")
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Failed to communicate with NAPSA service",
            status_code=500,
            http_status=500
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "NAPSA Combined API Error")
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="An unexpected error occurred",
            status_code=500,
            http_status=500
        )
