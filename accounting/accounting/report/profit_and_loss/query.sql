SELECT
  `tabGL Entry`.name AS "Name:Link/GL Entry:150",
  `tabGL Entry`.credit AS "Credit:Int:200",
  `tabGL Entry`.debit AS "Debit:Int:200",
  `tabGL Entry`.account AS "Account:Link/Account:300",
  `tabGl Entry`.voucher_number AS "Voucher Number:Data:200"
FROM
  `tabGL Entry` JOIN `tabAccount`
  ON `tabGL Entry`.account =`tabAccount`.name
WHERE
  report_type="Profit and Loss";
