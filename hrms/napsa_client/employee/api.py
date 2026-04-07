
from hrms.napsa_client.employee.employeeContract import createEmploymentContract
from hrms.napsa_client.save_files.save import save_file
from hrms.napsa_client.main import NapsaClient
from urllib.parse import urljoin
from datetime import datetime
from frappe import _
import random
import frappe
import math
import datetime



NAPSA_CLIENT_INSTANCE = NapsaClient()

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



@frappe.whitelist(allow_guest=False, methods=["POST"])
def create_employee():
    data = frappe.form_dict
    print("Data: ", data)
    FirstName = data.get("FirstName")
    LastName = data.get("LastName")
    OtherNames = data.get("OtherNames")
    MiddleName = data.get("MiddleName")
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
    PaymentMethod = data.get("PaymentMethod")
    AccountType = data.get("AccountType")
    BankName = data.get("BankName")
    AccountName = data.get("AccountName")
    AccountNumber = data.get("AccountNumber")
    BranchName = data.get("BranchName")
    BranchCode = data.get("BranchCode")
    PaymentCashFullname = data.get("PaymentCashPersonFullName")
    PaymentCashId = data.get("PaymentCashPersonId")
    PaymentMobileFullname = data.get("PaymentMobileMoneyFullName")
    PaymentMobilePhone = data.get("PaymentMobileMoneyPhone")
    PaymentMobileMno = data.get("PaymentMobileMoneyMnoType")
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
    probationPeriod = data.get("probationPeriod")
    contractStartDate = data.get("contractStartDate")
    contractEndDate = data.get("contractEndDate")
    contractTerms = data.get("contractTerms")
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
    Nationality = data.get("Nationality")
    SalaryStructure = data.get("SalaryStructure")
    BasicAmount = data.get("BasicAmount")
    status = data.get("status")
    
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

    if not EmployeeType:
        return NAPSA_CLIENT_INSTANCE.send_response(status="fail", message="Employee type is required", status_code=400, http_status=400)
    
    if not contractStartDate:
        contractStartDate = datetime.date.today().strftime("%Y-%m-%d")
        # return NAPSA_CLIENT_INSTANCE.send_response(status="fail", message="Contract start date is required", status_code=400, http_status=400)
    
    if EmployeeType != "Permanent" and not contractEndDate:
        return NAPSA_CLIENT_INSTANCE.send_response(status="fail", message="Contract end date is required for employee other than permanent employees", status_code=400, http_status=400)

    if not contractTerms:
        contractTerms = f"{EmployeeType} employment contract for {FirstName} {LastName}"
        # return NAPSA_CLIENT_INSTANCE.send_response(status="fail", message="Contract terms is required", status_code=400, http_status=400)

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
    
    if AlternatePhone:
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
        
    
    if AccountNumber:
        existing_employee = frappe.db.get_value("Employee", {"bank_ac_no": AccountNumber}, "name")
        if existing_employee:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message=f"Bank Account {AccountNumber} already exists.",
                status_code=400,
                http_status=400
            )
            
    
    ALLOWED_MARITAL_STATUS = {
        "",
        "Single",
        "Married",
        "Divorced",
        "Widowed",
    }
    
    if MaritalStatus not in ALLOWED_MARITAL_STATUS:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=(
                f'Marital Status cannot be "{MaritalStatus}". '
                f'It should be one of {", ".join([v or "Empty" for v in ALLOWED_MARITAL_STATUS])}'
            ),
            status_code=400,
            http_status=400
        )

    
    if not SalaryStructure:
        return NAPSA_CLIENT_INSTANCE.send_response(status="fail", message="Salary Structure is required", status_code=400, http_status=400)
    
    
    if SalaryStructure:
        if not frappe.db.exists("Salary Structure", SalaryStructure):
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message=f"Salary Structure '{SalaryStructure}' does not exist.",
                status_code=400,
                http_status=400
            )
            
    if not BasicAmount:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status = "fail",
            message = "Basic Amount must not be null",
            status_code = 400,
            http_status= 400,
        )

    
    availableTypeMethods = NAPSA_CLIENT_INSTANCE.GetPaymentTypes()

    if not PaymentMethod or PaymentMethod not in availableTypeMethods:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"Invalid payment method. Allowed values: {', '.join(availableTypeMethods)}",
            status_code=400,
            http_status=400,
        )

    validations = NAPSA_CLIENT_INSTANCE.GetPaymentValidations(data).get(PaymentMethod, [])
    for value, label in validations:
        if not value:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message=f"{label} is required for payment method '{PaymentMethod}'",
                status_code=400,
                http_status=400
            )
            
    DATE_FORMAT = "%Y-%m-%d"

    try:
        start = datetime.datetime.strptime(contractStartDate, DATE_FORMAT)
    except ValueError:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Invalid contract start date format. Expected YYYY-MM-DD.",
            status_code=400,
            http_status=400
        )

    if contractEndDate: 
        try:
            end = datetime.datetime.strptime(contractEndDate, DATE_FORMAT)
        except ValueError:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Invalid contract end date format. Expected YYYY-MM-DD.",
                status_code=400,
                http_status=400
            )

        if start > end:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Contract start date cannot be after end date.",
                status_code=400,
                http_status=400
            )

    
    errors = []

    if PaymentMethod == "Cash":
        if not data.get("PaymentCashPersonFullName"):
            errors.append("Cash person full name is required for Cash payments.")
        if not data.get("PaymentCashPersonId"):
            errors.append("Cash person ID is required for Cash payments.")
        if AccountNumber or data.get("BankName"):
            errors.append("Cash payment cannot have bank account details.")
        if data.get("PaymentMobileMoneyPhone"):
            errors.append("Cash payment cannot have mobile money details.")

    elif PaymentMethod == "Mobile Money":
        if not data.get("PaymentMobileMoneyFullName"):
            errors.append("Mobile money full name is required.")
        if not data.get("PaymentMobileMoneyPhone"):
            errors.append("Mobile money phone is required.")
        if not data.get("PaymentMobileMoneyMnoType"):
            errors.append("Mobile money MNO type is required.")
            
        if data.get("PaymentCashPersonFullName") or data.get("PaymentCashPersonId"):
            errors.append("Mobile Money payment cannot have cash person details.")
        if AccountNumber or data.get("BankName"):
            errors.append("Mobile Money payment cannot have bank account details.")

    elif PaymentMethod == "Bank Transfer":
        if not data.get("AccountName"):
            errors.append("Account name is required for Bank Transfer.")
        if not AccountNumber:
            errors.append("Account number is required for Bank Transfer.")
        if not data.get("BankName"):
            errors.append("Bank name is required for Bank Transfer.")
            
        if data.get("PaymentCashPersonFullName") or data.get("PaymentCashPersonId"):
            errors.append("Bank Transfer cannot have cash person details.")
        if data.get("PaymentMobileMoneyPhone"):
            errors.append("Bank Transfer cannot have mobile money details.")

    else:
        errors.append("Invalid PaymentType. Must be Cash, Mobile Money, or Bank Transfer.")

    if errors:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=", ".join(errors),
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
                "start_time": NAPSA_CLIENT_INSTANCE.GetDefaultShiftStart(),
                "end_time":  NAPSA_CLIENT_INSTANCE.GetDefaultShiftEnd(),
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
                "company": NAPSA_CLIENT_INSTANCE.GetCompany()
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

    
    NRC_DOCUMENT_URL = save_file(NRC_DOC, site_name=NAPSA_CLIENT_INSTANCE.GetDefaultSiteName(), folder_type="NRC_DOC")
    CV_DOCUMENT_URL = save_file(CV_DOC, site_name=NAPSA_CLIENT_INSTANCE.GetDefaultSiteName(), folder_type="CV_DOC")
    CV_EDUCERT_URL = save_file(EDUCERT_DOC, site_name=NAPSA_CLIENT_INSTANCE.GetDefaultSiteName(), folder_type="EDUCERT_DOC")
    POLICE_REPORT_DOC_URL = save_file(POLICE_REPORT_DOC, site_name=NAPSA_CLIENT_INSTANCE.GetDefaultSiteName(), folder_type="POLICE_REPORT_DOC")

    employee_id = generate_employee_id()
    date = NAPSA_CLIENT_INSTANCE.GetStaticDate()
    try: 
        employee = frappe.get_doc({
            "doctype": "Employee",
            "custom_id": employee_id,
            "first_name": FirstName,
            "last_name": LastName,
            "middle_name": OtherNames,
            "custom_other_name": MiddleName,
            "gender": Gender,
            "date_of_birth": date,
            "date_of_joining": date,
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
            "custom_accont_name": AccountName,
            "bank_ac_no": AccountNumber,
            "custom_bank_branch_name": BranchName,
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
            "custom_nationality": Nationality,
            "custom_nrc": NRC_DOCUMENT_URL,
            "custom_cv": CV_DOCUMENT_URL,
            "custom_educationcertificates": CV_EDUCERT_URL,
            "custom_policereport": POLICE_REPORT_DOC_URL,
            "custom_dob": Dob,
            "custom_doj": EngagementDate,
            "custom_payment_cash_full_name_": PaymentCashFullname,
            "custom_payment_cash_id": PaymentCashId,
            "custom_payment_mobile_full_name": PaymentMobileFullname,
            "custom_payment_mobile_phone": PaymentMobilePhone,
            "custom_payment_mobile_mno":  PaymentMobileMno,
            "status": status,
        })

        employee.insert(ignore_permissions=True)
        
        salaryStructureAssignment = frappe.get_doc({
            "doctype": "Salary Structure Assignment",
            "employee": employee.name,
            "salary_structure": SalaryStructure,
            "base":   BasicAmount,
            "from_date":  NAPSA_CLIENT_INSTANCE.GetStaticDate()
        })

        salaryStructureAssignment.insert(ignore_permissions=True)
        salaryStructureAssignment.submit()
        
        result = createEmploymentContract(employee, EmployeeType, contractStartDate, contractEndDate, contractTerms)
        if result["status"] != "success":

            frappe.db.rollback()
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message=f"Employee creation failed due to contract error: {contract_result['message']}",
                status_code=400,
                http_status=400
            )
                        

        frappe.db.commit()

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success", 
            message="Employee added successfully", 
            data=[],
            status_code=201, 
            http_status=201
        )
        
    except frappe.ValidationError as e:
        frappe.db.rollback()

        frappe.log_error(
            title="Validation Error During Employee Creation",
            message=frappe.get_traceback()
        )

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"Validation error: {str(e)}",
            status_code=400,
            http_status=400
        )

    except Exception as e:
        frappe.db.rollback()

        frappe.log_error(
            title="Employee Transaction Failed",
            message=frappe.get_traceback()
        )

    return NAPSA_CLIENT_INSTANCE.send_response(
        status="fail",
        message=f"Failed to create employee: {str(e)}",
        status_code=500,
        http_status=500
    )


