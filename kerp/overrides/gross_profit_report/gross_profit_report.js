// overrides/gross_profit_report/gross_profit_report.js
// Full copy of ERPNext's erpnext/accounts/report/gross_profit/gross_profit.js
// + custom "Export (Formatted)" button.
// NOTE: if ERPNext updates gross_profit.js upstream, re-sync this file manually.

frappe.query_reports["Gross Profit"] = {
    filters: [
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company"),
            reqd: 1,
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[1],
            reqd: 1,
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[2],
            reqd: 1,
        },
        {
            fieldname: "sales_invoice",
            label: __("Sales Invoice"),
            fieldtype: "Link",
            options: "Sales Invoice",
        },
        {
            fieldname: "group_by",
            label: __("Group By"),
            fieldtype: "Select",
            options:
                "Invoice\nItem Code\nItem Group\nBrand\nWarehouse\nCustomer\nCustomer Group\nTerritory\nSales Person\nProject\nCost Center\nMonthly\nPayment Term",
            default: "Invoice",
        },
        {
            fieldname: "item_group",
            label: __("Item Group"),
            fieldtype: "Link",
            options: "Item Group",
        },
        {
            fieldname: "sales_person",
            label: __("Sales Person"),
            fieldtype: "Link",
            options: "Sales Person",
        },
        {
            fieldname: "warehouse",
            label: __("Warehouse"),
            fieldtype: "Link",
            options: "Warehouse",
            get_query: function () {
                var company = frappe.query_report.get_filter_value("company");
                return {
                    filters: [["Warehouse", "company", "=", company]],
                };
            },
        },
        {
            fieldname: "cost_center",
            label: __("Cost Center"),
            fieldtype: "MultiSelectList",
            options: "Cost Center",
            get_data: function (txt) {
                return frappe.db.get_link_options("Cost Center", txt, {
                    company: frappe.query_report.get_filter_value("company"),
                });
            },
        },
        {
            fieldname: "project",
            label: __("Project"),
            fieldtype: "MultiSelectList",
            options: "Project",
            get_data: function (txt) {
                return frappe.db.get_link_options("Project", txt, {
                    company: frappe.query_report.get_filter_value("company"),
                });
            },
        },
        {
            fieldname: "include_returned_invoices",
            label: __("Include Returned Invoices (Stand-alone)"),
            fieldtype: "Check",
            default: 1,
        },
    ],
    tree: true,
    name_field: "parent",
    parent_field: "parent_invoice",
    initial_depth: 3,
    formatter: function (value, row, column, data, default_formatter) {
        if (column.fieldname == "sales_invoice" && column.options == "Item" && data && data.indent == 0) {
            column._options = "Sales Invoice";
        } else {
            column._options = "";
        }
        value = default_formatter(value, row, column, data);

        if (data && (data.indent == 0.0 || (row[1] && row[1].content == "Total"))) {
            value = $(`<span>${value}</span>`);
            var $value = $(value).css("font-weight", "bold");
            value = $value.wrap("<p></p>").parent().html();
        }

        return value;
    },
    onload(report) {
        report.page.add_inner_button(__("Export (Formatted)"), function () {
            const filters = report.get_filter_values(true);

            // export_gross_profit_xlsx only supports Group By "Invoice" —
            // checked here, before window.open, so a mismatch shows a normal
            // frappe dialog instead of a raw Server Error page in a new tab
            // (a GET navigation like window.open has no JS context to catch
            // and prettify an error the way frappe.call responses do)
            if ((filters.group_by || "Invoice") !== "Invoice") {
                frappe.msgprint({
                    title: __("Group By Not Supported"),
                    message: __('This export only supports Group By "Invoice" (currently "{0}").', [
                        filters.group_by,
                    ]),
                    indicator: "orange",
                });
                return;
            }

            const params = new URLSearchParams({
                filters: JSON.stringify(filters),
            }).toString();
            window.open(
                `/api/method/kerp.overrides.gross_profit_report.gross_profit_report.export_gross_profit_xlsx?${params}`
            );
        });
    },
};

erpnext.utils.add_dimensions("Gross Profit", 15);