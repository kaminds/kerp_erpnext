from kerp.utils.custom_fields import create_custom_fields
from kerp.utils.property_setters import create_property_setters


def after_install():
    create_custom_fields()
    create_property_setters()