@frappe.whitelist(allow_guest=False, methods=["GET"])
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

    page = max(page, 1)
    page_size = max(1, min(page_size, 100))
    offset = (page - 1) * page_size

    args = frappe.request.args
    filters = {}

    
    if args.get("status"):
        filters["status"] = args.get("status")

    if args.get("department"):
        filters["department"] = args.get("department")

    if args.get("jobTitle"):
        filters["custom_jobtitle"] = args.get("jobTitle")

    if args.get("workLocation"):
        filters["custom_work_location"] = args.get("workLocation")

    if args.get("custom_id"):
        filters["custom_id"] = args.get("custom_id")

    name = args.get("name")
    name_filters = []

    if name:
        name_filters = [
            ["Employee", "first_name", "like", f"%{name}%"],
            ["Employee", "middle_name", "like", f"%{name}%"],
            ["Employee", "last_name", "like", f"%{name}%"]
        ]

    if name:
        total_employees = len(
            frappe.get_all(
                "Employee",
                filters=filters,
                or_filters=name_filters,
                fields=["name"]
            )
        )
    else:
        total_employees = frappe.db.count("Employee", filters=filters)

    employees = frappe.get_all(
        "Employee",
        fields=[
            "name",
            "custom_id",
            "first_name",
            "middle_name",
            "last_name",
            "custom_jobtitle",
            "department",
            "custom_work_location",
            "status",
            "image"
        ],
        filters=filters,
        or_filters=name_filters if name else None,
        limit_start=offset,
        limit_page_length=page_size,
        order_by="creation desc"
    )

    data = []

    for emp in employees:
        full_name = " ".join(filter(None, [
            emp.first_name,
            emp.middle_name,
            emp.last_name
        ]))

        department_label = frappe.db.get_value(
            "Department",
            emp.department,
            "department_name"
        ) or ""

        assignment = frappe.db.get_value(
            "Salary Structure Assignment",
            {"employee": emp.name},
            ["base"],
            as_dict=True
        )

        base = float(assignment.base) if assignment and assignment.base else 0

        salary =  NAPSA_CLIENT_INSTANCE.CalculateSalaryFromBasic(base)

        data.append({
            "id": emp.custom_id,
            "employeeId": emp.name,
            "name": full_name,
            "jobTitle": emp.custom_jobtitle,
            "department": department_label,
            "workLocation": emp.custom_work_location,
            "grossSalary": salary,  
            "status": emp.status,
            "profilePicture": emp.image
        })

    summary = {
        "totalEmployees": total_employees,
        "active": frappe.db.count("Employee", {**filters, "status": "Active"}),
        "onLeave": frappe.db.count("Employee", {**filters, "status": "On Leave"}),
        "inactive": frappe.db.count("Employee", {**filters, "status": "Inactive"})
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

    total_pages = math.ceil(total_employees / page_size) if page_size else 0

    pagination = {
        "page": page,
        "page_size": page_size,
        "total": total_employees,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
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

    department_name = employee.department.split(" - ")[0] if employee.department else None
    shift_name = employee.default_shift if employee.default_shift else None
    
    employee_contracts = frappe.get_all(
        "Contract",
        filters={
            "party_name": employee.name,
        },
        fields=["name", "start_date", "end_date", "status", "contract_terms"]
    )
    
    documents = frappe.get_all(
        "HR Documents",
        filters={
            "parent_id": employee.custom_id, 
        },
        fields=["id", "description", "file"]
    )
    assignment = frappe.db.get_value(
        "Salary Structure Assignment",
        {"employee": employee.name},
        ["name", "base"],
        as_dict=True
    )

    existing_assignment = assignment.name if assignment else None
    base = assignment.base if assignment else 0

    payroll = NAPSA_CLIENT_INSTANCE.CalculateAllowancesAndDeductions(base)


    doc_list = []
    for doc in documents:
        doc_list.append({
            "id": doc.get("id"),
            "description": doc.get("description"),
            "file": doc.get("file")
        })

    if not doc_list:
        doc_list = []


    response_data = {
        "id": str(employee.custom_id),
        "employeeId": employee.employee_number or employee.name,
        "status": employee.status,
        "identityInfo": {
            "NrcId": employee.custom_national_registration_number,
            "SocialSecurityNapsa": employee.custom_social_security_number,
            "NhimaHealthInsurance": employee.custom_nhima_health_insurance_number,
            "TpinId": employee.custom_tax_payer_indentification_number,
            "verifiedFromSource": employee.custom_verifiedfromsource
        },
        "personalInfo": {
            "FirstName": employee.first_name,
            "OtherNames": employee.middle_name,
            "MiddleName": employee.custom_other_name,
            "LastName": employee.last_name,
            "Dob": str(employee.custom_dob),
            "Gender": employee.gender,
            "Nationality": employee.custom_nationality,
            "maritalStatus": employee.marital_status
        },
        "contactInfo": {
            "Email": employee.personal_email,
            "workEmail": getattr(employee, "company_email", None),
            "phoneNumber": employee.cell_number,
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
            "Department":  department_name,
            "JobTitle": getattr(employee, "custom_jobtitle", None),
            "reportingManager": employee.reports_to,
            "EmployeeType": getattr(employee, "custom_employeetype", None),
            "joiningDate": str(employee.custom_doj),
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
            "grossSalary": payroll["gross_pay"],
            "currency": employee.salary_currency,
            "paymentFrequency": getattr(employee, "custom_payment_frequency", None),
            "paymentMethod": employee.custom_payment_method,
            "salaryBreakdown": {
                "BasicSalary": base,
                "HousingAllowance": payroll["housing_allowance"],
                "TransportAllowance": payroll["transport_allowance"]

            },
            "statutoryDeductions": {
                "EmployeeNapsa": payroll["employee_napsa"],
                "EmployeerNapsa": payroll["employer_napsa"],
                "EmployeeNhima": payroll["employee_nhima"],
                "EmployeerNhima": payroll["employer_nhima"],
                "PayAsYouEarn": payroll["paye"]
            },
            "bankAccount": {
                "AccountNumber": employee.bank_ac_no,
                "AccountName": employee.custom_accont_name,
                "BankName": employee.bank_name,
                "BranchName": employee.custom_bank_branch_name,
                "branchCode": employee.custom_bank_branch_code,
                "AccountType": employee.custom_bank_account_type
            },
            "Cash": {
                "PaymentCashPersonFullName": employee.custom_payment_cash_full_name_,
                "PaymentCashPersonId": employee.custom_payment_cash_id,
            },
            "MobileMoney": {
                "PaymentMobileMoneyFullName": employee.custom_payment_mobile_full_name,
                "PaymentMobileMoneyPhone": employee.custom_payment_mobile_phone,
                "PaymentMobileMoneyMnoType": employee.custom_payment_mobile_mno,
                
            }
        
        },
        "documents": doc_list,
        "ProfilePicture": employee.image,
        "contracts": employee_contracts
    }

    return NAPSA_CLIENT_INSTANCE.send_response(
        status="success",
        message="Employee fetched successfully",
        data=response_data,
        status_code=200,
        http_status=200
    )


@frappe.whitelist(allow_guest=False, methods=["PATCH"])
def update_employee():
    data = frappe.form_dict
    id = data.get("id")

    if not id:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Employee id is required",
            status_code=400,
            http_status=400
        )

    employee_name = frappe.db.get_value(
        "Employee",
        {"custom_id": id},
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
    EngagementDate = NAPSA_CLIENT_INSTANCE.GetStaticDate()
    Email = data.get("Email")
    Dob = data.get("Dob")
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
    Nationality = data.get("Nationality")
    status = data.get("status")
    SalaryStructure = data.get("SalaryStructure")
    BasicAmount = data.get("BasicAmount")
    BranchName = data.get("BranchName")

    if reportingManager:
        if not frappe.db.exists("Employee", {"name": reportingManager}):
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message= f"Reporting Manager '{reportingManager}' does not exist.",
                status_code=400,
                http_status=400
            )
    def check_unique(field, value, label):
        if value and frappe.db.exists(
            "Employee",
            {field: value, "name": ["!=", employee.name]}
        ):
            frappe.throw(f"{label} {value} already exists")

    check_unique("personal_email", Email, "Email")
    check_unique("company_email", CompanyEmail, "Company Email")
    check_unique("cell_number", PhoneNumber, "Phone Number")
    check_unique("custom_alternate_phone", AlternatePhone, "Alternate Phone")
    check_unique("custom_tax_payer_indentification_number", TpinId, "TPIN")
    check_unique("custom_national_registration_number", NrcId, "NRC")
    check_unique("custom_nhima_health_insurance_number", NhimaHealthInsurance, "NHIMA")
    check_unique("custom_social_security_number", SocialSecurityNapsa, "NAPSA")
    
    ALLOWED_MARITAL_STATUS = {
        "",
        "Single",
        "Married",
        "Divorced",
        "Widowed",
    }
    
    if MaritalStatus:
        if MaritalStatus not in ALLOWED_MARITAL_STATUS:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message=(
                    f'Marital Status cannot be "{MaritalStatus}". '
                    f'It should be one of {", ".join([v or "Empty" for v in ALLOWED_MARITAL_STATUS])}'
                ),
                status_code=400,
                http_status=400
            )


    if shift:
        shift_id = frappe.db.get_value("Shift Type", {"name": shift}, "name")
        if not shift_id:
            shift_doc = frappe.get_doc({
                "doctype": "Shift Type",
                "name": shift,
                "start_time": NAPSA_CLIENT_INSTANCE.GetDefaultShiftStart(),
                "end_time":  NAPSA_CLIENT_INSTANCE.GetDefaultShiftEnd(),
                "enable_auto_attendance": 0
            })
            shift_doc.insert(ignore_permissions=True)
            shift_id = shift_doc.name
        employee.default_shift = shift_id


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

        employee.department = department_id


    field_map = {
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
        "custom_accont_name": AccountName,
        "bank_ac_no": AccountNumber,
        "custom_bank_branch_code": BranchCode,
        "custom_bank_branch_name": BranchName,
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
        # "default_shift": shift_id,
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
        "custom_gross_salary": BasicAmount,
        "custom_nationality": Nationality,
        "custom_dob": Dob,
        "status": status,
    }

    for field, value in field_map.items():
        if value is not None:
            employee.set(field, value)

 
    files = {
        "custom_nrc": ("Documents[NRC]", "NRC_DOC"),
        "custom_cv": ("Documents[CV]", "CV_DOC"),
        "custom_educationcertificates": ("Documents[EducationCertificates]", "EDUCERT_DOC"),
        "custom_policereport": ("Documents[PoliceReport]", "POLICE_REPORT_DOC"),
    }

    for field, (file_key, folder) in files.items():
        file = frappe.local.request.files.get(file_key)
        if file:
            employee.set(field, save_file(file, NAPSA_CLIENT_INSTANCE.GetDefaultSiteName(), folder))

    employee.save(ignore_permissions=True)
    frappe.db.commit()
    
    if SalaryStructure or BasicAmount:
        assignment_name = frappe.db.get_value("Salary Structure Assignment", {"employee": employee.name}, "name")
        try:
            if assignment_name:
                assignment = frappe.get_doc("Salary Structure Assignment", assignment_name)
                if assignment.docstatus == 1:
                    assignment.cancel()
                    frappe.db.commit()
                    frappe.delete_doc("Salary Structure Assignment", assignment_name, force=True)
                    frappe.db.commit()

                    new_assignment = frappe.get_doc({
                        "doctype": "Salary Structure Assignment",
                        "employee": employee.name,
                        "salary_structure": SalaryStructure or assignment.salary_structure,
                        "base": BasicAmount or assignment.base,
                        "from_date":  NAPSA_CLIENT_INSTANCE.GetStaticDate(),
                        "company": assignment.company
                    })
                    new_assignment.insert()
                    new_assignment.submit()
                    frappe.db.commit()
                else:

                    if SalaryStructure:
                        if not frappe.db.exists("Salary Structure", SalaryStructure):
                            return NAPSA_CLIENT_INSTANCE.send_response(
                                status="fail",
                                message=f"Salary Structure '{SalaryStructure}' does not exist.",
                                status_code=404,
                                http_status=404
                            )
                        assignment.salary_structure = SalaryStructure
                    if BasicAmount is not None:
                        assignment.base = BasicAmount
                    assignment.save(ignore_permissions=True)
                    frappe.db.commit()
            else:
                if not SalaryStructure:
                    return NAPSA_CLIENT_INSTANCE.send_response(
                        status="fail",
                        message="Salary Structure is required to create a new assignment",
                        status_code=400,
                        http_status=400
                    )
                new_assignment = frappe.get_doc({
                    "doctype": "Salary Structure Assignment",
                    "employee": employee.name,
                    "salary_structure": SalaryStructure,
                    "base": BasicSalary,
                    "from_date": NAPSA_CLIENT_INSTANCE.GetStaticDate(),
                    "company": employee.company
                })
                new_assignment.insert()
                new_assignment.submit()
                frappe.db.commit()

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Update Salary/Base Error")
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message=f"Error updating Salary Structure or Base: {str(e)}",
                status_code=500,
                http_status=500
            )

    return NAPSA_CLIENT_INSTANCE.send_response(
        status="success",
        message="Employee updated successfully",
        status_code=200,
        http_status=200
    )


