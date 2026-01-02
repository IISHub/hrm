from hrms.napsa_client.save_files.save import save_file
from hrms.napsa_client.main import NapsaClient
from urllib.parse import urljoin
from frappe import _
import frappe



NAPSA_CLIENT_INSTANCE = NapsaClient()

import frappe
from frappe import _

@frappe.whitelist()
def create_employee():
    data = frappe.form_dict
    print("Data: ", data)
    FirstName = data.get("FirstName")
    LastName = data.get("LastName")
    OtherNames = data.get("OtherNames")
    EngagementDate = data.get("EngagementDate")
    Dob = data.get("Dob")
    Gender = data.get("Gender")
    Email = data.get("Email")
    MaritalStatus = data.get("MaritalStatus")
    PhoneNumber = data.get("PhoneNumber")
    JobTitle = data.get("JobTitle")
    EmployeeType = data.get("EmployeeType")
    AccountType = data.get("AccountType")
    BankName = data.get("BankName")
    AccountName = data.get("AccountName")
    AccountNumber = data.get("AccountNumber")
    PaymentMethod = data.get("PaymentMethod")
    SocialSecurityNapsa = data.get("SocialSecurityNapsa")
    NhimaHealthInsurance = data.get("NhimaHealthInsurance")
    NrcId = data.get("NrcId")
    TpinId = data.get("TpinId")
    CeilingYear = data.get("CeilingYear")
    CeilingAmount = data.get("CeilingAmount")


    department_label = data.get("Department")
    department_id = None

    if department_label:
        department_id = frappe.db.get_value(
            "Department",
            {"department_name": department_label},
            "name"
        )

        if not department_id:
            dept = frappe.get_doc({
                "doctype": "Department",
                "department_name": department_label,
                "company": frappe.defaults.get_user_default("Company")
            })
            dept.insert(ignore_permissions=True)
            department_id = dept.name

    NRC_DOC = frappe.local.request.files.get("Documents[NRC]")
    CV_DOC = frappe.local.request.files.get("Documents[CV]")
    EDUCERT_DOC = frappe.local.request.files.get("Documents[EducationCertificates]")
    POLICE_REPORT_DOC = frappe.local.request.files.get("Documents[PoliceReport]")
    
    NRC_DOCUMENT_URL = save_file(NRC_DOC, site_name="erpnext.localhost", folder_type="NRC_DOC")
    CV_DOCUMENT_URL = save_file(CV_DOC, site_name="erpnext.localhost", folder_type="CV_DOC")
    CV_EDUCERT_URL = save_file(EDUCERT_DOC, site_name="erpnext.localhost", folder_type="EDUCERT_DOC")
    POLICE_REPORT_DOC_URL = save_file(POLICE_REPORT_DOC, site_name="erpnext.localhost", folder_type="POLICE_REPORT_DOC")

    employee = frappe.get_doc({
        "doctype": "Employee",
        "first_name": FirstName,
        "last_name": LastName,
        "middle_name": OtherNames,
        "gender": Gender,
        "date_of_birth": Dob,
        "date_of_joining": EngagementDate,
        "personal_email": Email,
        "cell_number": PhoneNumber,
        "marital_status": MaritalStatus,
        "department": department_id,
        "custom_jobtitle": JobTitle,
        "custom_employeetype": EmployeeType,
        "custom_tax_payer_indentification_number": TpinId,
        "custom_national_registration_number": NrcId,
        "custom_nhima_health_insurance_number": NhimaHealthInsurance,
        "custom_social_security_number": SocialSecurityNapsa,
        "custom_ceiling_year": CeilingYear,
        "custom_ceiling_amount": CeilingAmount,
        "custom_payment_method": PaymentMethod,
        "custom_accounttype": AccountType,
        "custom_bankname": BankName,
        "custom_accountname": AccountName,
        "custom_accountnumber": AccountNumber,
        "custom_nrc": NRC_DOCUMENT_URL,
        "custom_cv": CV_DOCUMENT_URL,
        "custom_educationcertificates": CV_EDUCERT_URL,
        "custom_policereport": POLICE_REPORT_DOC_URL
    })

    employee.insert(ignore_permissions=True)
    frappe.db.commit()

    return NAPSA_CLIENT_INSTANCE.send_response(status="sucesss", message="Employee added successfully", data=[], status_code=201, http_status=201)

@frappe.whitelist()
def get_all_employees():
    data = []
    return NAPSA_CLIENT_INSTANCE.send_response(
        
        status="success",
        message="API fetch all employees reserved",
        data=data,
        status_code=200,
        http_status=200
    )
@frappe.whitelist()
def get_employee():
    data = frappe.form_dict
    employee_id = data.get("id")
    
    if not employee_id:
        NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Employee id required",
            status_code=400,
            http_status=400
        )
    return NAPSA_CLIENT_INSTANCE.send_response(
        status="success",
        message=f"API fetch employee {employee_id} reserved",
        status_code=200,
        http_status=200
    )


@frappe.whitelist()
def update_employee():
    data = frappe.form_dict
    employee_id = data.get("id")
    
    if not employee_id:
        NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message="Employee id required",
            status_code=400,
            http_status=400
        )
    return NAPSA_CLIENT_INSTANCE.send_response(
        status="success",
        message=f"API update employee {employee_id} reserved",
        status_code=200,
        http_status=200
    )


@frappe.whitelist()
def delete_employee():
    data = frappe.form_dict
    employee_id = data.get("id")

    if not employee_id:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message="Employee id is required",
            status_code=400,
            http_status=400
        )

    if not frappe.db.exists("Employee", employee_id):
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message=f"Employee {employee_id} not found",
            status_code=404,
            http_status=404
        )

    try:

        frappe.delete_doc(
            doctype="Employee",
            name=employee_id,
            force=1   
        )

        frappe.db.commit()

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message=f"Employee {employee_id} deleted successfully",
            status_code=200,
            http_status=200
        )

    except Exception as e:
        frappe.log_error(
            title="Delete Employee Error",
            message=frappe.get_traceback()
        )

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message=str(e),
            status_code=500,
            http_status=500
        )
