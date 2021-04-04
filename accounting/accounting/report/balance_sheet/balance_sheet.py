# Copyright (c) 2013, Lin To and contributors
# For license information, please see license.txt
# PLEASE NOTE : THIS CODE IS TERRIBLE, I GENERALLY DO BETTER THAN THIS

from __future__ import unicode_literals

import frappe
from frappe import _


def execute(filters=None, filter_by_date=True):
    records = get_sql_records(filters, filter_by_date)
    if len(records) == 0:
        frappe.throw(_("No values available for set filters"))
    accounts = get_sql_records_accounts(filters)
    tree = build_sheet_tree(records, accounts)
    columns = get_columns()
    data = get_data(tree)
    return columns, data


def get_data(tree):
    tk = [(k, i[3]) for k, i in tree.items() if i[1] is None]
    tk.sort(key=lambda i: i[1])
    data = []
    totals = {0: 0, 1: 0}
    default = int(tk[0][1])
    has_switched = False

    for i, (an, i_c) in enumerate(tk):
        assert isinstance(i_c, int), "Apply cast."
        totals[i_c] += tree[an][0]

        if i_c != default and not has_switched:
            append_total_row(default, totals, data)
            has_switched == True
            data.append(get_data_row("", "", 0, 0))

        add_data_row(an, tree, data, 0)

        if i == len(tk) - 1:
            append_total_row(i_c, totals, data)

    return data


def append_total_row(i_c, totals, data):
    label = frappe.bold(f'Total ({"Credit" if i_c else "Debit"})')
    amount = frappe.format(totals[i_c], "Currency")
    row = get_data_row(label, amount, 0, 0)
    data.append(row)


def add_data_row(an, tree, data, i):
    balance, _, children, _ = tree[an]
    is_group = 0 if not children else 1
    account = an
    if i == 0:
        account = frappe.bold(account)

    amount = frappe.format(balance, "Currency")
    data.append(get_data_row(account, amount, i, is_group))
    if is_group:
        for child in children:
            add_data_row(child, tree, data, i + 1)


def get_data_row(account, amount, indent, is_group):
    return frappe._dict(
        {"account": account, "amount": amount, "indent": indent, "is_group": is_group}
    )


def get_columns():
    return ["Account:Data:300", "Amount:Currency:200"]


def build_sheet_tree(records, accounts):
    statement = get_balance_statement(records)
    accounts = {n: (n, an, pn, i_g, i_c, c) for n, an, pn, i_g, i_c, c in accounts}
    accs = {}

    for an in statement:
        balance, pn, _ = statement[an]
        if an not in accs:
            pan = None if pn is None else accounts[pn][1]
            accs[an] = [balance, pan, None, None]

        manage_parents(an, pn, accs, accounts, balance)
    return accs


def manage_parents(an, pn, accs, accounts, balance):
    insert_parents(pn, accs, accounts)
    update_parents(an, pn, accs, accounts, balance)


def insert_parents(pn, accs, accounts):
    pan = accounts[pn][1]
    if pan in accs:
        return

    ppn = accounts[pn][2]
    i_c = accounts[pn][4]
    if ppn is None:
        accs[pan] = [0, None, [], i_c]
    else:
        ppan = accounts[ppn][1]
        accs[pan] = [0, ppan, [], None]
        insert_parents(ppn, accs, accounts)


def update_parents(an, pn, accs, accounts, balance):
    pan = accounts[pn][1]
    accs[pan][0] += balance
    accs[pan][2].append(an)
    ppn = accounts[pn][2]

    if ppn is not None:
        update_parents(pan, ppn, accs, accounts, balance)


def get_balance_statement(records):
    statement = {}
    for _, cr, dr, is_credit, account_name, parent_account in records:
        if account_name not in statement:
            statement[account_name] = [0, parent_account, None]

        if is_credit:
            statement[account_name][0] += cr
            statement[account_name][0] -= dr
        else:
            statement[account_name][0] -= cr
            statement[account_name][0] += dr
    return statement


def get_sql_records_accounts(filters):
    query = f"""
    SELECT
        name,
        account_name,
        parent_account,
        is_group,
        is_credit,
        currency
    FROM
        tabAccount
    WHERE
        company="{filters['company']}"
    ORDER BY
        is_group DESC
    """
    return frappe.db.sql(query)


def get_sql_records(filters, filter_by_date=True):
    query = f"""
    SELECT
        `tabGL Entry`.account,
        `tabGL Entry`.credit,
        `tabGL Entry`.debit,
        `tabAccount`.is_credit,
        `tabAccount`.account_name,
        `tabAccount`.parent_account
    FROM
        `tabGL Entry` JOIN `tabAccount`
        ON `tabGL Entry`.account =`tabAccount`.name
    WHERE
        `tabAccount`.company="{filters['company']}"
        AND
        `tabAccount`.report_type="Balance Sheet"
    """
    if filter_by_date:
        query += f"""
            AND
            `tabGL Entry`.posting_date BETWEEN
                "{filters['from_date']}"
                AND
                "{filters['to_date']}"
        """
    return frappe.db.sql(query)


# PLEASE NOTE : THIS CODE IS TERRIBLE, I GENERALLY DO BETTER THAN THIS
