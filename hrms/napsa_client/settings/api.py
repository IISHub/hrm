import random
from hrms.napsa_client.main import NapsaClient
import frappe

NAPSA_CLIENT_INSTANCE = NapsaClient()


@frappe.whitelist()
def create_company_human_resource_settings():
    data = frappe.form_dict
    company_id = data.get("companyId")
    
    if not company_id:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Company id is required",
            status_code=400,
            http_status=400
        )
        
    company_list = frappe.get_list(
            "Company",
            filters={"custom_company_id": company_id},
            fields=["name"]
        )
    if not company_list:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message="Company not found",
            status_code=404,
            http_status=404
        )
    general_settings = data.get("generalSettings", {})
    statutory_contributions = data.get("statutoryContributions", {})
    salary_structures = data.get("salaryStructures", [])
    leave_policies = data.get("leavePolicyDefinitions", [])
    work_schedules = data.get("workScheduleDefinitions", [])
    job_levels = data.get("jobLevels", [])
    salary_components = data.get("salaryComponentDefinitions", [])
    departments = data.get("orgDepartments", [])
    job_roles = data.get("jobRoleDefinitions", [])
    
    
    payroll_frequency = general_settings.get("payrollFrequency")
    payroll_cutoff_day = general_settings.get("payrollCutoffDayOfMonth")
    daily_hours = general_settings.get("standardDailyWorkingHours")
    probation_months = general_settings.get("probationDurationMonths")
    notice_days = general_settings.get("standardNoticePeriodDays")
    currency = general_settings.get("currency")
    
    existing_settings = frappe.get_all(
        "General Settings",
        filters={"company": company_id},
        limit=1
    )

    if existing_settings:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"Company {company_id} already has general settings. Please consider updating the settings instead.",
            status_code=400,
            http_status=400
        )
        
    statutoryContributions_doc = frappe.get_all(
        "Statutory Contributions",
        filters={"company": company_id},
        limit=1
    )

    if statutoryContributions_doc:
        return NAPSA_CLIENT_INSTANCE.send_response(
            status="fail",
            message=f"Company {company_id} already has statutory contributions. Please consider updating instead.",
            status_code=400,
            http_status=400
        )
        


    gen_settings = frappe.get_doc({
        "doctype": "General Settings",
        "company": company_id,
        "payroll_frequency": payroll_frequency,
        "payroll_cut_off_day_of_month": payroll_cutoff_day,
        "standard_daily_working_hours": daily_hours,
        "probation_duration_months": probation_months,
        "standard_notice_period_days": notice_days,
        "currency": currency
    })

    gen_settings.save() 
   
    
    napsa = statutory_contributions.get("napsa", {})
    napsa_enabled = napsa.get("enabled")
    napsa_employee_rate = napsa.get("employeeContributionRate")
    napsa_employer_rate = napsa.get("employerContributionRate")
    napsa_base_code = napsa.get("contributionBaseComponentCode")

    nhima = statutory_contributions.get("nhima", {})
    nhima_enabled = nhima.get("enabled")
    nhima_employee_rate = nhima.get("employeeContributionRate")
    nhima_employer_rate = nhima.get("employerContributionRate")

    paye = statutory_contributions.get("paye", {})
    paye_enabled = paye.get("enabled")
    tax_method = paye.get("taxComputationMethod")
    tax_table = paye.get("taxTableCode")
    
    
    
    statutoryContributions_doc = frappe.get_doc({
        "doctype": "Statutory Contributions",
        "company": company_id,
        "napsa_enabled": napsa_enabled,
        "napsa_employee_contribution_rate": napsa_employee_rate,
        "napsa_employer_contribution_rate": napsa_employer_rate,
        "napsa_contribution_base_component_code": napsa_base_code,
        "nhima_enabled": nhima_enabled,
        "nhima_employee_contribution_rate": nhima_employee_rate,
        "nhima_employer_contribution_rate": nhima_employer_rate,
        "paye_enabled": paye_enabled,
        "paye_tax_computation_method": tax_method,
        "paye_tax_table_code": tax_table
        
    })
    
    statutoryContributions_doc.save()
   
    
    
    salary_structures_id = random.randint(100000, 999999)
    for structure in salary_structures:
        structure_code = structure.get("structureCode")
        structure_name = structure.get("structureName")
        job_level_code = structure.get("jobLevelCode")
        version = structure.get("version")
        default_salary = structure.get("defaultGrossMonthlySalary")
        status = structure.get("status")
 
        SalaryStructuresDoc = frappe.get_doc({
            "doctype": "Salary Structures",
            "default_gross_monthly_salary": default_salary,
            "structure_name": structure_name,
            "structure_code": structure_code,
            "job_level_code": job_level_code,
            "version": version,
            "status": status,
            "company": company_id,
            "id": salary_structures_id
            
        })
        
        SalaryStructuresDoc.save()
       
                

        component_id = random.randint(100000, 999999)
        components = structure.get("salaryComponents", [])
        for comp in components:
            component_code = comp.get("componentCode")
            calc_rule = comp.get("calculationRule", {})
            calc_type = calc_rule.get("type")
            calc_value = calc_rule.get("calculationValue")
            statutory_code = calc_rule.get("statutoryCode")
            used_as_base = comp.get("usedAsStatutoryBase", False)
            
            salaryComponetDoc = frappe.get_doc({
                "doctype": "Salary Components",
                "calculation_rule_calculation_value": calc_value,
                "component_code": component_code,
                "calculation_rule_type": calc_type,
                "used_as_statutory_base": used_as_base,
                "statutory_code": statutory_code,
                "id": component_id,
                "salary_structures": salary_structures_id,
            })
            
            salaryComponetDoc.save()
           
    
    
    leave_policy_id = random.randint(100000, 999999)
    for policy in leave_policies:
        policy_code = policy.get("policyCode")
        policy_name = policy.get("policyName")
        version = policy.get("version")
        effective_from = policy.get("effectiveFrom")
        status = policy.get("status")
        
        leavePolicyDefinitionsDoc = frappe.get_doc({
            "doctype": "Leave Policy Definitions",
            "effective_from": effective_from,
            "policy_code": policy_code,
            "policy_name": policy_name,
            "version": version,
            "status": status,
            "id": leave_policy_id,
            "company": company_id
        })
        
        leavePolicyDefinitionsDoc.insert()
       

        rule_id = random.randint(100000, 999999)
        rules = policy.get("leaveRules", [])
        for rule in rules:
            leave_type = rule.get("leaveTypeCode")
            annual_entitlement = rule.get("annualEntitlement")
            accrual_frequency = rule.get("accrualFrequency")
            carry_forward = rule.get("allowCarryForward")
            max_carry_days = rule.get("maxCarryForwardDays")
            allow_during_probation = rule.get("allowDuringProbation")
            prorate_on_join = rule.get("prorateOnJoin")
            allow_negative = rule.get("allowNegativeBalance")
            
            leaveRuleDoc = frappe.get_doc({
                "doctype": "Leave Rules",
                "leave_type_code": leave_type,
                "annual_entitlement": annual_entitlement,
                "accrual_frequency": accrual_frequency,
                "allow_carry_forward": carry_forward,
                "max_carry_forward_days": max_carry_days,
                "allow_during_probation": allow_during_probation,
                "prorate_on_join": prorate_on_join,
                "allow_negative_balance": allow_negative,
                "leave_policy_definitions": leave_policy_id,
                "id": rule_id
            })
            
            leaveRuleDoc.save()
           
    
    schedule_id = random.randint(100000, 999999)
    for schedule in work_schedules:
        schedule_code = schedule.get("scheduleCode")
        schedule_name = schedule.get("scheduleName")
        schedule_type = schedule.get("scheduleType")
        status = schedule.get("status")
        hours_per_week = schedule.get("hoursPerWeek")
        weekly_pattern = schedule.get("weeklyWorkPattern", {})
        monday = weekly_pattern.get("mon")
        tuesday = weekly_pattern.get("tue")
        wednesday = weekly_pattern.get("wed")
        thursday = weekly_pattern.get("thu")
        friday = weekly_pattern.get("fri")
        saturday = weekly_pattern.get("sat")
        sunday = weekly_pattern.get("sun")

        
        scheduleDoc = frappe.get_doc({
            "doctype": "Work Schedule Definitions",
            "schedule_code": schedule_code,
            "schedule_name": schedule_name,
            "schedule_type": schedule_type,
            "status": status,
            "hours_per_week": hours_per_week,
            "weekly_work_pattern_mon": monday,
            "weekly_work_pattern_tue": tuesday,
            "weekly_work_pattern_wed": wednesday,
            "weekly_work_pattern_thu": thursday,
            "weekly_work_pattern_fri": friday,
            "weekly_work_pattern_sat": saturday,
            "weekly_work_pattern_sun": sunday,
            "company": company_id,
            "id":schedule_id,
            
        })
        
        scheduleDoc.save()
       
        
    
    for dept in departments:
        dept_id = random.randint(100000, 999999)
        dept_code = dept.get("departmentCode")
        dept_name = dept.get("departmentName")
        
        departmentsDoc = frappe.get_doc({
            "doctype": "Organisation Departments",
            "id": dept_id,
            "company": company_id,
            "department_code": dept_code,
            "department_name": dept_name
        })
        
        departmentsDoc.insert()
       

    
    for role in job_roles:
        role_id = random.randint(100000, 999999)
        depart_code = role.get("departcode")
        role_code = role.get("jobRoleCode")
        role_name = role.get("jobRoleName")
        
        roleDoc = frappe.get_doc({
            "doctype": "Job Role Definitions",
            "id": role_id,
            "department": depart_code,
            "job_role_code": role_code,
            "job_role_name": role_name
        })

        roleDoc.insert()

    return NAPSA_CLIENT_INSTANCE.send_response(
        status="success",
        message="Human resource settings created successfully",
        status_code=201,
        http_status=201
    )


