import frappe
from frappe.model.naming import make_autoname


def autoname(doc, method=None):
    doc.batch_no_kerp = doc.batch_id
    naming_series = "BATCH-.YYYY.-.####"
    doc.batch_id = make_autoname(naming_series)
    doc.name = doc.batch_id


def before_save(doc, method=None):
    if frappe.db.exists(
        "Batch", {"batch_no_kerp": doc.batch_no_kerp, "item": doc.item}
    ):
        frappe.throw(
            f"Batch Number {doc.batch_no_kerp} already exists for Item {doc.item}"
        )
