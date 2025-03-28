frappe.ui.form.on("Sales Invoice", {
	refresh: function (frm) {
		if (frm.doc.items && frm.doc.items.length > 0) {
			let first_item = frm.doc.items[0];

			if (first_item.sales_order) {
				let sales_order_id = first_item.sales_order;

				frappe.db
					.get_value("Sales Order", sales_order_id, [
						"transporter_kerp",
						"transporter_name_kerp",
					])
					.then((r) => {
						if (r.message) {
							let transporter = r.message.transporter_kerp;
							let transporter_name = r.message.transporter_name_kerp;

							if (transporter) {
								frm.set_value("transporter", transporter);
							} else if (transporter_name) {
								frm.set_value("driver_name", transporter_name);
							}
						}
					});
			}
		}
	},
});
