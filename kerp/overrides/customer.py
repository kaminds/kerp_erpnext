import frappe
import pycountry
from frappe.model.naming import make_autoname


def autoname(doc, method=None):
    country_code = frappe.get_cached_value("Country", doc.country_kerp, "code")
    country_code_numeric = pycountry.countries.get(alpha_2=country_code.upper()).numeric
    naming_series = f"C{country_code_numeric}.YY.###"
    doc.customer_code_kerp = make_autoname(naming_series)
    doc.name = f"{doc.customer_name}-{doc.customer_code_kerp}"
