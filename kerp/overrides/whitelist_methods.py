import frappe
from collections import OrderedDict
from frappe.query_builder.functions import Concat, Sum
from frappe.utils import today

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_batch_no(doctype, txt, searchfield, start, page_len, filters):
	doctype = "Batch"
	meta = frappe.get_meta(doctype, cached=True)
	searchfields = meta.get_search_fields()
	title_field = meta.get_title_field()
	page_len = 300

	batches = get_batches_from_stock_ledger_entries(searchfields, title_field, txt, filters, start, page_len)
	batches.extend(get_batches_from_serial_and_batch_bundle(searchfields, title_field, txt, filters, start, page_len))

	filtered_batches = get_filterd_batches(batches)

	if filters.get("is_inward"):
		filtered_batches.extend(get_empty_batches(filters, start, page_len, filtered_batches, txt, title_field))

	return filtered_batches

def get_batches_from_stock_ledger_entries(searchfields, title_field, txt, filters, start=0, page_len=100):
	item_code = filters.get("item_code") or filters.get("item")
	stock_ledger_entry = frappe.qb.DocType("Stock Ledger Entry")
	batch_table = frappe.qb.DocType("Batch")

	expiry_date = filters.get("posting_date") or today()

	query = (
		frappe.qb.from_(stock_ledger_entry)
		.inner_join(batch_table)
		.on(batch_table.name == stock_ledger_entry.batch_no)
		.select(
			stock_ledger_entry.batch_no,
			batch_table[title_field],
			Sum(stock_ledger_entry.actual_qty).as_("qty"),
			batch_table.stock_uom,
		)
		.where(stock_ledger_entry.is_cancelled == 0)
		.where(
			(stock_ledger_entry.item_code == item_code)
			& (batch_table.disabled == 0)
			& (stock_ledger_entry.batch_no.isnotnull())
		)
		.groupby(stock_ledger_entry.batch_no, stock_ledger_entry.warehouse)
		.having(Sum(stock_ledger_entry.actual_qty) != 0)
		.offset(start)
		.limit(page_len)
	)

	if not filters.get("include_expired_batches"):
		query = query.where((batch_table.expiry_date >= expiry_date) | (batch_table.expiry_date.isnull()))

	query = query.select(
		Concat("MFG-", batch_table.manufacturing_date).as_("manufacturing_date"),
		Concat("EXP-", batch_table.expiry_date).as_("expiry_date"),
	)

	if filters.get("warehouse"):
		query = query.where(stock_ledger_entry.warehouse == filters.get("warehouse"))

	for field in searchfields:
		query = query.select(batch_table[field])

	if txt:
		txt_condition = batch_table.name.like(f"%{txt}%")
		for field in [*searchfields, "name"]:
			txt_condition |= batch_table[field].like(f"%{txt}%")

		query = query.where(txt_condition)

	return query.run(as_list=1) or []


def get_batches_from_serial_and_batch_bundle(searchfields, title_field, txt, filters, start=0, page_len=100):
	item_code = filters.get("item_code") or filters.get("item")
	bundle = frappe.qb.DocType("Serial and Batch Entry")
	stock_ledger_entry = frappe.qb.DocType("Stock Ledger Entry")
	batch_table = frappe.qb.DocType("Batch")

	expiry_date = filters.get("posting_date") or today()

	bundle_query = (
		frappe.qb.from_(bundle)
		.inner_join(stock_ledger_entry)
		.on(bundle.parent == stock_ledger_entry.serial_and_batch_bundle)
		.inner_join(batch_table)
		.on(batch_table.name == bundle.batch_no)
		.select(
			bundle.batch_no,
			batch_table[title_field],
			Sum(bundle.qty).as_("qty"),
			batch_table.stock_uom,
		)
		.where(stock_ledger_entry.is_cancelled == 0)
		.where(
			(stock_ledger_entry.item_code == item_code)
			& (batch_table.disabled == 0)
			& (stock_ledger_entry.serial_and_batch_bundle.isnotnull())
		)
		.groupby(bundle.batch_no, bundle.warehouse)
		.having(Sum(bundle.qty) != 0)
		.offset(start)
		.limit(page_len)
	)

	if not filters.get("include_expired_batches"):
		bundle_query = bundle_query.where(
			(batch_table.expiry_date >= expiry_date) | (batch_table.expiry_date.isnull())
		)

	bundle_query = bundle_query.select(
		Concat("MFG-", batch_table.manufacturing_date),
		Concat("EXP-", batch_table.expiry_date),
	)

	if filters.get("warehouse"):
		bundle_query = bundle_query.where(stock_ledger_entry.warehouse == filters.get("warehouse"))

	for field in searchfields:
		bundle_query = bundle_query.select(batch_table[field])

	if txt:
		txt_condition = batch_table.name.like(f"%{txt}%")
		for field in [*searchfields, "name"]:
			txt_condition |= batch_table[field].like(f"%{txt}%")

		bundle_query = bundle_query.where(txt_condition)

	return bundle_query.run(as_list=1)

def get_filterd_batches(data):
	batches = OrderedDict()

	for batch_data in data:
		if batch_data[0] not in batches:
			batches[batch_data[0]] = list(batch_data)
		else:
			batches[batch_data[0]][2] += batch_data[2]

	filterd_batch = []
	for _batch, batch_data in batches.items():
		if batch_data[2] > 0:
			filterd_batch.append(tuple(batch_data))

	return filterd_batch

def get_empty_batches(filters, start, page_len, filtered_batches=None, txt=None, title_field="name"):
	item_code = filters.get("item_code") or filters.get("item")
	query_filter = {"item": item_code, "disabled": 0}
	if txt:
		query_filter["name"] = ("like", f"%{txt}%")

	exclude_batches = [batch[0] for batch in filtered_batches] if filtered_batches else []
	if exclude_batches:
		query_filter["name"] = ("not in", exclude_batches)

	batches = frappe.get_all(
        "Batch",
        fields=["name", title_field, "stock_uom", "manufacturing_date", "expiry_date"],
        filters=query_filter,
        limit_start=start,
        limit_page_length=page_len,
    )
	
	result = []
	for b in batches:
		mfg = f"MFG-{b.manufacturing_date}" if b.manufacturing_date else ""
		exp = f"EXP-{b.expiry_date}" if b.expiry_date else ""
		result.append((b.name, b.get(title_field) or b.name, 0.0, b.stock_uom or "", mfg, exp))
		
	return result