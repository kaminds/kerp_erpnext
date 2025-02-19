# Copyright (c) 2025, Kaminds Nutrichem Private Limited and contributors
# For license information, please see license.txt

from frappe.model.document import Document
from kerp.utils import upsert_item_attribute, remove_item_attr_value


class ItemAssayValue(Document):
    def before_save(self):
        if self.name == "None":
            self.abbreviation = "0"
        else:
            self.abbreviation = self.value.replace(" ", "").upper()
        upsert_item_attribute(self.doctype, self.name, self.abbreviation)

    def on_trash(self):
        remove_item_attr_value(self.doctype, self.abbreviation)
