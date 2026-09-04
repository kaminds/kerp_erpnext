frappe.ui.form.on("Customer", {
    refresh(frm) {
        frm.add_custom_button("Download Statement (PDF)", () => {
            // raw-response endpoint (streams the PDF, saves no File record) —
            // open it directly as a GET rather than going through frappe.call
            const params = new URLSearchParams({ customer: frm.doc.name });
            window.open(`/api/method/kerp.utils.party_statement.get_statement_pdf?${params.toString()}`);
        }, "View");

        frm.add_custom_button("Send Overdue Reminder", () => {
            frappe.confirm(
                __("Send an overdue-invoice reminder email to {0}?", [frm.doc.name]),
                () => {
                    frappe.call({
                        method: "kerp.utils.party_statement.send_overdue_reminder",
                        args: { customer: frm.doc.name },
                        freeze: true,
                        freeze_message: __("Sending..."),
                        callback: (r) => {
                            frappe.show_alert({
                                message: __("Reminder sent to {0}", [r.message.emails.join(", ")]),
                                indicator: "green",
                            });
                        },
                    });
                }
            );
        }, "View");
    },
});