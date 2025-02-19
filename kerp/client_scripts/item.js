frappe.ui.form.on("Item", {
	refresh: function (frm) {
		if (frm.is_new()) {
			if (frm.doc.attributes !== undefined) {
				frm.doc.attributes.forEach((item, index) => {
					if (item.attribute === "Brand" || item.attribute === "Item Group") {
						frm.set_value(
							`${item.attribute.replace(/[\s\-]/g, "_").toLowerCase()}`,
							item.attribute_value
						);
					} else {
						frm.set_value(
							`${item.attribute.replace(/[\s\-]/g, "_").toLowerCase()}_kerp`,
							item.attribute_value
						);
					}
				});
			}
		}
	},
	item_pack_size_kerp: function (frm) {
		if (frm.doc.item_pack_size_kerp) {
			frappe.db.get_doc("Item Pack Size", frm.doc.item_pack_size_kerp).then((doc) => {
				frm.set_value("stock_uom", doc.base_uom);
				frm.clear_table("uoms");
				frm.refresh_field("uoms");
				frm.add_child("uoms", {
					uom: doc.base_uom,
					conversion_factor: 1,
				});
				frm.add_child("uoms", {
					uom: doc.pack_size_uom,
					conversion_factor: doc.quantity,
				});
				frm.refresh_field("uoms");
			});
		} else {
			frm.set_value("stock_uom", "");
			frm.clear_table("uoms");
			frm.refresh_field("uoms");
		}
	},
});

$.extend(erpnext.item, {
	show_single_variant_dialog: function (frm) {
		var fields = [];

		for (var i = 0; i < frm.doc.attributes.length; i++) {
			var fieldtype, desc;
			var row = frm.doc.attributes[i];

			if (!row.disabled) {
				if (row.numeric_values) {
					fieldtype = "Float";
					desc =
						"Min Value: " +
						row.from_range +
						" , Max Value: " +
						row.to_range +
						", in Increments of: " +
						row.increment;
				} else {
					fieldtype = "Data";
					desc = "";
				}
				fields = fields.concat({
					label: row.attribute,
					fieldname: row.attribute,
					fieldtype: fieldtype,
					reqd: 0,
					description: desc,
				});
			}
		}

		if (frm.doc.image) {
			fields.push({
				fieldtype: "Check",
				label: __("Create a variant with the template image."),
				fieldname: "use_template_image",
				default: 0,
			});
		}

		var d = new frappe.ui.Dialog({
			title: __("Create Variant"),
			fields: fields,
		});

		d.set_primary_action(__("Create"), function () {
			var args = d.get_values();
			if (!args) return;
			frappe.call({
				method: "erpnext.controllers.item_variant.get_variant",
				btn: d.get_primary_btn(),
				args: {
					template: frm.doc.name,
					args: d.get_values(),
				},
				callback: function (r) {
					// returns variant item
					if (r.message) {
						var variant = r.message;
						frappe.msgprint_dialog = frappe.msgprint(
							__("Item Variant {0} already exists with same attributes", [
								repl(
									'<a href="/app/item/%(item_encoded)s" class="strong variant-click">%(item)s</a>',
									{
										item_encoded: encodeURIComponent(variant),
										item: variant,
									}
								),
							])
						);
						frappe.msgprint_dialog.hide_on_page_refresh = true;
						frappe.msgprint_dialog.$wrapper
							.find(".variant-click")
							.on("click", function () {
								d.hide();
							});
					} else {
						d.hide();
						frappe.call({
							method: "erpnext.controllers.item_variant.create_variant",
							args: {
								item: frm.doc.name,
								args: d.get_values(),
								use_template_image: args.use_template_image,
							},
							callback: function (r) {
								var doclist = frappe.model.sync(r.message);
								frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
							},
						});
					}
				},
			});
		});

		d.show();

		$.each(d.fields_dict, function (i, field) {
			if (field.df.fieldtype !== "Data") {
				return;
			}

			$(field.input_area).addClass("ui-front");

			var input = field.$input.get(0);
			input.awesomplete = new Awesomplete(input, {
				minChars: 0,
				maxItems: 99,
				autoFirst: true,
				list: [],
			});
			input.field = field;

			field.$input
				.on("input", function (e) {
					input.awesomplete.evaluate();
					var term = e.target.value;
					var fieldname = e.target.dataset.fieldname;
					frappe.call({
						method: "erpnext.stock.doctype.item.item.get_item_attribute",
						args: {
							parent: i,
							attribute_value: term,
						},
						callback: function (r) {
							if (r.message) {
								if (
									fieldname !== "Item Physical Sub-Form" &&
									fieldname !== "Item Grade Standard"
								) {
									e.target.awesomplete.list = r.message.map(function (d) {
										return d.attribute_value;
									});
								}
							}
						},
					});
				})
				.on("focus", function (e) {
					$(e.target).val("").trigger("input");
				})
				.on("awesomplete-open", () => {
					let modal = field.$input.parents(".modal-dialog")[0];
					if (modal) {
						$(modal).removeClass("modal-dialog-scrollable");
					}
				})
				.on("awesomplete-selectcomplete", (e) => {
					let fieldname = e.target.dataset.fieldname;
					if (fieldname === "Item Physical Form") {
						get_item_physical_sub_forms(e.target.value);
					}
					if (fieldname === "Item Grade") {
						get_item_grade_standards(e.target.value);
					}
				});
		});
	},
});

function get_item_physical_sub_forms(form) {
	const item_physical_sub_form_field = document.querySelector(
		"div.modal.show input[data-fieldname='Item Physical Sub-Form']"
	);
	item_physical_sub_form_field.value = "";
	frappe.call({
		method: "frappe.client.get_list",
		args: {
			doctype: "Item Physical Form Reference",
			fields: ["parent"],
			filters: { item_physical_form: form },
			parent: "Item Physical Sub-Form",
		},
		callback: function (r) {
			if (r.message) {
				item_physical_sub_form_field.awesomplete.list = r.message.map(function (d) {
					return d.parent;
				});
			}
		},
	});
}

function get_item_grade_standards(item_grade) {
	const item_grade_standard_form_field = document.querySelector(
		"div.modal.show input[data-fieldname='Item Grade Standard']"
	);
	item_grade_standard_form_field.value = "";
	frappe.call({
		method: "frappe.client.get_list",
		args: {
			doctype: "Item Grade Reference",
			fields: ["parent"],
			filters: { item_grade: item_grade },
			parent: "Item Grade Standard",
		},
		callback: function (r) {
			if (r.message) {
				item_grade_standard_form_field.awesomplete.list = r.message.map(function (d) {
					return d.parent;
				});
			}
		},
	});
}
