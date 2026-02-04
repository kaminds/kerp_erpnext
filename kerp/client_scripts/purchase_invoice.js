frappe.ui.form.on("Purchase Invoice", {
	get_email_recipient_filters: function (frm) {
		if (!frm.doc.customer) return;

		let filters = [
			["Dynamic Link", "link_doctype", "=", "Supplier"],
			["Dynamic Link", "link_name", "=", frm.doc.supplier],
		];
		return filters;
	},
});
