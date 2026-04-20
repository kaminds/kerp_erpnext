frappe.after_ajax(() => {
	if (erpnext.SerialBatchPackageSelector) {

		const original = erpnext.SerialBatchPackageSelector.prototype.get_dialog_table_fields;

		erpnext.SerialBatchPackageSelector.prototype.get_dialog_table_fields = function () {

			let fields = original.call(this);

			// 🔍 find batch_no field
			fields.forEach(field => {
				if (field.fieldname === "batch_no") {

					// 🔁 override only get_query
					field.get_query = () => {
						let is_inward = false;
						if (
							(["Purchase Receipt", "Purchase Invoice"].includes(this.frm.doc.doctype) &&
								!this.frm.doc.is_return) ||
							(this.frm.doc.doctype === "Stock Entry" &&
								(this.frm.doc.purpose === "Material Receipt" ||
									(this.frm.doc.purpose === "Manufacture" && this.item.is_finished_item)))
						) {
							is_inward = true;
						}

						let include_expired_batches = this.include_expired_batches();

						return {
							query: "kerp.overrides.whitelist_methods.get_batch_no",
							filters: {
								item_code: this.item.item_code,
								warehouse:
									this.item.s_warehouse || this.item.t_warehouse || this.item.warehouse,
								is_inward: is_inward,
								include_expired_batches: include_expired_batches,
							},
						};
					}
				}
			});

			return fields;
		};

		erpnext.SerialBatchPackageSelector.prototype.get_auto_data = function () {
			let { qty, based_on } = this.dialog.get_values();

		if (this.item.serial_and_batch_bundle || this.item.rejected_serial_and_batch_bundle) {
			if (this.qty && qty === Math.abs(this.qty)) {
				return;
			}
		}

		if (this.item.serial_no || this.item.batch_no) {
			return;
		}

		if (!based_on) {
			based_on = "FIFO";
		}

		let warehouse = this.item.warehouse || this.item.s_warehouse;
		if (this.item?.is_rejected) {
			warehouse = this.item.rejected_warehouse;
		}

		if (qty) {
			frappe.call({
				method: "erpnext.stock.doctype.serial_and_batch_bundle.serial_and_batch_bundle.get_auto_data",
				args: {
					item_code: this.item.item_code,
					warehouse: warehouse,
					has_serial_no: this.item.has_serial_no,
					has_batch_no: this.item.has_batch_no,
					qty: qty,
					based_on: based_on,
					posting_date: this.frm.doc.posting_date,
					posting_time: this.frm.doc.posting_time,
					scio_detail: this.item.scio_detail,
				},
				callback: (r) => {
					if (r.message) {
						r.message.forEach((row) => {
							frappe.utils.add_link_title("Batch", row.batch_no, row.batch_no_display);
						});
						this.dialog.fields_dict.entries.df.data = r.message;
						this.dialog.fields_dict.entries.grid.refresh();
						}
					},
				});
			}
		}
	}
});

frappe.after_ajax(() => {
	if (erpnext.TransactionController) {
		const original = erpnext.TransactionController.prototype.set_query_for_batch;

		erpnext.TransactionController.prototype.set_query_for_batch = function (doc, cdt, cdn) {

			let result = original.call(this, doc, cdt, cdn);

			result.query = "kerp.overrides.whitelist_methods.get_batch_no";

			return result;
		};
	}
});