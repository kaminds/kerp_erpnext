// Copyright (c) 2026, Kaminds Nutrichem Private Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sample Request", {
	setup: function (frm) {
		set_party_query(frm);
		set_common_queries(frm);
	},

	refresh: function (frm) {
		if (["Approved", "Partially Dispatched"].includes(frm.doc.status) && !frm.doc.__islocal) {
			frm.add_custom_button("Create Movement", () => {
				frappe.model.open_mapped_doc({
					method: "kerp.kerp.doctype.sample_request.sample_request.make_sample_movement",
					frm: frm,
				});
			});
		}
	},

	request_type: function (frm) {
		frm.set_value("sample_from_to", "");
		set_party_query(frm);
	},

	sample_from_to: function (frm) {
		frm.doc.party = "";
		frm.refresh_field("party");
		frm.trigger("party");
	},

	party: function (frm) {
		frappe.dynamic_link = {
			doc: frm.doc,
			fieldname: "party",
			doctype: frm.doc.sample_from_to,
		};
		frappe.call({
			method: "kerp.kerp.utils.party.get_party_details",
			args: {
				party_type: frm.doc.sample_from_to,
				party: frm.doc.party,
			},
			freeze: true,
			callback: function (r) {
				if (r.message) {
					frm.set_value("party_name", r.message.party_name || "");
					frm.set_value("contact", r.message.contact || "");
					frm.set_value("address", r.message.address || "");
					frm.set_value("contact_person", r.message.contact_person || "");
					frm.set_value("contact_person_email", r.message.contact_person_email || "");
					frm.set_value(
						"contact_person_mobile",
						`+91-${r.message.contact_person_mobile ? r.message.contact_person_mobile : ""}`,
					);
				}
			},
		});
	},

	contact: function (frm) {
		if (!frm.doc.contact) {
			frm.set_value("contact_person", "");
			frm.set_value("contact_person_email", "");
			frm.set_value("contact_person_mobile", "");
			return;
		}

		frappe.call({
			method: "frappe.contacts.doctype.contact.contact.get_contact_details",
			args: {
				contact: frm.doc.contact,
			},
			freeze: true,
			callback: function (r) {
				if (r.message) {
					frm.set_value("contact_person", r.message.contact_display || "");
					frm.set_value("contact_person_email", r.message.contact_email || "");
					frm.set_value(
						"contact_person_mobile",
						`+91-${r.message.contact_mobile ? r.message.contact_mobile : ""}`,
					);
				}
			},
		});
	},

	address(frm) {
		if (!frm.doc.address) {
			frm.set_value("party_address", "");
			return;
		}

		frappe.call({
			method: "kerp.kerp.utils.address.get_address_display",
			args: { address: frm.doc.address },
			freeze: true,
			callback: (r) => {
				if (r.message) frm.set_value("party_address", r.message);
			},
		});
	},
});

function set_party_query(frm) {
	const outwardParties = ["Customer", "CRM Lead"];
	const inwardParties = ["Supplier"];

	let parties = [];
	if (frm.doc.request_type === "Issue") parties = outwardParties;
	if (frm.doc.request_type === "Receipt") parties = inwardParties;

	frm.set_query("sample_from_to", () => ({
		filters: { name: ["in", parties] },
	}));
}

function set_common_queries(frm) {
	frm.set_query("uom", "items", () => ({
		filters: { name: ["in", ["Kg", "Gram"]] },
	}));

	frm.set_query("contact", erpnext.queries.contact_query);
	frm.set_query("address", erpnext.queries.address_query);
}