@frappe.whitelist()
def get_company_human_resource_settings():
    request_data = frappe.form_dict
    data = {
        "companyId": "COMP00003",
        "generalSettings": {
            "payrollFrequency": "MONTHLY",
            "payrollCutoffDayOfMonth": 25,
            "standardDailyWorkingHours": 8,
            "probationDurationMonths": 3,
            "standardNoticePeriodDays": 30,
            "currency": "ZMW"
        },
        "statutoryContributions": {
            "napsa": {"enabled": True, "employeeContributionRate": 5, "employerContributionRate": 5, "contributionBaseComponentCode": "BASIC"},
            "nhima": {"enabled": True, "employeeContributionRate": 1, "employerContributionRate": 1},
            "paye": {"enabled": True, "taxComputationMethod": "TAX_SLAB", "taxTableCode": "ZM_PAYE_2025"}
        },
        "salaryStructures": [
            {
                "+++++++": "EXEC",
                "structureName": "Executive Level",
                "jobLevelCode": "L3",
                "version": "2025",
                "defaultGrossMonthlySalary": 240000,
                "status": "ACTIVE",
                "salaryComponents": [
                    {"componentCode": "BASIC", "calculationRule": {"type": "PERCENTAGE", "calculationValue": 60}, "usedAsStatutoryBase": True},
                    {"componentCode": "HRA", "calculationRule": {"type": "PERCENTAGE", "calculationValue": 20}},
                    {"componentCode": "LTA", "calculationRule": {"type": "PERCENTAGE", "calculationValue": 10}},
                    {"componentCode": "REWARD", "calculationRule": {"type": "FIXED", "calculationValue": 0}},
                    {"componentCode": "NHIMA", "calculationRule": {"type": "STATUTORY", "statutoryCode": "NHIMA"}},
                    {"componentCode": "NAPSA", "calculationRule": {"type": "STATUTORY", "statutoryCode": "NAPSA"}},
                    {"componentCode": "PAYE", "calculationRule": {"type": "STATUTORY", "statutoryCode": "PAYE"}}
                ]
            }
        ],
        "leavePolicyDefinitions": [
            {
                "policyCode": "STANDARD",
                "policyName": "Standard Leave Policy",
                "version": "2025",
                "effectiveFrom": "2025-01-01",
                "status": "ACTIVE",
                "leaveRules": [
                    {"leaveTypeCode": "AL", "annualEntitlement": 24, "accrualFrequency": "MONTHLY", "allowCarryForward": True, "maxCarryForwardDays": 12, "allowDuringProbation": False, "prorateOnJoin": True, "allowNegativeBalance": False},
                    {"leaveTypeCode": "SL", "annualEntitlement": 14, "accrualFrequency": "YEARLY", "allowCarryForward": False, "allowDuringProbation": True, "prorateOnJoin": False, "allowNegativeBalance": False}
                ]
            }
        ],
        "workScheduleDefinitions": [
            {
                "scheduleCode": "STD",
                "scheduleName": "Standard Work Week",
                "scheduleType": "FIXED",
                "status": "ACTIVE",
                "hoursPerWeek": 40,
                "weeklyWorkPattern": {"mon": "OFFICE", "tue": "OFFICE", "wed": "OFFICE", "thu": "OFFICE", "fri": "OFFICE", "sat": "OFF", "sun": "OFF"}
            }
        ],
        "jobLevels": [
            {"levelCode": "L1", "levelName": "Junior", "hierarchyRank": 1},
            {"levelCode": "L2", "levelName": "Mid", "hierarchyRank": 2},
            {"levelCode": "L3", "levelName": "Senior", "hierarchyRank": 3}
        ],
        "salaryComponentDefinitions": [
            {"componentCode": "BASIC", "componentName": "Basic Salary", "componentType": "EARNING", "isTaxable": True},
            {"componentCode": "HRA", "componentName": "House Allowance", "componentType": "EARNING", "isTaxable": True},
            {"componentCode": "LTA", "componentName": "Leave Travel Allowance", "componentType": "EARNING", "isTaxable": True},
            {"componentCode": "REWARD", "componentName": "Reward", "componentType": "EARNING", "isTaxable": True},
            {"componentCode": "NHIMA", "componentName": "NHIMA", "componentType": "DEDUCTION", "isTaxable": False},
            {"componentCode": "NAPSA", "componentName": "NAPSA", "componentType": "DEDUCTION", "isTaxable": False},
            {"componentCode": "PAYE", "componentName": "PAYE", "componentType": "DEDUCTION", "isTaxable": False}
        ],
        "orgDepartments": [
            {"departmentCode": "ENG", "departmentName": "Engineering"},
            {"departmentCode": "HR", "departmentName": "Human Resources"}
        ],
        "jobRoleDefinitions": [
            {"departcode": "eng", "jobRoleCode": "SDE", "jobRoleName": "Software Developer"},
            {"departcode": "HR", "jobRoleCode": "HRM", "jobRoleName": "HR Manager"}
        ]
    }

    return NAPSA_CLIENT_INSTANCE.send_response(
        status="success",
        message="Human resource settings retrieved successfully",
        data=data,
        status_code=200,
        http_status=200
    )


@frappe.whitelist()
def update_company_human_resource_settings():
    data = frappe.form_dict

    return NAPSA_CLIENT_INSTANCE.send_response(
        status="success",
        message="Human resource settings updated successfully",
        status_code=200,
        http_status=200
    )


@frappe.whitelist()
def delete_company_human_resource_settings():
    data = frappe.form_dict

    return NAPSA_CLIENT_INSTANCE.send_response(
        status="success",
        message="Human resource settings deleted successfully",
        data={},
        status_code=200,
        http_status=200
    )
