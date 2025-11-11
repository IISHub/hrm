import uuid
from hrms.napsa_client.config.settings import NAPSA_BASE_URL, CLIENT_ID, USERNAME, PASSWORD
from frappe import _
import requests
import frappe


def save_new_token(token: str):
    napsa_name = frappe.db.get_value("Napsa Keys", {}, "name")
    if not napsa_name:
        frappe.throw("No Napsa Keys record found. Please create one first.")
    
    napsa_doc = frappe.get_doc("Napsa Keys", napsa_name)
    napsa_doc.token = token
    napsa_doc.save(ignore_permissions=True)
    frappe.db.commit()


@frappe.whitelist(allow_guest=False)
def get_token(mock: bool = False):
    try:
        if mock:
            random_token = uuid.uuid4()
            mock_data = {
                "statusCode": 200,
                "message": "Success",
                "success": True,
                "data": {
                    "expiresIn": 10800,
                    "tokenType": "bearer",
                    "accessToken": random_token,
                    "refreshToken": "MOCK_REFRESH_TOKEN_0987654321"
                }
            }
            access_token = mock_data["data"]["accessToken"]
            save_new_token(access_token)
            return access_token
        
        url = f"{NAPSA_BASE_URL}/central-authentication-integrations/auth/authenticate"
        payload = {"username": USERNAME, "password": PASSWORD}
        headers = {
            "Content-Type": "application/json",
            "clientId": CLIENT_ID,
            "grantType": "password",
            "scope": "*"
        }

        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()

        data = response.json()
        print(data)
        access_token = data.get("data", {}).get("accessToken")

        if not access_token:
            frappe.throw(_("Failed to retrieve access token from NAPSA response"))

        save_new_token(access_token)
        return access_token

    except requests.exceptions.RequestException as e:
        frappe.log_error(message=str(e), title="NAPSA Token Request Failed")
        frappe.throw(_("Error connecting to NAPSA API: {0}").format(str(e)))

    except Exception as e:
        frappe.log_error(message=str(e), title="NAPSA Token Retrieval Failed")
        frappe.throw(_("Unexpected error while retrieving NAPSA token: {0}").format(str(e)))
