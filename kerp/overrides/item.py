import frappe
from frappe.utils import cstr


def autoname(self, method=None):
    if self.is_stock_item and not self.has_variants:
        attrs_map = {
            "Item Name Abbreviation": "",
            "Item Assay Value": self.item_assay_value_kerp,
            "Item Variant Name": self.item_variant_name_kerp,
            "Item Pack Size": self.item_pack_size_kerp,
            "Brand": self.brand,
            "Manufacturer": self.manufacturer_kerp,
            "Manufacturer Item Code": (
                "0"
                if not self.manufacturer_item_code_kerp
                or self.manufacturer_item_code_kerp == "None"
                else self.manufacturer_item_code_kerp
            ),
            "Item Physical Form": self.item_physical_form_kerp,
            "Item Physical Sub-Form": self.item_physical_sub_form_kerp,
            "Item Group": self.item_group,
            "Item Grade": self.item_grade_kerp,
            "Item Grade Standard": self.item_grade_standard_kerp,
        }

        if self.variant_of:
            item_template = frappe.get_doc("Item", self.variant_of)
            item_name_abbr = frappe.get_value(
                "Item", self.variant_of, "item_name_abbreviation_kerp"
            )
            attrs_map["Item Name Abbreviation"] = item_name_abbr
            attributes_map = {
                attr.attribute: attr.attribute_value for attr in self.attributes
            }
            item_attrs = []
            for attr in attrs_map.keys():
                item_attrs.append(
                    frappe._dict(
                        {
                            "attribute": attr,
                            "attribute_value": attributes_map.get(
                                attr, attrs_map[attr]
                            ),
                        }
                    )
                )
        else:
            item_name_abbr = "".join([word[0] for word in self.item_name.split()])
            attrs_map["Item Name Abbreviation"] = item_name_abbr
            item_attrs = []
            for attr, attr_value in attrs_map.items():
                item_attrs.append(
                    frappe._dict({"attribute": attr, "attribute_value": attr_value})
                )

        abbreviations = []
        for attr in item_attrs:
            if (
                attr.attribute == "Item Name Abbreviation"
                or attr.attribute == "Manufacturer Item Code"
            ):
                abbreviations.append(attr.attribute_value)
                continue

            item_attribute = frappe.db.sql(
                """select i.numeric_values, v.abbr
			from `tabItem Attribute` i left join `tabItem Attribute Value` v
				on (i.name=v.parent)
			where i.name=%(attribute)s and (v.attribute_value=%(attribute_value)s or i.numeric_values = 1)""",
                {"attribute": attr.attribute, "attribute_value": attr.attribute_value},
                as_dict=True,
            )

            if not item_attribute:
                continue
                # frappe.throw(_('Invalid attribute {0} {1}').format(frappe.bold(attr.attribute),
                # 	frappe.bold(attr.attribute_value)), title=_('Invalid Attribute'),
                # 	exc=InvalidItemAttributeValueError)

            abbr_or_value = (
                cstr(attr.attribute_value)
                if item_attribute[0].numeric_values
                else item_attribute[0].abbr
            )
            abbreviations.append(abbr_or_value)

        abbreviations[7] += abbreviations.pop(8)

        if abbreviations:
            item_grade_standard = "" if abbreviations[-1] == "0" else abbreviations[-1]
            mfr_item_code = (
                ""
                if attrs_map["Manufacturer Item Code"] == "0"
                else attrs_map["Manufacturer Item Code"]
            )
            self.item_code = "-".join(abbreviations)
            self.name = self.item_code.upper()
            self.item_name = (
                f'{item_template.item_name} {attrs_map["Item Assay Value"]} {attrs_map["Item Variant Name"]} {item_grade_standard} - {attrs_map["Brand"]} {mfr_item_code}'.replace(
                    "  ", " "
                ).strip(),
            )

