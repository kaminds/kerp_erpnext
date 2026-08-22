import frappe

# Central config: map each reference doctype to its internal recipients
INTERNAL_RECIPIENTS_CONFIG = {
    "Sales Invoice": {
        "cc": ["inder.karamchandani@kaminds.com, prateek@kaminds.com"],
        "bcc": [],
        "dynamic": "get_sales_team_emails",
    },
    "Sales Order": {
        "cc": ["inder.karamchandani@kaminds.com, prateek@kaminds.com"],
        "bcc": [],
        "dynamic": "get_sales_team_emails",
    },
    "Purchase Order": {
        "cc": ["inder.karamchandani@kaminds.com, prateek@kaminds.com"],
        "bcc": [],
        "dynamic": None,
    },
    "Quotation": {
        "cc": ["inder.karamchandani@kaminds.com, prateek@kaminds.com"],
        "bcc": [],
        "dynamic": None,
    },
}

def get_creator_email(reference_doctype, reference_name):
    """Return the email of the user who created the reference document."""
    owner = frappe.db.get_value(reference_doctype, reference_name, "owner")
    if not owner:
        return None

    # `owner` is usually the email itself (default username = email in Frappe),
    # but fall back to the User doctype's email field to be safe.
    if "@" in owner:
        return owner
    return frappe.db.get_value("User", owner, "email")

def add_internal_recipients(doc, method):
    """Communication.before_insert hook.
    Adds internal CC/BCC recipients based on the linked document type.
    """
    if doc.communication_type != "Communication":
        return
    if not doc.reference_doctype or not doc.reference_name:
        return

    config = INTERNAL_RECIPIENTS_CONFIG.get(doc.reference_doctype)
    if not config:
        return  # no rule for this doctype, do nothing

    cc_list = list(config.get("cc") or [])
    bcc_list = list(config.get("bcc") or [])

    # Optional: pull in dynamic recipients (e.g. sales team, owner, etc.)
    dynamic_fn_name = config.get("dynamic")
    if dynamic_fn_name:
        dynamic_fn = globals().get(dynamic_fn_name)
        if dynamic_fn:
            cc_list += dynamic_fn(doc) or []

    creator_email = get_creator_email(doc.reference_doctype, doc.reference_name)
    if creator_email:
        cc_list.append(creator_email)

    doc.cc = _merge_emails(doc.cc, cc_list)
    doc.bcc = _merge_emails(doc.bcc, bcc_list)


def _merge_emails(existing, new_emails):
    """Merge new emails into an existing comma-separated email string, deduped."""
    existing_list = [e.strip() for e in existing.split(",")] if existing else []
    merged = {e for e in existing_list + new_emails if e}
    return ", ".join(sorted(merged))


def get_sales_team_emails(doc):
    """Example dynamic recipient resolver for Sales Invoice."""
    sales_invoice = frappe.get_cached_doc("Sales Invoice", doc.reference_name)
    emails = []
    for row in sales_invoice.get("sales_team") or []:
        if not row.sales_person:
            continue

        employee = frappe.db.get_value("Sales Person", row.sales_person, "employee")
        if not employee:
            continue

        employee_details = frappe.db.get_value(
            "Employee", employee, ["user_id", "reports_to"], as_dict=True
        )
        if not employee_details:
            continue

        if employee_details.user_id:
            emails.append(employee_details.user_id)

        if employee_details.reports_to:
            manager_email = frappe.db.get_value(
                "Employee", employee_details.reports_to, "user_id"
            )
            if manager_email:
                emails.append(manager_email)

    return emails