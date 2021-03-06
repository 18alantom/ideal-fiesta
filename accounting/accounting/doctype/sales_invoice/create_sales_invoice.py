import frappe
import datetime
import json


@frappe.whitelist()
def create_sales_invoice(company, customer, items):
    customer = parse(customer)
    items = parse(items)
    check_and_insert_customer(customer)
    doc = create_and_submit_sales_invoice_doc(company, customer, items)
    return [f"Invoice created: {doc.name}", doc.route]


def parse(argument):
    if argument:
        return json.loads(argument)


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


def create_and_submit_sales_invoice_doc(company, customer, items):
    defaults = frappe.get_doc("Default Accounts")
    doc = frappe.get_doc(
        dict(
            doctype="Sales Invoice",
            company=company,
            customer=customer["customer_id"],
            posting_date=frappe.utils.get_date_str(datetime.date.today()),
            items=[get_item_dict(item) for item in items],
            receiving_account=defaults.income_account,
            stock_account=defaults.stock_account,
        )
    )

    doc.insert()
    doc.save()
    doc.submit()
    return doc


def get_item_dict(item):
    return dict(
        doctype="Invoice Item",
        item=item["name"],
        quantity=float(item["quantity"]),
    )
