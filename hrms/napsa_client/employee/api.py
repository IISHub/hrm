from hrms.napsa_client.save_files.save import save_file
from hrms.napsa_client.main import NapsaClient
from urllib.parse import urljoin
from frappe import _
import frappe



NAPSA_CLIENT_INSTANCE = NapsaClient()

import frappe
from frappe import _

def generate_employee_id():
    last_id = frappe.db.sql("""
        SELECT custom_id
        FROM `tabEmployee`
        WHERE custom_id IS NOT NULL
        ORDER BY CAST(custom_id AS UNSIGNED) DESC
        LIMIT 1
    """, as_dict=True)

    if last_id and str(last_id[0]["custom_id"]).isdigit():
        last_num = int(last_id[0]["custom_id"])
    else:
        last_num = 0

    return last_num + 1

FIELD_MAP = {
    "Email": "personal_email",
    "CompanyEmail": "company_email",
    "PhoneNumber": "cell_number",
    "AlternatePhone": "custom_alternate_phone",
    "TpinId": "custom_tax_payer_indentification_number",
    "NrcId": "custom_national_registration_number",
    "NhimaHealthInsurance": "custom_nhima_health_insurance_number",
    "SocialSecurityNapsa": "custom_social_security_number",
    "AccountNumber": "bank_ac_no",
}

