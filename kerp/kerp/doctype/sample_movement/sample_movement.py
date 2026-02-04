# Copyright (c) 2026, Kaminds Nutrichem Private Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate, flt
from frappe.model.document import Document


class SampleMovement(Document):
    def before_save(self):
        self.update_sample_request_dispatch()

    def validate(self):
        self.validate_against_sample_request()
        if self.courier_name and self.tracking_url and self.tracking_number:
            self.status = "Dispatched"

    def update_sample_request_dispatch(self):
        multiplier = 1
        for d in self.items:
            if not d.sample_request or not d.sr_item:
                continue
            frappe.db.sql(
                """
				UPDATE `tabSample Request Item`
				SET dispatched_qty = IFNULL(dispatched_qty, 0) + %s
				WHERE name = %s
			""",
                (multiplier * flt(d.qty), d.sr_item),
            )

        for req in {d.sample_request for d in self.items if d.sample_request}:
            frappe.get_doc("Sample Request", req).set_status()

    def validate_against_sample_request(self):
        for row in self.items:
            if not row.sample_request or not row.sr_item:
                continue

            sr_row = frappe.db.get_value(
                "Sample Request Item",
                row.sr_item,
                ["item_code", "qty", "uom"],
                as_dict=True,
            )

            if not sr_row:
                frappe.throw(
                    _("Row {0}: Linked Sample Request Item not found").format(row.idx)
                )

            if row.item_code != sr_row.item_code:
                frappe.throw(
                    _("Row {0}: Item Code must match Sample Request Item ({1})").format(
                        row.idx, sr_row.item_code
                    )
                )

            if row.uom != sr_row.uom:
                frappe.throw(
                    _("Row {0}: UOM must be same as Sample Request ({1})").format(
                        row.idx, sr_row.uom
                    )
                )

            if flt(row.qty) > flt(sr_row.qty):
                frappe.throw(
                    _(
                        "Row {0}: Quantity cannot exceed requested quantity ({1})"
                    ).format(row.idx, sr_row.qty)
                )


@frappe.whitelist()
def make_stock_entry(doc, method=None):
    doc = frappe.parse_json(doc)
    if doc.get("movement_type") == "Outward":
        stock_entry_type = "Material Issue"
    elif doc.get("movement_type") in ("Inward", "Return"):
        stock_entry_type = "Material Receipt"
    elif doc.get("movement_type") == "Consumption":
        stock_entry_type = "Material Issue"
    else:
        return

    se = frappe.new_doc("Stock Entry")
    se.stock_entry_type = stock_entry_type
    se.company = doc.get("company")
    se.posting_date = nowdate()

    for d in doc.get("items"):
        se.append(
            "items",
            {
                "status": "Draft",
                "item_code": d.get("item_code"),
                "item_name": d.get("item_name"),
                "qty": d.get("qty"),
                "uom": d.get("uom"),
                "use_serial_batch_fields": 1,
                "batch_no": d.get("batch_no"),
                "t_warehouse": d.get("warehouse")
                if stock_entry_type == "Material Receipt"
                else None,
                "s_warehouse": d.get("warehouse")
                if stock_entry_type == "Material Issue"
                else None,
            },
        )
    se.insert(ignore_permissions=True)
    frappe.db.set_value("Sample Movement", doc.get("name"), "stock_entry", se.name)
    return se.name
