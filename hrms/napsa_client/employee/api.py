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
    verifiedFromSource = data.get("verifiedFromSource")
    addressStreet = data.get("addressStreet")
    addressCity = data.get("addressCity")
    addressProvince = data.get("addressProvince")
    department_label = data.get("Department")
    addressPostalCode = data.get("addressPostalCode")
    addressCountry = data.get("addressCountry")
    emergencyContactName = data.get("emergencyContactName")
    emergencyContactPhone = data.get("emergencyContactPhone")
    emergencyContactRelationship = data.get("emergencyContactRelationship")
    shift = data.get("shift")
    reportingManager = data.get("reportingManager")
    probationPeriod = data.get("probationPeriod")
    contractEndDate = data.get("contractEndDate")
    workLocation = data.get("workLocation")
    workAddress = data.get("workAddress")
    weeklyScheduleMonday = data.get("weeklyScheduleMonday")
    weeklyScheduleTuesday = data.get("weeklyScheduleTuesday")
    weeklyScheduleWednesday = data.get("weeklyScheduleWednesday")
    weeklyScheduleThursday = data.get("weeklyScheduleThursday")
    weeklyScheduleFriday = data.get("weeklyScheduleFriday")
    weeklyScheduleSaturday = data.get("weeklyScheduleSaturday")
    weeklyScheduleSunday = data.get("weeklyScheduleSunday")
    currency = data.get("currency")
    PaymentFrequency = data.get("PaymentFrequency")
    BasicSalary = data.get("BasicSalary")
    HousingAllowance = data.get("HousingAllowance")
    TransportAllowance = data.get("TransportAllowance")
    otherAllowances = data.get("otherAllowances")
    
    shift_name = shift 
    shift_id = None

    if shift_name:
        shift_id = frappe.db.get_value(
            "Shift Type",
            {"name": shift_name},
            "name"
        )

        if not shift_id:
            shift_doc = frappe.get_doc({
                "doctype": "Shift Type",
                "name": shift_name,
                "start_time": "09:00:00",
                "end_time": "17:00:00",
                "enable_auto_attendance": 0
            })
            shift_doc.insert(ignore_permissions=True)
            shift_id = shift_doc.name
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

    print("FILES RECEIVED")

    def print_file(label, file):
        if file:
            print(f"{label}: {file.filename} ({file.content_type})")
        else:
            print(f"{label}: NOT PROVIDED")

    print_file("NRC", NRC_DOC)
    print_file("CV", CV_DOC)
    print_file("Education Certificates", EDUCERT_DOC)
    print_file("Police Report", POLICE_REPORT_DOC)

    
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
        "custom_verifiedfromsource": verifiedFromSource,
        "custom_address_street": addressStreet,
        "custom_address_city": addressCity,
        "custom_address_province": addressProvince,
        "custom_address_postal_code": addressPostalCode,
        "custom_address_country": addressCountry,
        "custom_emergency_contact_name": emergencyContactName,
        "custom_emergency_contact_phone": emergencyContactPhone,
        "custom_emergency_contact_relationship": emergencyContactRelationship,
        "reports_to": reportingManager,
        "default_shift": shift_id,
        "custom_probation_period": probationPeriod,
        "custom_work_location": workLocation,
        "custom_work_address": workAddress,
        "contract_end_date": contractEndDate,
        "custom_weekly_schedule_monday": weeklyScheduleMonday,
        "custom_weekly_schedule_tuesday": weeklyScheduleTuesday,
        "custom_weekly_schedule_wednesday": weeklyScheduleWednesday,
        "custom_weekly_schedule_thursday": weeklyScheduleThursday,
        "custom_weekly_schedule_friday": weeklyScheduleFriday,
        "custom_weekly_schedule_saturday": weeklyScheduleSaturday,
        "custom_weekly_schedule_sunday": weeklyScheduleSunday,
        "salary_currency": currency,
        "custom_payment_frequency": PaymentFrequency,
        "custom_basic_salary": BasicSalary,
        "custom_housing_allowance": HousingAllowance,
        "custom_transport_allowance": TransportAllowance,
        "custom_otherallowances": otherAllowances,
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
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="error",
            message="Employee id required",
            status_code=400,
            http_status=400
        )
    employee = frappe.get_doc("Employee", employee_id)
    department_name = employee.department if employee.department else None
    shift_name = employee.default_shift if employee.default_shift else None

    response_data = {
        "id": str(employee.name),
        "status": employee.status,
        "identityInfo": {
            "nrc": employee.custom_national_registration_number,
            "ssn": employee.custom_social_security_number,
            "verifiedFromSource": employee.custom_verifiedfromsource
        },
        "personalInfo": {
            "firstName": employee.first_name,
            "middleName": employee.middle_name,
            "lastName": employee.last_name,
            "dateOfBirth": str(employee.date_of_birth),
            "gender": employee.gender,
            "nationality": getattr(employee, "nationality", "Zambian"),
            "maritalStatus": employee.marital_status
        },
        "contactInfo": {
            "email": employee.personal_email,
            "workEmail": getattr(employee, "company_email", None),
            "phone": employee.cell_number,
            "alternatePhone": getattr(employee, "alternate_phone", None),
            "address": {
                "street": employee.custom_address_street,
                "city": employee.custom_address_city,
                "province": employee.custom_address_province,
                "postalCode": employee.custom_address_postal_code,
                "country": employee.custom_address_country
            },
            "emergencyContact": {
                "name": employee.custom_emergency_contact_name,
                "phone": employee.custom_emergency_contact_phone,
                "relationship": employee.custom_emergency_contact_relationship
            }
        },
        "employmentInfo": {
            "employeeId": employee.employee_number or employee.name,
            "department": department_name,
            "designation": getattr(employee, "custom_jobtitle", None),
            "reportingManager": employee.reports_to,
            "employmentType": getattr(employee, "custom_employeetype", None),
            "joiningDate": str(employee.date_of_joining),
            "probationPeriod": getattr(employee, "custom_probation_period", None),
            "contractEndDate": str(employee.contract_end_date) if employee.contract_end_date else None,
            "workLocation": employee.custom_work_location,
            "workAddress": employee.custom_work_address,
            "shift": shift_name,
            "weeklySchedule": {
                "monday": employee.custom_weekly_schedule_monday,
                "tuesday": employee.custom_weekly_schedule_tuesday,
                "wednesday": employee.custom_weekly_schedule_wednesday,
                "thursday": employee.custom_weekly_schedule_thursday,
                "friday": employee.custom_weekly_schedule_friday,
                "saturday": employee.custom_weekly_schedule_saturday,
                "sunday": employee.custom_weekly_schedule_sunday
            }
        },
        "payrollInfo": {
            "grossSalary": getattr(employee, "gross_salary", None),
            "currency": employee.salary_currency,
            "paymentFrequency": getattr(employee, "custom_payment_frequency", None),
            "paymentMethod": employee.custom_payment_method,
            "salaryBreakdown": {
                "basicSalary": employee.custom_basic_salary,
                "housingAllowance": employee.custom_housing_allowance,
                "transportAllowance": employee.custom_transport_allowance,
                "mealAllowance": getattr(employee, "custom_meal_allowance", 0),
                "otherAllowances": employee.custom_otherallowances
            },
            "statutoryDeductions": {
                "napsaEmployeeRate": getattr(employee, "custom_napsa_employee_rate", 5),
                "napsaEmployerRate": getattr(employee, "custom_napsa_employer_rate", 5),
                "nhimaRate": getattr(employee, "custom_nhima_rate", 2),
                "payeAmount": getattr(employee, "custom_paye_amount", 0)
            },
            "bankAccount": {
                "accountNumber": employee.custom_accountnumber,
                "bankName": employee.custom_bankname,
                "branchCode": getattr(employee, "custom_branch_code", None),
                "accountType": employee.custom_accounttype
            }
        },
        "documents": {
            "nrcCopy": employee.custom_nrc,
            "cvCopy": employee.custom_cv,
            "educationCertificates": employee.custom_educationcertificates
        }
    }

    return NAPSA_CLIENT_INSTANCE.send_response(
        status="success",
        message="Employee fetched successfully",
        data=response_data,
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
            status="fail",
            message="Employee id is required",
            status_code=400,
            http_status=400
        )

    if not frappe.db.exists("Employee", employee_id):
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
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
            status="fail",
            message=str(e),
            status_code=500,
            http_status=500
        )
