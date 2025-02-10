from kerp.utils import upsert_item_attribute, remove_item_attr_value


def before_insert(doc, method=None):
    upsert_item_attribute(doc.doctype, doc.brand, doc.abbreviation_kerp)


def on_trash(doc, method=None):
    remove_item_attr_value(doc.doctype, doc.abbreviation_kerp)
