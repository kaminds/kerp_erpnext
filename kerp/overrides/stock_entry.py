import frappe


def on_trash(doc, method=None):
    unlink_sample_movement(doc)


def unlink_sample_movement(doc):
    linked_sms = frappe.get_all(
        "Sample Movement", filters={"stock_entry": doc.name}, pluck="name"
    )

    for sm_name in linked_sms:
        frappe.db.set_value("Sample Movement", sm_name, "stock_entry", None)
