// Copyright (c) 2021, Lin To and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Invoice', {
  setup(frm) {
    frappe.db.get_doc("Account Defaults").then(doc => {
      frm.set_value("receiving_account", doc.income_account)
      frm.set_value("stock_account", doc.stock_account)
    })

    frm.set_value("posting_date", frappe.datetime.now_date())
    // frm.set_value("cost", 0.000)
  }
});
