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
});
