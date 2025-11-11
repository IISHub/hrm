from hrms.napsa_client.config.settings import NAPSA_BASE_URL, CLIENT_ID, USERNAME, PASSWORD
from hrms.napsa_client.main import NapsaClient
from hrms.napsa_client.mocks.mock import mock_get_by_nrc
from urllib.parse import urljoin
import requests
from frappe import _
import frappe
import re

NAPSA_CLIENT_INSTANCE = NapsaClient()


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
    token = NAPSA_CLIENT_INSTANCE.get_saved_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = urljoin(NAPSA_BASE_URL, f"icare-thirdparty-returns/employerReturn")
    payload = {
        "returnReference": "234567897651",
        "employerAccountNumber": "5205098",
        "year": 2025,
        "month": "03",
        "ssn": "307484332",
        "nrc": "445362/67/1",
        "surname": "BANDA",
        "firstName": "BUUMBA",
        "otherName": "",
        "dob": "03/23/1970",
        "employeeGrossPay": 20000,
        "employerShare": 1000,
        "employeeShare": 1000
        }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=50)
        res.raise_for_status()

        return res.json()
        # member_data = res.json().get("data", {})
        # return NAPSA_CLIENT_INSTANCE.send_response(
        #     status="success",
        #     message="Member details retrieved successfully",
        #     data=member_data,
        #     status_code=200,
        #     http_status=200
        # )
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
