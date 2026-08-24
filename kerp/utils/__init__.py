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

@frappe.whitelist()
def get_transporter_list(txt: str = None, limit: int = 20):
    supplier = frappe.qb.DocType("Supplier")

    query = (
        frappe.qb.from_(supplier)
        .select(supplier.supplier_name.as_("value"))
        .where(supplier.is_transporter == 1)
        .where(supplier.disabled == 0)
        .orderby(supplier.supplier_name)
        .limit(int(limit) if limit else 20)
    )

    if txt:
        query = query.where(
            supplier.name.like(f"%{txt}%") | supplier.supplier_name.like(f"%{txt}%")
        )

    return query.run(as_dict=True)