@frappe.whitelist(allow_guest=False, methods=["PUT"])
def disable_employee():
    data = frappe.form_dict
    employee_id = data.get("id") 

    if not employee_id:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Employee id is required",
            status_code=400,
            http_status=400
        )

    employee = frappe.db.get_value(
        "Employee",
        {"custom_id": employee_id},
        ["name", "status"],
        as_dict=True
    )

    if not employee:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"Employee {employee_id} not found",
            status_code=404,
            http_status=404
        )

    if employee.status == "Inactive":
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"Employee {employee_id} is already inactive",
            status_code=400,
            http_status=400
        )

    try:
        frappe.db.set_value(
            "Employee",
            employee.name,
            "status",
            "Inactive"
        )

        frappe.db.commit()

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message=f"Employee {employee_id} disabled successfully",
            status_code=200,
            http_status=200
        )

    except Exception as e:
        frappe.log_error(
            title="Disable Employee Error",
            message=frappe.get_traceback()
        )

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=str(e),
            status_code=500,
            http_status=500
        )


@frappe.whitelist(allow_guest=False, methods=["PUT"])
def enable_employee():
    data = frappe.form_dict
    employee_id = data.get("id") 

    if not employee_id:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Employee id is required",
            status_code=400,
            http_status=400
        )

    employee = frappe.db.get_value(
        "Employee",
        {"custom_id": employee_id},
        ["name", "status"],
        as_dict=True
    )

    if not employee:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"Employee {employee_id} not found",
            status_code=404,
            http_status=404
        )

    if employee.status == "Active":
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"Employee {employee_id} is already active",
            status_code=400,
            http_status=400
        )

    try:
        frappe.db.set_value(
            "Employee",
            employee.name,
            "status",
            "Active"
        )

        frappe.db.commit()

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="success",
            message=f"Employee {employee_id} re-enabled successfully",
            status_code=200,
            http_status=200
        )

    except Exception as e:
        frappe.log_error(
            title="Enable Employee Error",
            message=frappe.get_traceback()
        )

        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=str(e),
            status_code=500,
            http_status=500
        )
        
