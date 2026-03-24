from frappe.utils import get_site_path
import frappe
import os



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
    
    def GetDefaultShiftStart(self):
        return "09:00:00"
    
    def GetDefaultShiftEnd(self):
        return "17:00:00"
    
    
    def GetCompanyId(self):
        companyId = frappe.conf.default_company_id

        if not companyId:
            return self.send_response(
                status="fail",
                message="Default Company ID is not set in config",
                status_code=400,
                http_status=400
            )

        return companyId
    
    def GetDefaultSiteName(self):
        site_name = frappe.conf.default_site_name
        if not site_name:
            return self.send_response(
                status="fail",
                message="Default site name is not set",
                status_code=400,
                http_status=400
            )

        return site_name
    
    def GetCompany(self):
        return frappe.get_doc(
            "Company",
            {"custom_company_id":  self.GetCompanyId()}
        )
    
    def GetCompanyLogoPath(self):
        return frappe.db.get_value(
            "Company",
            {"custom_company_id": self.GetCompanyId()},
            "company_logo"
        ) or ""
        
    def GetLogoFullPath(self):
        path = self.GetCompanyLogoPath()

        if not path:
            return None

        return os.path.join(
            get_site_path("public"),
            path.replace("/files/", "files/")
        )
    
    def GetLoggedInUser(self):
        return frappe.session.user