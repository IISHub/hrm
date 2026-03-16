import frappe
from frappe import _
from frappe.utils import flt, getdate

@frappe.whitelist()
def create_custom_salary_slip(employee, posting_date, start_date, end_date):
    """
    Creates a Salary Slip for a single employee.
    Usage: /api/method/your_app.api.create_custom_salary_slip
    """
    try:
        # 1. Initialize the Salary Slip Document
        ss = frappe.new_doc("Salary Slip")
        ss.employee = employee
        ss.posting_date = posting_date
        ss.start_date = start_date
        ss.end_date = end_date

        # 2. Fetch Employee details
        emp = frappe.get_doc("Employee", employee)
        ss.company = emp.company
        ss.employee_name = emp.employee_name

        # 3. Fetch latest Salary Structure for this employee
        salary_structure_list = frappe.get_all(
            "Salary Structure",
            filters={"employee": employee, "docstatus": 1, "is_active": "Yes"},
            order_by="creation desc",
            limit_page_length=1
        )
        if salary_structure_list:
            salary_structure_doc = frappe.get_doc("Salary Structure", salary_structure_list[0].name)
            ss.salary_structure = salary_structure_doc.name
            ss.payroll_frequency = salary_structure_doc.payroll_frequency or "Monthly"
        else:
            # Default payroll frequency if no salary structure exists
            ss.payroll_frequency = "Monthly"

        # 4. Add Earnings
        earnings = [
            {"component": "Basic Pay", "amount": 4000.00},
            {"component": "Housing Allowance", "amount": 1400.00},
            {"component": "Transport Allowance", "amount": 875.00},
            {"component": "Lunch Allowance", "amount": 1000.00},
            {"component": "Leave Pay", "amount": 1846.20},
            {"component": "Medical Allowance", "amount": 500.00}
        ]
        for e in earnings:
            ss.append("earnings", {
                "salary_component": e["component"],
                "amount": flt(e["amount"])
            })

        # 5. Add Deductions
        deductions = [
            {"component": "NHIMA", "amount": 40.00},
            {"component": "NAPSA", "amount": 481.06},
            {"component": "PAYE", "amount": 1185.84}
        ]
        for d in deductions:
            ss.append("deductions", {
                "salary_component": d["component"],
                "amount": flt(d["amount"])
            })

        # 6. Calculate totals
        ss.calculate_net_pay()

        # 7. Save
        ss.insert()
        # ss.submit()  # Uncomment to auto-submit

        return {
            "status": "success",
            "message": _("Salary Slip {0} created").format(ss.name),
            "name": ss.name,
            "net_pay": ss.net_pay
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Payroll API Error")
        return {"status": "error", "message": str(e)}