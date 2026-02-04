frappe.listview_settings["Sample Movement"] = {
	get_indicator: function (doc) {
		const status_colors = {
			"Pending Dispatch": "gray",
			Dispatched: "blue",
			Received: "green",
		};
		return [__(doc.status), status_colors[doc.status], "status,=," + doc.status];
	},
};
