import frappe
from frappe.utils import flt

def get_qty_based_available_batches(available_batches, qty):
	batches = []
	title_field = frappe.get_meta("Batch").get_title_field()

	for batch in available_batches:
		if qty <= 0:
			break

		batch_display_name = frappe.get_cached_value("Batch", batch.batch_no, title_field)
		batch_qty = flt(batch.qty)

		if qty > batch_qty:
			batches.append(
				frappe._dict(
					{
						"batch_no": batch.batch_no,
						"batch_no_display": batch_display_name,
						"qty": batch_qty,
						"warehouse": batch.warehouse,
					}
				)
			)
			qty -= batch_qty
		else:
			batches.append(
				frappe._dict(
					{
						"batch_no": batch.batch_no,
						"batch_no_display": batch_display_name,
						"qty": qty,
						"warehouse": batch.warehouse,
					}
				)
			)
			qty = 0

	return batches
