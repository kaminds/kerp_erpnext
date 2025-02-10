import frappe
from frappe.custom.doctype.custom_field.custom_field import (
    create_custom_fields as _create_custom_fields,
)
from kerp.constants.custom_fields import CUSTOM_FIELDS
from kerp.constants.property_setters import PROPERTY_SETTERS


def after_install():
    create_custom_fields()
    create_property_setters()


def create_custom_fields():
    _create_custom_fields(get_custom_fields(), ignore_validate=True)


def get_custom_fields():
    custom_fields = {}

    for doctypes, fields in CUSTOM_FIELDS.items():
        if isinstance(fields, dict):
            fields = [fields]

        custom_fields.setdefault(doctypes, []).extend(fields)

    return custom_fields


def create_property_setters():
    for property_setter in PROPERTY_SETTERS:
        frappe.make_property_setter(
            property_setter,
            validate_fields_for_doctype=False,
            is_system_generated=property_setter.get("is_system_generated", True),
        )