def validate_unique_employee_fields(data, employee_name=None):
    for api_field, employee_field in FIELD_MAP.items():
        value = data.get(api_field)

        if not value:
            continue

        filters = {employee_field: value}

        if employee_name:
            filters["name"] = ["!=", employee_name]

        if frappe.db.exists("Employee", filters):
            
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="sucesss", 
                message=f"{api_field} '{value}' already exists", 
                data=[], 
                status_code=400, 
                http_status=400
            )



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
    CompanyEmail = data.get("CompanyEmail")
    MaritalStatus = data.get("MaritalStatus")
    PhoneNumber = data.get("PhoneNumber")
    AlternatePhone = data.get("AlternatePhone")
    JobTitle = data.get("JobTitle")
    EmployeeType = data.get("EmployeeType")
    AccountType = data.get("AccountType")
    BankName = data.get("BankName")
    AccountName = data.get("AccountName")
    AccountNumber = data.get("AccountNumber")
    BranchCode = data.get("BranchCode")
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
    MealAllowance = data.get("MealAllowance")
    TransportAllowance = data.get("TransportAllowance")
    otherAllowances = data.get("otherAllowances")
    GrossSalary = data.get("GrossSalary")
    
    if not FirstName:
        return NAPSA_CLIENT_INSTANCE.send_response(status="fail", message="First name is required", status_code=400, http_status=400)
    if not LastName:
        return NAPSA_CLIENT_INSTANCE.send_response(status="fail", message="Last name is required", status_code=400, http_status=400)
    if not EngagementDate:
        return NAPSA_CLIENT_INSTANCE.send_response(status="fail", message="Engagement date is required", status_code=400, http_status=400)
    if not Dob:
        return NAPSA_CLIENT_INSTANCE.send_response(status="fail", message="Date of birth is required", status_code=400, http_status=400)
    if not Gender:
        return NAPSA_CLIENT_INSTANCE.send_response(status="fail", message="Gender is required", status_code=400, http_status=400)
    if not NrcId:
        return NAPSA_CLIENT_INSTANCE.send_response(status="fail", message="NRC is required", status_code=400, http_status=400)
    if not TpinId:
        return NAPSA_CLIENT_INSTANCE.send_response(status="fail", message="TPIN is required", status_code=400, http_status=400)
    if not SocialSecurityNapsa:
        return NAPSA_CLIENT_INSTANCE.send_response(status="fail", message="Social Security NAPSA is required", status_code=400, http_status=400)
    if not NhimaHealthInsurance:
        return NAPSA_CLIENT_INSTANCE.send_response(status="fail", message="NHIMA number is required", status_code=400, http_status=400)
    if not PhoneNumber:
        return NAPSA_CLIENT_INSTANCE.send_response(status="fail", message="Phone number is required", status_code=400, http_status=400)
    if not Email:
        return NAPSA_CLIENT_INSTANCE.send_response(status="fail", message="Email is required", status_code=400, http_status=400)
    if not department_label:
        return NAPSA_CLIENT_INSTANCE.send_response(status="fail", message="Department is required", status_code=400, http_status=400)
    if not JobTitle:
        return NAPSA_CLIENT_INSTANCE.send_response(status="fail", message="Job title is required", status_code=400, http_status=400)

    
    existing_employee = frappe.db.get_value("Employee", {"personal_email": Email}, "name")
    if existing_employee:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"Personal Email {Email} already exists.",
            status_code=400,
            http_status=400
        )
        
    existing_employee = frappe.db.get_value("Employee", {"company_email": CompanyEmail}, "name")
    if existing_employee:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"Company Email {CompanyEmail} already exists.",
            status_code=400,
            http_status=400
        )

    existing_employee = frappe.db.get_value("Employee", {"cell_number": PhoneNumber}, "name")
    if existing_employee:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"Phone Number {PhoneNumber} already exists.",
            status_code=400,
            http_status=400
        )
        
    existing_employee = frappe.db.get_value("Employee", {"custom_alternate_phone": AlternatePhone}, "name")
    if existing_employee:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"Alternate Phone {AlternatePhone} already exists.",
            status_code=400,
            http_status=400
        )
        
    existing_employee = frappe.db.get_value("Employee", {"custom_tax_payer_indentification_number": TpinId}, "name")
    if existing_employee:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"TPIN {TpinId} already exists.",
            status_code=400,
            http_status=400
        )
        
        
    existing_employee = frappe.db.get_value("Employee", {"custom_national_registration_number": NrcId}, "name")
    if existing_employee:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"NRC {NrcId} already exists.",
            status_code=400,
            http_status=400
        )
        
    existing_employee = frappe.db.get_value("Employee", {"custom_nhima_health_insurance_number": NhimaHealthInsurance}, "name")
    if existing_employee:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"NHIMA number {NhimaHealthInsurance} already exists.",
            status_code=400,
            http_status=400
        )
    
    existing_employee = frappe.db.get_value("Employee", {"custom_social_security_number": SocialSecurityNapsa}, "name")
    if existing_employee:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"NAPSA number {SocialSecurityNapsa} already exists.",
            status_code=400,
            http_status=400
        )
        
    
    existing_employee = frappe.db.get_value("Employee", {"bank_ac_no": AccountNumber}, "name")
    if existing_employee:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"Bank Account {AccountNumber} already exists.",
            status_code=400,
            http_status=400
        )


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

    employee_id = generate_employee_id()
    employee = frappe.get_doc({
        "doctype": "Employee",
        "custom_id": employee_id,
        "first_name": FirstName,
        "last_name": LastName,
        "middle_name": OtherNames,
        "gender": Gender,
        "date_of_birth": Dob,
        "date_of_joining": EngagementDate,
        "personal_email": Email,
        "company_email": CompanyEmail,
        "cell_number": PhoneNumber,
        "custom_alternate_phone": AlternatePhone,
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
        "custom_bank_account_type": AccountType,
        "bank_name": BankName,
        "custom_accountname": AccountName,
        "bank_ac_no": AccountNumber,
        "custom_bank_branch_code": BranchCode,
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
        "custom_meal_allowance": MealAllowance,
        "custom_gross_salary": GrossSalary,
        "custom_nrc": NRC_DOCUMENT_URL,
        "custom_cv": CV_DOCUMENT_URL,
        "custom_educationcertificates": CV_EDUCERT_URL,
        "custom_policereport": POLICE_REPORT_DOC_URL
    })

    employee.insert(ignore_permissions=True)
    frappe.db.commit()

    return NAPSA_CLIENT_INSTANCE.send_response(status="sucesss", message="Employee added successfully", data=[], status_code=201, http_status=201)


