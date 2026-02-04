import frappe
import textwrap


@frappe.whitelist()
def get_address_display(address):
    if not address:
        return ""
    doc = frappe.get_doc("Address", address)
    address_template = textwrap.dedent("""
		{{- address_line1 -}}<br>
		{%- if address_line2 %}
		{{- address_line2 -}}<br>
		{%- endif %}
		{%- if city or pincode or state or country %}
		{{- city -}}{%- if pincode %} - {{ pincode }}{%- endif -%}
		{%- if state or country %}, {% endif -%}
		{%- if state %}{{- state -}}{%- endif -%}
		{%- if state and country %}, {% endif -%}
		{%- if country %}{{- country -}}{%- endif %}<br>
		{%- endif %}
		{%- if mobile %}
		{{ _("Mobile") }}: {{- mobile -}}
		{%- endif %}
	""")

    addr_display = frappe.render_template(address_template, doc.as_dict())
    return addr_display
