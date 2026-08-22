frappe.ui.form.on("Quotation", {
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

	get_email_recipient_filters: function (frm) {
		if (!frm.doc.party_name) return;

		let filters = [
			["Dynamic Link", "link_doctype", "=", "Customer"],
			["Dynamic Link", "link_name", "=", frm.doc.party_name],
		];
		return filters;
	},
});
