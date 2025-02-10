import frappe
from kerp.utils import upsert_item_attribute, remove_item_attr_value


def before_insert(doc, method=None):
    country_code = frappe.get_cached_value("Country", doc.country, "code")
    doc.short_name = f"{doc.short_name} - {doc.country}"
    doc.abbreviation_kerp = f"{doc.abbreviation_kerp}{country_code}".upper()

    upsert_item_attribute(doc.doctype, doc.short_name, doc.abbreviation_kerp)


def on_trash(doc, method=None):
    remove_item_attr_value(doc.doctype, doc.abbreviation_kerp)
