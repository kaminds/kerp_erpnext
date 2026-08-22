import frappe
from frappe import bold, _

class PurchaseOrderMixin:
    def validate_company_linked_addresses(self):
        purchase_doctypes = ("Purchase Order", "Purchase Receipt", "Purchase Invoice", "Supplier Quotation")
        if self.doctype in purchase_doctypes:
            address = self.get("billing_address")

            if address and not frappe.db.exists(
                "Dynamic Link",
                {
                    "parent": address,
                    "parenttype": "Address",
                    "link_doctype": "Company",
                    "link_name": self.company,
                },
            ):
                frappe.throw(
                    _("Billing Address does not belong to the Company {0}.").format(bold(self.company))
                )
            return

        return super().validate_company_linked_addresses()
