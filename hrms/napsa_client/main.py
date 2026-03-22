import frappe

EMPLOYER_ACCOUNT_NUMBER = "5205098"
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
            
            
    def send_response_list(self, status="success", message="", data=None, status_code=200, http_status=200):
        response_payload = {
            "status_code": status_code,
            "status": status,
            "message": message
        }

        if data is not None:
            if isinstance(data, dict) and "success" in data and "data" in data:
                response_payload["data"] = data["data"]
                response_payload["pagination"] = data.get("pagination", {})
            else:
                response_payload["data"] = data

        frappe.local.response = frappe._dict(response_payload)
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
    
    def get_approver_name(self):
        return "timeastw@gmail.com"
    
    def getAllAllowedLeaveTypes(self):
        leaves = frappe.get_all("Leave Type", pluck="name")
        return leaves
    
    def CalculateBasicBasedOnGrosssPay(self, grossPay):
        basicPay = grossPay / 1.4
        return basicPay
    
    def CalculateSalaryFromBasic(self, base):
        base = float(base or 0)

        transport = base * 0.10
        housing = base * 0.30

        gross = base + transport + housing
        return gross
    
    def GetPaymentTypes(self):
        return ["Cash", "Mobile Money", "Bank Transfer"]
    
    def GetPaymentValidations(self, data):
        return {
            "Cash": [
                (data.get("PaymentCashPersonFullName"), "Cash person full name"),
                (data.get("PaymentCashPersonId"), "Cash person ID"),
            ],
            "Mobile Money": [
                (data.get("PaymentMobileMoneyFullName"), "Mobile money full name"),
                (data.get("PaymentMobileMoneyPhone"), "Mobile money phone"),
                (data.get("PaymentMobileMoneyMnoType"), "Mobile money MNO type"),
            ],
            "Bank Transfer": [
                (data.get("AccountName"), "Account name"),
                (data.get("AccountNumber"), "Account number"),
                (data.get("BankName"), "Bank name"),
            ],
        }
        
        
    def GetStaticDate(self):
        return "1964-01-01"