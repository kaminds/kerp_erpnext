# Copyright (c) 2026, Kaminds Nutrichem Private Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class KERPAccountsSettings(Document):
	def validate(self):
		if self.outstanding_reminder_sender_email_account and not frappe.db.get_value(
			"Email Account", self.outstanding_reminder_sender_email_account, "enable_outgoing"
		):
			frappe.msgprint(
				_(
					"{0} does not have Enable Outgoing checked — reminders sent from it will fail "
					"until that's turned on."
				).format(self.outstanding_reminder_sender_email_account),
				indicator="orange",
				title=_("Outgoing Not Enabled"),
			)

		if self.outstanding_reminder_cc_addresses:
			# throws immediately naming the first bad entry, same utility
			# frappe itself uses to validate recipient fields
			frappe.utils.validate_email_address(self.outstanding_reminder_cc_addresses, throw=True)


def get_settings():
	"""Cached accessor — same pattern as any other Frappe Settings singleton
	(e.g. frappe.get_cached_doc("Selling Settings"))."""
	return frappe.get_cached_doc("KERP Accounts Settings")
