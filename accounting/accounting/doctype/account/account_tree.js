// Copyright (c) 2021, Lin To and contributors
// For license information, please see license.txt

frappe.provide("frappe.treeview_settings");

frappe.treeview_settings["Account"] = {
  title: __("Chart of Accounts"),
  get_tree_root: false,
  get_tree_nodes: "accounting.accounting.doctype.account.utils.get_children",
  filters: [
    {
      fieldname: "company",
      fieldtype: "Link",
      options: "Company",
    },
  ],
  onrender: function (node) {
    console.log(node);
    if (node.data.balance !== undefined) {
      const suf = node.data.is_credit ? "Cr" : "Dr";
      $(
        '<span class="balance-area pull-right">' +
          `${node.data.currency} ${node.data.balance} ${suf}` +
          "</span>"
      ).insertBefore(node.$ul);
    }
  },
};
