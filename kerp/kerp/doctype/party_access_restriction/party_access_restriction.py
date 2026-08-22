# Copyright (c) 2026, Kaminds Nutrichem Private Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

ALLOWED_NAME_PATTERNS = ["%Debtor%", "%Creditor%", "%Bank%"]
ALLOWED_ACCOUNT_TYPES = ["Receivable", "Payable", "Bank", "Cash"]
BYPASS_ROLES = {"System Manager", "Accounts Manager"}

class PartyAccessRestriction(Document):
	pass


def _user_can_bypass(user):
    if user == "Administrator":
        return True
    user_roles = set(frappe.get_roles(user))
    return bool(user_roles.intersection(BYPASS_ROLES))


def get_restricted_parties(user, party_type):
    """Returns list of restricted party names of a given type (Customer/Supplier/Employee)."""
    if _user_can_bypass(user):
        return []

    return frappe.get_all(
        "Party Access Restriction Detail",
        filters={"parenttype": "Party Access Restriction", "party_type": party_type},
        pluck="party"
    )


def is_restricted(user, party_type, party):
    """Direct check for has_permission hooks."""
    if not party:
        return False
    if _user_can_bypass(user):
        return False

    return frappe.db.exists(
        "Party Access Restriction Detail",
        {"parenttype": "Party Access Restriction", "party_type": party_type, "party": party}
    ) is not None


# ---------- PERMISSION QUERY CONDITIONS ----------

def sales_invoice_permission_query(user):
    restricted = get_restricted_parties(user, "Customer")
    if restricted:
        return "`tabSales Invoice`.customer not in ({0})".format(
            ", ".join(frappe.db.escape(p) for p in restricted)
        )
    return ""


def sales_order_permission_query(user):
    restricted = get_restricted_parties(user, "Customer")
    if restricted:
        return "`tabSales Order`.customer not in ({0})".format(
            ", ".join(frappe.db.escape(p) for p in restricted)
        )
    return ""


def purchase_invoice_permission_query(user):
    restricted = get_restricted_parties(user, "Supplier")
    if restricted:
        return "`tabPurchase Invoice`.supplier not in ({0})".format(
            ", ".join(frappe.db.escape(p) for p in restricted)
        )
    return ""


def purchase_order_permission_query(user):
    restricted = get_restricted_parties(user, "Supplier")
    if restricted:
        return "`tabPurchase Order`.supplier not in ({0})".format(
            ", ".join(frappe.db.escape(p) for p in restricted)
        )
    return ""


def gl_entry_permission_query(user):
    restricted_suppliers = get_restricted_parties(user, "Supplier")
    restricted_customers = get_restricted_parties(user, "Customer")
    restricted_employees = get_restricted_parties(user, "Employee")

    conditions = []
    if restricted_suppliers:
        vals = ", ".join(frappe.db.escape(p) for p in restricted_suppliers)
        conditions.append(f"(`tabGL Entry`.party_type = 'Supplier' and `tabGL Entry`.party in ({vals}))")
    if restricted_customers:
        vals = ", ".join(frappe.db.escape(p) for p in restricted_customers)
        conditions.append(f"(`tabGL Entry`.party_type = 'Customer' and `tabGL Entry`.party in ({vals}))")
    if restricted_employees:
        vals = ", ".join(frappe.db.escape(p) for p in restricted_employees)
        conditions.append(f"(`tabGL Entry`.party_type = 'Employee' and `tabGL Entry`.party in ({vals}))")

    if conditions:
        return "not (" + " or ".join(conditions) + ")"
    return ""


def payment_entry_permission_query(user):
    restricted_suppliers = get_restricted_parties(user, "Supplier")
    restricted_customers = get_restricted_parties(user, "Customer")
    restricted_employees = get_restricted_parties(user, "Employee")

    conditions = []
    if restricted_suppliers:
        vals = ", ".join(frappe.db.escape(p) for p in restricted_suppliers)
        conditions.append(f"(`tabPayment Entry`.party_type = 'Supplier' and `tabPayment Entry`.party in ({vals}))")
    if restricted_customers:
        vals = ", ".join(frappe.db.escape(p) for p in restricted_customers)
        conditions.append(f"(`tabPayment Entry`.party_type = 'Customer' and `tabPayment Entry`.party in ({vals}))")
    if restricted_employees:
        vals = ", ".join(frappe.db.escape(p) for p in restricted_employees)
        conditions.append(f"(`tabPayment Entry`.party_type = 'Employee' and `tabPayment Entry`.party in ({vals}))")

    if conditions:
        return "not (" + " or ".join(conditions) + ")"
    return ""

