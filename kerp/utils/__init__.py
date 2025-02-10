import frappe


def upsert_item_attribute(item_attr, attr_value, attr_abbr):
    if frappe.db.exists("Item Attribute", item_attr):
        attr = frappe.get_doc("Item Attribute", item_attr)
        attr.append(
            "item_attribute_values",
            {"attribute_value": attr_value, "abbr": attr_abbr},
        )
        attr.save()
    else:
        new_attr = frappe.get_doc(
            {
                "doctype": "Item Attribute",
                "attribute_name": item_attr,
                "item_attribute_values": [
                    {"attribute_value": attr_value, "abbr": attr_abbr}
                ],
            }
        )
        new_attr.insert(ignore_if_duplicate=True)


def remove_item_attr_value(item_attr, attr_abbr):
    if frappe.db.exists("Item Attribute", item_attr):
        attr = frappe.get_doc("Item Attribute", item_attr)
        for row in attr.item_attribute_values:
            if row.abbr == attr_abbr:
                attr.remove(row)
                break
        attr.save()