@frappe.whitelist(allow_guest=False)
def manage_employee_documents():
    data = frappe.local.form_dict
    files = frappe.local.request.files

    parent_id = data.get("employeeId")
    is_update = data.get("isUpdate") == "1"
    is_delete = data.get("isDelete") == "1"
    doc_id = data.get("id")  


    if not parent_id:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Employee ID is required",
            status_code=400,
            http_status=400
        )

    employee_name = frappe.db.get_value(
        "Employee",
        {"custom_id": parent_id},
        "name"
    )

    if not employee_name:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"Employee with ID {parent_id} does not exist",
            status_code=404,
            http_status=404
        )
  
    if is_delete:
        if not doc_id:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message="Document ID required to delete",
                status_code=400,
                http_status=400
            )

        doc_name = frappe.db.get_value("HR Documents", {"id": doc_id}, "name")
        
        if not doc_name:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message=f"Document with ID {doc_id} not found",
                status_code=404,
                http_status=404
            )

        try:
            frappe.delete_doc("HR Documents", doc_name, force=True)
            frappe.db.commit()

            return NAPSA_CLIENT_INSTANCE.send_response(
                status="success",
                message=f"Document with ID {doc_id} deleted successfully",
                status_code=200,
                http_status=200
            )

        except Exception as e:
            frappe.log_error(
                title="Delete HR Document Error",
                message=frappe.get_traceback()
            )
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message=str(e),
                status_code=500,
                http_status=500
            )


    i = 0
    created_docs = []

    while True:
        name_key = f"name[{i}]"
        desc_key = f"description[{i}]"
        file_key = f"file[{i}]"

        name_val = data.get(name_key)
        desc_val = data.get(desc_key)
        file_obj = files.get(file_key)

        if not name_val and not desc_val and not file_obj:
            break  

        if not name_val or not desc_val or not file_obj:
            return NAPSA_CLIENT_INSTANCE.send_response(
                status="fail",
                message=f"Missing data for document index {i}",
                status_code=400,
                http_status=400
            )

       
        saved_file_url = save_file(file_obj, site_name=NAPSA_CLIENT_INSTANCE.GetDefaultSiteName(), folder_type="HUMAN_RESOURCE_PDF")

        if is_update and doc_id:
           
            doc = frappe.get_doc("HR Documents", doc_id)
            doc.parent_id = parent_id
            doc.name1 = name_val
            doc.description = desc_val
            existing_files = doc.file.split(",") if doc.file else []
            doc.file = ",".join(existing_files + [saved_file_url])
            doc.save()
            frappe.db.commit()
            created_docs.append(doc.name)
        else:
            random_id = str(random.randint(10000000, 99999999))
            doc = frappe.get_doc({
                "doctype": "HR Documents",
                "id": random_id,
                "name": random_id,
                "parent_id": parent_id,
                "name1": name_val,
                "description": desc_val,
                "file": saved_file_url,
                "is_update": 0,
                "is_delete": 0
            }).insert()
            frappe.db.commit()
            created_docs.append(doc.name)

        i += 1

    return NAPSA_CLIENT_INSTANCE.send_response(
        status="success",
        message=f"{len(created_docs)} document(s) processed",
        status_code=200,
        http_status=200
    )




