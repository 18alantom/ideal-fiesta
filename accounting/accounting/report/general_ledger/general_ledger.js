// Copyright (c) 2016, Lin To and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["General Ledger"] = {
  filters: [
    {
      fieldname: "company",
      label: __("Company"),
      fieldtype: "Link",
      options: "Company",
      mandatory: true,
    },
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      mandatory: true,
      default: frappe.datetime.month_start(),
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
      mandatory: true,
      default: frappe.datetime.now_date(),
    },
  ],
};

frappe.db.get_list("Company").then((c) => {
  if (c.length > 0) {
    frappe.query_reports["General Ledger"].filters[0]["default"] = c[0]["name"];
  }
});
