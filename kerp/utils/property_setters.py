import frappe
from kerp.constants.property_setters import PROPERTY_SETTERS


def create_property_setters():
    for property_setter in PROPERTY_SETTERS:
        frappe.make_property_setter(
            property_setter,
            validate_fields_for_doctype=False,
            is_system_generated=property_setter.get("is_system_generated", True),
        )
