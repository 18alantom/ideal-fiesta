# Copyright (c) 2013, Lin To and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe


def execute(filters=None):
    company_name = "Lin's Landmines"
    query_filters = dict(company_name=company_name)

    fields = [
        "posting_date",
        "account",
        "debit",
        "credit",
        "voucher_type",
        "voucher_number",
        "against_account",
    ]

    currency = frappe.db.get_value("Company", company_name, "currency")
    records = frappe.db.get_all(
        "GL Entry", filters=query_filters, fields=fields, order_by="posting_date asc"
    )
    #  frappe.throw(str(records))

    columns = [
        "Posting Date",
        "Account",
        f"Debit ({currency})",
        f"Credit ({currency})",
        f"Balance ({currency})",
        "Voucher Type",
        "Voucher No",
        "Against Account",
    ]
    data = [[r[f] for f in fields] for r in records]
    for row in data:
        row.insert(4, row[2] - row[3])
    return columns, data
