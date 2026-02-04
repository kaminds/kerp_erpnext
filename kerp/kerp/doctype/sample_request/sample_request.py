# Copyright (c) 2026, Kaminds Nutrichem Private Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


@frappe.whitelist()
def make_sample_movement(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.status = "Pending Dispatch"
        if source.request_type == "Issue":
            target.movement_type = "Outward"
        elif source.request_type == "Receipt":
            target.movement_type = "Inward"

    doc = get_mapped_doc(
        "Sample Request",
        source_name,
        {
            "Sample Request": {
                "doctype": "Sample Movement",
            },
            "Sample Request Item": {
                "doctype": "Sample Movement Item",
                "field_map": {
                    "name": "sr_item",
                    "parent": "sample_request",
                },
            },
        },
        target_doc,
        set_missing_values,
    )

    return doc


class SampleRequest(Document):
    def set_status(self):
        total_qty = sum(d.qty for d in self.items)
        dispatched = sum(d.dispatched_qty for d in self.items)

        if dispatched == 0:
            self.status = "Approved"
        elif dispatched < total_qty:
            self.status = "Partially Dispatched"
        else:
            self.status = "Fulfilled"

        self.db_set("status", self.status)
