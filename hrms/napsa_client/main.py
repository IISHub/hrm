import frappe

EMPLOYER_ACCOUNT_NUMBER = "5205743"
class NapsaClient():
    def __init__(self):
        self.EMPLOYER_ACCOUNT_NUMBER = EMPLOYER_ACCOUNT_NUMBER
        
        
    def send_response(self, status="success", message="", data=None, status_code = None , http_status=200):

        if  not data:
            frappe.local.response = frappe._dict({

                "status_code": status_code, 
                "status": status,
                "message": message,
            })
            frappe.local.response.http_status_code = http_status

        else:
            frappe.local.response = frappe._dict({

                "status_code": status_code, 
                "status": status,
                "message": message,
                "data": data
            })
            frappe.local.response.http_status_code = http_status

    def get_saved_token(self):
        token = frappe.db.get_value("Napsa Keys", {}, "token")
        if not token:
            self.send_response(
                status="fail",
                message="Token not found",
                status_code=400,
                http_status=400
            )
        return token
    
    def get_employeer_account(self):
        return self.EMPLOYER_ACCOUNT_NUMBER
    