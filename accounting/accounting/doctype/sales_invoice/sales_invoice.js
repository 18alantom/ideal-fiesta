// Copyright (c) 2021, Lin To and contributors
// For license information, please see license.txt

frappe.provide("defaults.itemDict");

frappe.ui.form.on("Sales Invoice", {
  setup(frm) {
    frappe.db.get_doc("Account Defaults").then((doc) => {
      frm.set_value("receiving_account", doc.receivable_account);
      frm.set_value("stock_account", doc.stock_account);
    });

    frm.set_value("posting_date", frappe.datetime.now_date());
    frappe.db
      .get_list("Item", { fields: ["name", "value"] })
      .then((itemList) => {
        itemList.forEach(({ name, value }) => {
          window.defaults.itemDict[name] = value;
        });
      });

    frm.set_value("posting_date", frappe.datetime.now_date());
    frm.set_value("cost", 0.0);
  },
});

frappe.ui.form.on("Invoice Item", {
  item(frm, cdt, cdn) {
    updateItems(frm, cdt, cdn, true);
    updateTotalCost(frm);
  },
  quantity(frm, cdt, cdn) {
    updateItems(frm, cdt, cdn, false);
    updateTotalCost(frm);
  },
  value(frm, cdt, cdn) {
    updateItems(frm, cdt, cdn, false);
    updateTotalCost(frm);
  },
});

function updateTotalCost(frm) {
  const cost = frappe
    .get_list("Invoice Item")
    .map(({ cost }) => cost)
    .reduce((a, b) => a + b);
  frm.set_value("cost", cost);
}

function updateItems(frm, cdt, cdn, zero) {
  let q, v;

  const row = frappe.get_doc(cdt, cdn);
  if (zero) {
    q = v = 0;
    if (row.item in window.defaults.itemDict) {
      v = window.defaults.itemDict[row.item];
    }
  } else {
    q = row.quantity;
    v = row.value;
  }

  const item_list = frappe
    .get_list("Invoice Item")
    .map(({ item, name, quantity, value, cost }) => {
      const item_dict = { item, quantity, value, cost };
      if (name === cdn) {
        item_dict.quantity = q;
        item_dict.value = v;
        item_dict.cost = q * v;
      }
      return item_dict;
    });

  frm.set_value("items", item_list);
}
