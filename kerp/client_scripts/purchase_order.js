frappe.ui.form.on("Purchase Order", {

	refresh(frm) {
		frm.set_query("transporter_name_kerp", () => ({
			query: "kerp.utils.get_transporter_list",
		}));

		frappe.meta.get_docfield("Purchase Order", "transporter_name_kerp").ignore_validation = 1;

		frm.set_query("shipping_contact_person_kerp", erpnext.queries.company_contact_query);

		if (frm.is_new() && !frm.doc.shipping_contact_person_kerp) {
			frappe.db.get_value("Contact", { "email_id": frappe.session.user }, "name")
				.then((r) => {
					if (r.message && r.message.name) {
						frm.set_value("shipping_contact_person_kerp", r.message.name);
					}
				});
		}
	},

	get_email_recipient_filters: function (frm) {
		if (!frm.doc.supplier) return;

		let filters = [
			["Dynamic Link", "link_doctype", "=", "Supplier"],
			["Dynamic Link", "link_name", "=", frm.doc.supplier],
		];
		return filters;
	},
});
