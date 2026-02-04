frappe.listview_settings["Sample Request"] = {
	get_indicator: function (doc) {
		const status_colors = {
			"Pending Approval": "gray",
			"Partially Dispatched": "orange",
			Approved: "blue",
			Rejected: "red",
			Fulfilled: "green",
			Closed: "red",
		};
		return [__(doc.status), status_colors[doc.status], "status,=," + doc.status];
	},
};
