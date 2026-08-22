frappe.ui.form.on("Sales Order", {
	setup: function (frm) {
		frm.set_query("transporter_kerp", function () {
			return {
				filters: {
					is_transporter: 1,
				},
			};
		});
	},

	transporter_kerp: function (frm) {
		if (frm.doc.transporter_kerp) {
			frappe.db
				.get_value("Supplier", frm.doc.transporter_kerp, "supplier_name")
				.then((r) => {
					if (r.message && r.message.supplier_name) {
						frm.set_value("transporter_name_kerp", r.message.supplier_name);
					}
				});
		} else {
			frm.set_value("transporter_name_kerp", "");
		}
	},

	refresh: function (frm) {
		if (frm.doc.items && frm.doc.items.length > 0) {
			let first_item = frm.doc.items[0];

			if (first_item.prevdoc_docname) {
				let quotation = first_item.prevdoc_docname;

				frappe.db
					.get_value("Quotation", quotation, [
						"transporter_kerp",
						"transporter_name_kerp",
					])
					.then((r) => {
						if (r.message) {
							let transporter = r.message.transporter_kerp;
							let transporter_name = r.message.transporter_name_kerp;

							if (transporter) {
								frm.set_value("transporter_kerp", transporter);
							} else if (transporter_name) {
								frm.set_value("transporter_name_kerp", transporter_name);
							}
						}
					});
			}
		}
	},

	get_email_recipient_filters: function (frm) {
		if (!frm.doc.customer) return;

		let filters = [
			["Dynamic Link", "link_doctype", "=", "Customer"],
			["Dynamic Link", "link_name", "=", frm.doc.customer],
		];
		return filters;
	},
});
