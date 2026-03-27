from frappe.utils import get_site_path
from decimal import Decimal, ROUND_HALF_UP
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
    
    def money(self, value):
        return value.quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)
    
    def money(self, value):
        return Decimal(value).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)

    def CalculateBasicBasedOnGrosssPay(self, grossPay):
        grossPay = Decimal(str(grossPay))
        basicPay = grossPay / Decimal("1.40")
        basic = basicPay.to_integral_value(rounding=ROUND_HALF_UP)
        print(f"Gross Pay: {grossPay} => Basic Pay: {basic}")
        return basic

    from decimal import Decimal, ROUND_HALF_UP

    def CalculateAllowancesAndDeductions(self, basic_input):
        basic = Decimal(str(basic_input))

        housing_allowance = (basic * Decimal('0.30')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        transport_allowance = (basic * Decimal('0.10')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        gross_pay = basic + housing_allowance + transport_allowance
        gross_whole = gross_pay.to_integral_value(rounding=ROUND_HALF_UP)

        diff = gross_whole - (basic + housing_allowance + transport_allowance).to_integral_value(rounding=ROUND_HALF_UP)
        transport_allowance += diff
        gross_pay = basic + housing_allowance + transport_allowance

        pensionable_earnings = gross_pay

        if pensionable_earnings >= Decimal("37236"):
            employee_napsa = 1862
        else:
            employee_napsa = (pensionable_earnings * Decimal("0.05")).to_integral_value(rounding=ROUND_HALF_UP)
        employer_napsa = employee_napsa

        # NHIMA
        employee_nhima = (basic * Decimal("0.01")).to_integral_value(rounding=ROUND_HALF_UP)
        employer_nhima = employee_nhima

        # PAYE
        gp = gross_pay.to_integral_value(rounding=ROUND_HALF_UP)
        if gp <= Decimal("5100"):
            paye = Decimal("0")
        elif gp <= Decimal("7100"):
            paye = ((gp - Decimal("5100")) * Decimal("0.20")).to_integral_value(rounding=ROUND_HALF_UP)
        elif gp <= Decimal("9200"):
            paye = (Decimal("2000") * Decimal("0.20") + (gp - Decimal("7100")) * Decimal("0.30")).to_integral_value(rounding=ROUND_HALF_UP)
        else:
            paye = (Decimal("2000") * Decimal("0.20") + Decimal("2100") * Decimal("0.30") + (gp - Decimal("9200")) * Decimal("0.37")).to_integral_value(rounding=ROUND_HALF_UP)

        result = {
            "BasicSalary": float(basic),
            "housing_allowance": int(housing_allowance.to_integral_value(rounding=ROUND_HALF_UP)),
            "transport_allowance": int(transport_allowance.to_integral_value(rounding=ROUND_HALF_UP)),
            "PensionableEarnings": int(pensionable_earnings.to_integral_value(rounding=ROUND_HALF_UP)),
            "employee_napsa": int(employee_napsa),
            "employer_napsa": int(employer_napsa),
            "employee_nhima": int(employee_nhima),
            "employer_nhima": int(employer_nhima),
            "gross_pay": int(gross_pay.to_integral_value(rounding=ROUND_HALF_UP)),
            "paye": int(paye)
        }

        print(result)
        return result
                        
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