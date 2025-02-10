# Copyright (c) 2025, Kaminds Nutrichem Private Limited and contributors
# For license information, please see license.txt

from frappe.model.document import Document
from kerp.utils import upsert_item_attribute, remove_item_attr_value


class ItemGradeStandard(Document):
    def before_insert(self):
        upsert_item_attribute(self.doctype, self.name, self.abbreviation)

    def on_trash(self):
        remove_item_attr_value(self.doctype, self.abbreviation)
