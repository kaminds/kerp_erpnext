import frappe
import random


def autoname(doc, method=None):
    if len(doc.links) > 0:
        link = doc.links[0]
        random_int = random.randint(10, 99)
        if link.link_doctype == "Customer":
            customer = frappe.get_doc("Customer", link.link_name)
            doc.address_title = customer.customer_name
            doc.name = f"{doc.pincode}-{customer.customer_code_kerp}-{random_int}"
        elif link.link_doctype == "Supplier":
            supplier = frappe.get_doc("Supplier", link.link_name)
            doc.address_title = supplier.supplier_name
            doc.name = f"{doc.pincode}-{supplier.supplier_code_kerp}-{random_int}"
        else:
            doc.name = f"{doc.pincode}-{link.link_name}-{random_int}"
