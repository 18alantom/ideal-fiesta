// Copyright (c) 2021, Lin To and contributors
// For license information, please see license.txt

frappe.ui.form.on('Journal Entry', {
  setup(frm) {
    frm.set_value("posting_date", frappe.datetime.now_date())
  }
});