@frappe.whitelist(allow_guest=False, methods=["PATCH"])
def update_employee_profile_photo():
    data = frappe.form_dict
    employeeId = data.get("employeeId")
    file = frappe.local.request.files.get("profilePhoto")
    
    if not employeeId:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Employee ID is required",
            status_code=400,
            http_status=400
        )
        
    if not file:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Profile photo file is required",
            status_code=400,
            http_status=400
        )
        
    employee_name = frappe.db.get_value(
        "Employee",
        {"custom_id": employeeId},
        "name"
    )

    print("Employee Name:", employee_name)
    if not employee_name:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Employee not found",
            status_code=404,
            http_status=404
        )

    employee = frappe.get_doc("Employee", employee_name)    
    saved_file_url = save_file(file, site_name=NAPSA_CLIENT_INSTANCE.GetDefaultSiteName(), folder_type="EMPLOYEE_PROFILE_PHOTO")

    print("Saved File URL:", saved_file_url)
    employee.image = saved_file_url
    employee.save()
    frappe.db.commit()

    return NAPSA_CLIENT_INSTANCE.send_response(
        status="success",
        message="Employee profile photo updated successfully",
        status_code=200,
        http_status=200
    )
    
    
    
@frappe.whitelist(allow_guest=False, methods=["POST"])
def validate_employee():

    nrc = (frappe.form_dict.get("NrcId") or "").strip()
    tpin = (frappe.form_dict.get("TpinId") or "").strip()
    nhima = (frappe.form_dict.get("NhimaHealthInsurance") or "").strip()
    napsa = (frappe.form_dict.get("SocialSecurityNapsa") or "").strip()
    
    
    if not all([nrc, tpin, nhima, napsa]):
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="NrcId, TpinId, NhimaHealthInsurance and SocialSecurityNapsa are all required",
            status_code=400,
            http_status=400,
            data={}
        )

        

    errors = {}

    if nrc:
        if frappe.db.exists("Employee", {"custom_national_registration_number": nrc}):
            errors["nrc"] = "NRC already exists"

    if tpin:
        if frappe.db.exists("Employee", {"custom_tax_payer_indentification_number": tpin}):
            errors["tpin"] = "TPIN already exists"


    if nhima:
        if frappe.db.exists("Employee", {"custom_nhima_health_insurance_number": nhima}):
            errors["nhima"] = "NHIMA number already exists"

    if napsa:
        if frappe.db.exists("Employee", {"custom_social_security_number": napsa}):
            errors["napsa"] = "NAPSA number already exists"

    if errors:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Validation failed",
            data=errors,
            status_code=400,
            http_status=400
        )

    return NAPSA_CLIENT_INSTANCE.send_response(
        status="success",
        message="Identifiers are valid",
        status_code=200,
        http_status=200,
        data={}
    )