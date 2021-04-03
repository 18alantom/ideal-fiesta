// Copyright (c) 2016, Lin To and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["P&L"] = {
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
      default: frappe.datetime.year_start(),
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
      mandatory: true,
      default: frappe.datetime.year_end(),
    },
  ],
};
