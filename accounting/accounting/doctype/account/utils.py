# -*- coding: utf-8 -*-
# Copyright (c) 2021, Lin To and contributors
# For license information, please see license.txt

import frappe


@frappe.whitelist()
def get_children(doctype, parent, company, is_root=False):
    accounts = frappe.get_list(
        doctype,
        fields=_get_fields(is_root),
        filters=_get_filters(parent, company, is_root),
    )

    _add_balance(accounts)
    return accounts


def _add_balance(accounts):

    pass


def _get_fields(is_root):
    return [
        "name as value",
        "is_group as expandable",
        "account_type",
        "report_type",
        "currency",
        "is_credit",
    ] + (["parent_account as parent"] if not is_root else [])


def _get_filters(parent, company, is_root):
    filters = []
    filters += [["company", "=", company]]
    filters += [['ifnull(`parent_account`,"")', "=", "" if is_root else parent]]
    return filters
