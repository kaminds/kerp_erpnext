import frappe
from frappe.custom.doctype.custom_field.custom_field import (
    create_custom_fields as _create_custom_fields,
)
from kerp.constants.custom_fields import CUSTOM_FIELDS


def create_custom_fields():
    _create_custom_fields(get_custom_fields(), ignore_validate=True)


def get_custom_fields():
    custom_fields = {}

    for doctypes, fields in CUSTOM_FIELDS.items():
        if isinstance(fields, dict):
            fields = [fields]

        custom_fields.setdefault(doctypes, []).extend(fields)

    return custom_fields


def delete_old_fields(fieldnames, doctypes):
    if isinstance(fieldnames, str):
        fieldnames = (fieldnames,)

    if isinstance(doctypes, str):
        doctypes = (doctypes,)

    frappe.db.delete(
        "Custom Field",
        {
            "fieldname": ("in", fieldnames),
            "dt": ("in", doctypes),
        },
    )
