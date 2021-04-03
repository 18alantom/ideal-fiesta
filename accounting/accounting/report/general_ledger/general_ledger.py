# Copyright (c) 2013, Lin To and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.utils import getdate

blank_line = ["", "", "", "", "", "", "", ""]
fields = [
    "posting_date",
    "account",
    "debit",
    "credit",
    "voucher_type",
    "voucher_number",
    "against_account",
]


def execute(filters=None):
    validate_filters(filters)
    records = get_db_records(filters)
    if len(records) == 0:
        frappe.throw(_("No values available for set filters"))
    columns = get_report_columns(filters)
    data = get_report_data(records)
    return columns, data


def validate_filters(filters):
    validate_dates(filters["from_date"], filters["from_date"])


def validate_dates(from_date, to_date):
    from_date = getdate(from_date)
    to_date = getdate(to_date)
    if from_date > to_date:
        frappe.throw(_("From Date can't be after To Date"))


def get_db_records(filters):
    query = f"""
        select {','.join(fields)}
        from `tabGL Entry`
        where
            posting_date between "{filters["from_date"]}" and "{filters["to_date"]}"
            and
            company_name="{filters["company"]}"
    """
    return frappe.db.sql(query)


def get_report_columns(filters):
    currency = frappe.db.get_value("Company", filters["company"], "currency")
    return [
        "Posting Date:Date:100",
        "Account:Link/Account:150",
        f"Debit ({currency}):Data:150",
        f"Credit ({currency}):Data:150",
        f"Balance ({currency}):Data:150",
        "Voucher Type:Data:150",
        "Voucher No:Data:150",
        "Against Account:Link/Account:150",
    ]


def get_report_data(records):
    # Initialize variables
    data = []
    debit_total = credit_total = balance = debit = credit = 0
    voucher_number = records[0][-2]

    for pd, a, d, c, vt, vn, aa in records:
        if vn != voucher_number:
            append_last_line(data, debit, credit)
            voucher_number = vn
            credit_total += credit
            debit_total += debit
            debit = credit = 0

        credit += c
        debit += d
        balance += d - c

        data.append([pd, a, f(d), f(c), f(balance), vt, vn, aa])

    credit_total += credit
    debit_total += debit
    append_last_line(data, debit, credit)

    # Footer Total
    data.append(
        [
            "",
            "Total",
            f(debit_total),
            f(credit_total),
            f(debit_total - credit_total),
            "",
            "",
            "",
        ]
    )
    return data


def f(v):
    return frappe.format_value(v, "Currency")


def append_last_line(data, debit, credit):
    data.append(["", "Total", f(debit), f(credit), f(debit - credit), "", "", ""])
    data.append(blank_line)