@frappe.whitelist(allow_guest=True)
def get_all_employees(page=None, page_size=None):
    try:
        page = int(page) if page else 1
        page_size = int(page_size) if page_size else 10
    except ValueError:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="page and page_size must be integers",
            status_code=400,
            http_status=400
        )

    # Ensure sensible pagination values
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
    if page_size > 100:
        page_size = 100

    offset = (page - 1) * page_size
    total_employees = frappe.db.count("Employee")

    employees = frappe.get_all(
        "Employee",
        fields=[
            "custom_id as id",
            "first_name",
            "middle_name",
            "last_name",
            "custom_jobtitle as jobTitle",
            "department",
            "custom_work_location as location",
            "status"
        ],
        limit_start=offset,
        limit_page_length=page_size,
        order_by="creation desc"
    )

    data = []
    for emp in employees:
        full_name = " ".join(filter(None, [
            emp.get("first_name"),
            emp.get("middle_name"),
            emp.get("last_name")
        ]))

        # Fetch human-readable department name
        department_label = frappe.db.get_value(
            "Department",
            emp.get("department"),
            "department_name"
        ) or ""

        data.append({
            "id": emp.get("id"),
            "name": full_name,
            "jobTitle": emp.get("jobTitle"),
            "department": department_label, 
            "location": emp.get("location"),
            "status": emp.get("status")
        })

    summary = {
        "totalEmployees": total_employees,
        "active": frappe.db.count("Employee", {"status": "Active"}),
        "onLeave": frappe.db.count("Employee", {"status": "On Leave"}),
        "inactive": frappe.db.count("Employee", {"status": "Inactive"})
    }


    locations = frappe.db.sql("""
        SELECT DISTINCT custom_work_location
        FROM tabEmployee
        WHERE custom_work_location IS NOT NULL
    """, pluck=True)

    statuses = frappe.db.sql("""
        SELECT DISTINCT status
        FROM tabEmployee
        WHERE status IS NOT NULL
    """, pluck=True)

    returned = len(data)
    remaining = max(total_employees - (offset + returned), 0)

    pagination = {
        "page": page,
        "page_size": page_size,
        "returned": returned,
        "remaining": remaining,
        "total": total_employees
    }

    return NAPSA_CLIENT_INSTANCE.send_response(
        status="success",
        message="Employees fetched successfully",
        data={
            "summary": summary,
            "pagination": pagination,
            "locations": locations,
            "statuses": statuses,
            "employees": data
        },
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
    employee_name = frappe.db.get_value(
        "Employee",
        {"custom_id": employee_id},
        "name"
    )

    if not employee_name:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Employee not found",
            status_code=404,
            http_status=404
        )

    employee = frappe.get_doc("Employee", employee_name)

    department_name = employee.department if employee.department else None
    shift_name = employee.default_shift if employee.default_shift else None

    response_data = {
        "id": str(employee.custom_id),
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
            "alternatePhone": employee.custom_alternate_phone,
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
            "grossSalary": employee.custom_gross_salary,
            "currency": employee.salary_currency,
            "paymentFrequency": getattr(employee, "custom_payment_frequency", None),
            "paymentMethod": employee.custom_payment_method,
            "salaryBreakdown": {
                "basicSalary": employee.custom_basic_salary,
                "housingAllowance": employee.custom_housing_allowance,
                "transportAllowance": employee.custom_transport_allowance,
                "mealAllowance": employee.custom_meal_allowance,
                "otherAllowances": employee.custom_otherallowances
            },
            "statutoryDeductions": {
                "napsaEmployeeRate": getattr(employee, "custom_napsa_employee_rate", 5),
                "napsaEmployerRate": getattr(employee, "custom_napsa_employer_rate", 5),
                "nhimaRate": getattr(employee, "custom_nhima_rate", 2),
                "payeAmount": getattr(employee, "custom_paye_amount", 0)
            },
            "bankAccount": {
                "accountNumber": employee.bank_ac_no,
                "bankName": employee.bank_name,
                "branchCode": employee.custom_bank_branch_code,
                "accountType": employee.custom_bank_account_type
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

    employee_name = frappe.db.get_value(
        "Employee",
        {"custom_id": employee_id},
        "name"
    )

    if not employee_name:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"Employee {employee_id} not found",
            status_code=404,
            http_status=404
        )

    try:
        frappe.delete_doc(
            doctype="Employee",
            name=employee_name,
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
