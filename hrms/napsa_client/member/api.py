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

    else:
        token = NAPSA_CLIENT_INSTANCE.get_saved_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        url = urljoin(NAPSA_BASE_URL, f"icare-thirdparty-returns/memberKycNrc?nrc={nrc}")
        try:
            res = requests.get(url, headers=headers, timeout=50)
            res.raise_for_status()
            member_data = res.json().get("data", {})
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="success",
                message="Member details retrieved successfully",
                data=member_data,
                status_code=200,
                http_status=200
            )
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
def get_napsa_member_current_year_ceiling():
    token = NAPSA_CLIENT_INSTANCE.get_saved_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = urljoin(NAPSA_BASE_URL, f"icare-thirdparty-returns/ceilingValue")
    try:
        res = requests.get(url, headers=headers, timeout=50)
        res.raise_for_status()
        member_data = res.json().get("data", {})
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Member details retrieved successfully",
            data=member_data,
            status_code=200,
            http_status=200
        )
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
def get_napsa_member_ssn(use_mock=False):
    ssn = frappe.form_dict.get("ssn")
    if not ssn:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Member ssn must not be empty",
            status_code=400,
            http_status=400
        )

    token = NAPSA_CLIENT_INSTANCE.get_saved_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = urljoin(NAPSA_BASE_URL, f"icare-thirdparty-returns/memberKyc/{ssn}")
    try:
        res = requests.get(url, headers=headers, timeout=50)
        res.raise_for_status()
        member_data = res.json().get("data", {})
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Member details retrieved successfully",
            data=member_data,
            status_code=200,
            http_status=200
        )
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
def submit_napsa_member_single_return():
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
    url = urljoin(NAPSA_BASE_URL, f"icare-thirdparty-returns/employerReturn")
    payload = {
        "returnReference": generate_numeric_id(),
        "employerAccountNumber": NAPSA_CLIENT_INSTANCE.get_employee_account(),
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
def napsa_member_return_status():
    returnReference = frappe.form_dict.get("returnReference")
    if not returnReference:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Reference Number is required",
            status_code=400,
            http_status=400
        )
    token = NAPSA_CLIENT_INSTANCE.get_saved_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = urljoin(NAPSA_BASE_URL, f"icare-thirdparty-returns/queryReturnStatus/{returnReference}")
    try:
        res = requests.get(url, headers=headers, timeout=50)
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
