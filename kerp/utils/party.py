import frappe


@frappe.whitelist()
def get_party_details(party_type, party):
    if not party_type or not party:
        return {}

    if party_type == "Customer":
        doc = frappe.get_doc("Customer", party)
        return {
            "party_name": doc.customer_name,
            "contact": doc.customer_primary_contact,
            "address": doc.customer_primary_address,
        }

    elif party_type == "CRM Lead":
        doc = frappe.get_doc("CRM Lead", party)
        return {
            "party_name": doc.organization,
            "contact_person": doc.lead_name,
            "contact_person_email": doc.email,
            "contact_person_mobile": doc.mobile_no,
        }
    elif party_type == "Supplier":
        doc = frappe.get_doc("Supplier", party)
        return {
            "party_name": doc.supplier_name,
            "contact": doc.supplier_primary_contact,
            "address": doc.supplier_primary_address,
        }

    return {}