def supplier_permission_query(user):
    restricted = get_restricted_parties(user, "Supplier")
    if restricted:
        return "`tabSupplier`.name not in ({0})".format(
            ", ".join(frappe.db.escape(p) for p in restricted)
        )
    return ""


def customer_permission_query(user):
    restricted = get_restricted_parties(user, "Customer")
    if restricted:
        return "`tabCustomer`.name not in ({0})".format(
            ", ".join(frappe.db.escape(p) for p in restricted)
        )
    return ""


def employee_permission_query(user):
    restricted = get_restricted_parties(user, "Employee")
    if restricted:
        return "`tabEmployee`.name not in ({0})".format(
            ", ".join(frappe.db.escape(p) for p in restricted)
        )
    return ""




# ---------- HAS_PERMISSION HOOKS ----------

def sales_invoice_has_permission(doc, ptype, user):
    return not is_restricted(user, "Customer", doc.customer)


def sales_order_has_permission(doc, ptype, user):
    return not is_restricted(user, "Customer", doc.customer)


def purchase_invoice_has_permission(doc, ptype, user):
    return not is_restricted(user, "Supplier", doc.supplier)


def purchase_order_has_permission(doc, ptype, user):
    return not is_restricted(user, "Supplier", doc.supplier)


def gl_entry_has_permission(doc, ptype, user):
    if doc.party_type and doc.party:
        return not is_restricted(user, doc.party_type, doc.party)
    return True


def payment_entry_has_permission(doc, ptype, user):
    if doc.party_type and doc.party:
        return not is_restricted(user, doc.party_type, doc.party)
    return True

def supplier_has_permission(doc, ptype, user):
    return not is_restricted(user, "Supplier", doc.name)


def customer_has_permission(doc, ptype, user):
    return not is_restricted(user, "Customer", doc.name)


def employee_has_permission(doc, ptype, user):
    return not is_restricted(user, "Employee", doc.name)

def account_gl_entry_permission_query(user):
    if _user_can_bypass(user):
        return ""

    like_conditions = " or ".join(
        "`tabAccount`.account_name like {0}".format(frappe.db.escape(p))
        for p in ALLOWED_NAME_PATTERNS
    )
    type_condition = "`tabAccount`.account_type in ({0})".format(
        ", ".join(frappe.db.escape(t) for t in ALLOWED_ACCOUNT_TYPES)
    )

    return """`tabGL Entry`.account in (
        select name from `tabAccount` where ({0}) and {1}
    )""".format(like_conditions, type_condition)


def account_gl_entry_has_permission(doc, ptype, user):
    if _user_can_bypass(user):
        return True

    if not doc.account:
        return True

    account = frappe.db.get_value(
        "Account", doc.account, ["account_name", "account_type"], as_dict=True
    )
    if not account:
        return False

    name_match = any(
        pattern.strip("%").lower() in (account.account_name or "").lower()
        for pattern in ALLOWED_NAME_PATTERNS
    )
    type_match = account.account_type in ALLOWED_ACCOUNT_TYPES

    return name_match and type_match

def account_permission_query(user):
    if _user_can_bypass(user):
        return ""

    like_conditions = " or ".join(
        "`tabAccount`.account_name like {0}".format(frappe.db.escape(p))
        for p in ALLOWED_NAME_PATTERNS
    )
    type_condition = "`tabAccount`.account_type in ({0})".format(
        ", ".join(frappe.db.escape(t) for t in ALLOWED_ACCOUNT_TYPES)
    )

    return """(({0}) and {1}) or `tabAccount`.is_group = 1""".format(like_conditions, type_condition)


def account_has_permission(doc, ptype, user):
    if _user_can_bypass(user):
        return True

    if doc.is_group:
        return True  # keep tree structure navigable

    name_match = any(
        pattern.strip("%").lower() in (doc.account_name or "").lower()
        for pattern in ALLOWED_NAME_PATTERNS
    )
    type_match = doc.account_type in ALLOWED_ACCOUNT_TYPES

    return name_match and type_match