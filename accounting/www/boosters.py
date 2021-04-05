import frappe


def get_context(context):
    inventory = {
        inv["name"]: inv["quantity"]
        for inv in frappe.get_list("Inventory", fields=["name", "quantity"])
    }
    context.company = frappe.get_list("Company", ["company_name", "currency"])[0]

    items = frappe.get_list(
        "Item",
        fields=[
            "name",
            "item_name",
            "description",
            "value",
            "unit_of_measure",
            "item_group",
        ],
    )

    for item in items:
        item["quantity"] = 0
        if item["name"] in inventory:
            item["quantity"] = inventory[item["name"]]
        item["unit_of_measure"] = item["unit_of_measure"].lower()

    items.sort(key=lambda i: -i["quantity"])
    context.items = items
