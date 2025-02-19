# Copyright (c) 2025, Kaminds Nutrichem Private Limited and contributors
# For license information, please see license.txt

import frappe
from kerp.constants import UOM_ABBR
from frappe.model.document import Document
from kerp.utils import upsert_item_attribute, remove_item_attr_value


class ItemPackSize(Document):
    def autoname(self):
        if int(self.quantity) == 0:
            self.name = "None"
            self.abbreviation = "0"
            self.base_uom = "Nos"
            self.pack_size_uom = "Nos"
            return

        base_uom = frappe.get_doc("UOM", self.base_uom)

        if base_uom.must_be_whole_number:
            self.quantity = int(self.quantity)
            self.name = "{2} of {0} {1}".format(
                self.quantity, self.base_uom, self.pack_size_uom
            )
        else:
            self.name = "{0} {1} {2}".format(
                self.quantity, self.base_uom, self.pack_size_uom
            )

        self.abbreviation = "{0}{1}{2}".format(
            str(self.quantity).zfill(2),
            UOM_ABBR[self.base_uom],
            UOM_ABBR[self.pack_size_uom],
        ).upper()

    def before_save(self):
        upsert_item_attribute(self.doctype, self.name, self.abbreviation)

    def on_trash(self):
        remove_item_attr_value(self.doctype, self.abbreviation)
