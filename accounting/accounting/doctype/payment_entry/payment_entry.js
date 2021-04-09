// Copyright (c) 2021, Lin To and contributors
// For license information, please see license.txt
function setIfNotUndefined(key, value, frm) {
  if (value !== undefined) {
    frm.set_value(key, value);
  }
}

frappe.ui.form.on("Payment Entry", {
  setup(frm) {
    if (frm.doc.docstatus === 0) {
      frm.set_value("naming_series", "ACC-PAY-.YYYY.-");
      frm.set_value("posting_date", frappe.datetime.now_date());

      if (window.tempDoc !== undefined) {
        const { reference_type, reference_name, total_amount } = window.tempDoc;
        const keys = [
          "payment_type",
          "party_type",
          "party_name",
          "company",
          "account_paid_to",
          "account_paid_from",
        ];
        keys.forEach((key) => {
          setIfNotUndefined(key, window.tempDoc[key], frm);
        });

        setIfNotUndefined("paid_amount", window.tempDoc["total_amount"], frm);
        setIfNotUndefined(
          "references",
          [
            {
              reference_type,
              reference_name,
              total_amount,
            },
          ],
          frm
        );

        frappe.db.get_doc("Account Defaults").then((doc) => {
          if (frm.doc.payment_type === "Pay") {
            frm.set_value("account_paid_from", doc.bank_account);
          } else {
            frm.set_value("account_paid_to", doc.bank_account);
          }
        });
      }
    }
  },
  // refresh: function(frm) {

  // }
});
