import frappe
import pycountry
from frappe.model.naming import make_autoname


def autoname(doc, method=None):
    country_code = frappe.get_cached_value("Country", doc.country, "code")
    country_code_numeric = pycountry.countries.get(alpha_2=country_code.upper()).numeric
    naming_series = f"S{country_code_numeric}.YY.###"
    doc.supplier_code_kerp = make_autoname(naming_series)
    doc.name = f"{doc.supplier_name}-{doc.supplier_code_kerp}"
