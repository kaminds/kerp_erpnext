import frappe
from datetime import datetime


def autoname(doc, method=None):
    item = frappe.get_doc("Item", doc.item)
    if item.brand_item_reference_kerp and not item.brand_item_reference_kerp == "None":
        today_date = datetime.today().strftime("%d%m%y")
        if item.item_pack_size_kerp and not item.item_pack_size_kerp == "None":
            pack_size_abbr = frappe.get_value(
                "Item Pack Size", item.item_pack_size_kerp, "abbreviation"
            )
            doc.name = (
                f"BOM-{item.brand_item_reference_kerp}-{pack_size_abbr}-{today_date}"
            )
        else:
            doc.name = f"BOM-{item.brand_item_reference_kerp}-{today_date}"
