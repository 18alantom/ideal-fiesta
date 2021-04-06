import frappe
import datetime


@frappe.whitelist()
def create_sales_invoice(company, customer, items):
    frappe.throw(str([company, customer, items]))
    check_and_insert_customer(customer)
    doc = create_sales_invoice_doc(company, customer, items)
    return doc


def check_and_insert_customer(customer):
    if not frappe.db.exists("Customer", customer["customer_id"]):
        doc = frappe.get_doc(
            dict(
                doctype="Customer",
                customer_id=customer["customer_id"],
                first_name=customer["first_name"],
                last_name=customer["last_name"],
            )
        )

        doc.insert()


def create_sales_invoice_doc(company, customer, items):
    defaults = frappe.get_doc("Account Defaults")
    doc = frappe.get_doc(
        dict(
            doctype="Sales Invoice",
            company=company,
            customer=customer.customer_name,
            posting_date=frappe.utils.get_date_str(datetime.date.today()),
            items=[get_item_dict(item) for item in items],
            receiving_account=defaults.income_account,
            stock_account=defaults.stock_account,
        )
    )
    return doc


def get_item_dict(item):
    return dict(
        doctype="Invoice Item",
        item=item["name"],
        quantity=item["quantity"],
        value=item["value"],
    )
