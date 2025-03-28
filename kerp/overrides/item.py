import frappe
import re
from frappe.utils import cstr


def autoname(self, method=None):
    if self.is_stock_item and not self.has_variants:
        attrs_map = {
            "Item Name Abbreviation": "",
            "Item Assay Value": self.item_assay_value_kerp,
            "Item Variant Name": self.item_variant_name_kerp,
            "Item Pack Size": self.item_pack_size_kerp,
            "Brand": self.brand,
            "Brand Item Reference": (
                "0"
                if not self.brand_item_reference_kerp
                or self.brand_item_reference_kerp == "None"
                else re.sub(r"\s+", "", self.brand_item_reference_kerp)
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
                or attr.attribute == "Brand Item Reference"
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

        if abbreviations[6] == "0":
            abbreviations.pop(7)
        else:
            abbreviations[6] += abbreviations.pop(7)

        if abbreviations:
            item_assay_value = (
                ""
                if attrs_map["Item Assay Value"] == "None"
                else attrs_map["Item Assay Value"]
            )
            item_variant_name = (
                ""
                if attrs_map["Item Variant Name"] == "None"
                else attrs_map["Item Variant Name"]
            )
            item_grade_standard = (
                ""
                if attrs_map["Item Grade Standard"] == "None"
                else attrs_map["Item Grade Standard"]
            )
            brand_item_ref = (
                ""
                if attrs_map["Brand Item Reference"] == "0"
                else f"({attrs_map['Brand Item Reference']})"
            )
            item_brand = (
                "" if attrs_map["Brand"] == "None" else f"- {attrs_map['Brand']}"
            )

            self.item_code = "-".join(abbreviations)
            self.name = self.item_code.upper()
            if self.variant_of:
                self.item_name = f"{item_template.item_name} {item_assay_value} {item_variant_name} {item_grade_standard} {brand_item_ref} {item_brand}"
            else:
                self.item_name = f"{self.item_name} {item_assay_value} {item_variant_name} {item_grade_standard} {brand_item_ref} {item_brand}"
            self.item_name = re.sub(r"\s{2,}", " ", self.item_name).strip()
