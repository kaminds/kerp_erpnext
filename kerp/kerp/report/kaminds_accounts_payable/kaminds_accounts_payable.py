# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from erpnext.accounts.report.accounts_receivable.accounts_receivable import ReceivablePayableReport

PRIVILEGED_ROLES = {"System Manager", "Accounts Manager"}

def _user_can_bypass(user):
    if user == "Administrator":
        return True
    return bool(set(frappe.get_roles(user)).intersection(PRIVILEGED_ROLES))


def _get_restricted_parties(user, party_type):
	if _user_can_bypass(user):
		return []

	return frappe.get_all(
        "Party Access Restriction Detail",
		filters={"parenttype": "Party Access Restriction", "party_type": party_type},
		pluck="party"
    )

class RestrictedReceivablePayableReport(ReceivablePayableReport):
    def add_user_permission_filters(self):
        # keep native User Permission behavior intact
        super().add_user_permission_filters()

        user = frappe.session.user
        if _user_can_bypass(user):
            return

        for party_type in self.party_type:
            restricted = _get_restricted_parties(user, party_type)
            if restricted:
                self.qb_selection_filter.append(
                    (self.ple.party_type != party_type) | (self.ple.party.notin(restricted))
                )

def execute(filters=None):
	args = {
		"account_type": "Payable",
		"naming_by": ["Buying Settings", "supp_master_name"],
	}
	return RestrictedReceivablePayableReport(filters).run(args)
