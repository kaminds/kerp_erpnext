app_name = "kerp"
app_title = "KERP"
app_publisher = "Kaminds Nutrichem Private Limited"
app_description = "Customizations for Kaminds ERP"
app_email = "tech@kaminds.com"
app_license = "agpl-3.0"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "kerp",
# 		"logo": "/assets/kerp/logo.png",
# 		"title": "KERP",
# 		"route": "/kerp",
# 		"has_permission": "kerp.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/kerp/css/kerp.css"
# app_include_js = "/assets/kerp/js/kerp.js"

# include js, css files in header of web template
# web_include_css = "/assets/kerp/css/kerp.css"
# web_include_js = "/assets/kerp/js/kerp.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "kerp/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Item": "client_scripts/item.js",
    "Sales Invoice": "client_scripts/sales_invoice.js",
    "Sales Order": "client_scripts/sales_order.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "kerp/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "kerp.utils.jinja_methods",
# 	"filters": "kerp.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "kerp.install.before_install"
after_install = "kerp.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "kerp.uninstall.before_uninstall"
# after_uninstall = "kerp.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "kerp.utils.before_app_install"
# after_app_install = "kerp.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "kerp.utils.before_app_uninstall"
# after_app_uninstall = "kerp.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "kerp.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Item": {"autoname": "kerp.overrides.item.autoname"},
    "BOM": {"autoname": "kerp.overrides.bom.autoname"},
    "Item Group": {
        "before_insert": "kerp.overrides.item_group.before_insert",
        "on_trash": "kerp.overrides.item_group.on_trash",
    },
    "Brand": {
        "before_insert": "kerp.overrides.brand.before_insert",
        "on_trash": "kerp.overrides.brand.on_trash",
    },
    "Batch": {
        "autoname": "kerp.overrides.batch.autoname",
        "before_save": "kerp.overrides.batch.before_save",
    },
    "Address": {"autoname": "kerp.overrides.address.autoname"},
    "Contact": {"autoname": "kerp.overrides.contact.autoname"},
    "Customer": {"autoname": "kerp.overrides.customer.autoname"},
    "Supplier": {"autoname": "kerp.overrides.supplier.autoname"},
    "Sales Invoice": {"before_insert": "kerp.overrides.sales_invoice.before_insert"},
    "Sales Order": {"before_insert": "kerp.overrides.sales_order.before_insert"},
    "Purchase Invoice": {
        "before_insert": "kerp.overrides.purchase_invoice.before_insert"
    },
    "Purchase Order": {"before_insert": "kerp.overrides.purchase_order.before_insert"},
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"kerp.tasks.all"
# 	],
# 	"daily": [
# 		"kerp.tasks.daily"
# 	],
# 	"hourly": [
# 		"kerp.tasks.hourly"
# 	],
# 	"weekly": [
# 		"kerp.tasks.weekly"
# 	],
# 	"monthly": [
# 		"kerp.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "kerp.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "kerp.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "kerp.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["kerp.utils.before_request"]
# after_request = ["kerp.utils.after_request"]

# Job Events
# ----------
# before_job = ["kerp.utils.before_job"]
# after_job = ["kerp.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"kerp.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
