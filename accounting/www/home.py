import frappe


def get_context(context):
    context.company = frappe.get_list(
        "Company", fields=["company_name", "description"]
    )[0]
