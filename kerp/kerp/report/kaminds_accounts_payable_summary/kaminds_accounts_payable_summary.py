# Copyright (c) 2026, Kaminds Nutrichem Private Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _, scrub
from erpnext.accounts.utils import get_currency_precision
from erpnext.accounts.party import get_partywise_advanced_payment_amount
from erpnext.accounts.report.accounts_receivable_summary.accounts_receivable_summary import get_gl_balance
from frappe.utils import flt
from kerp.kerp.report.kaminds_accounts_payable.kaminds_accounts_payable import (
    RestrictedReceivablePayableReport,
)
from erpnext.accounts.report.accounts_receivable_summary.accounts_receivable_summary import (
	AccountsReceivableSummary,
)

class RestrictedAccountsReceivableSummary(AccountsReceivableSummary):
    def get_data(self, args):
        self.data = []
        # ONLY CHANGE: use the restricted subclass instead of base ReceivablePayableReport
        self.receivables = RestrictedReceivablePayableReport(self.filters).run(args)[1]
        self.currency_precision = get_currency_precision() or 2

        self.get_party_total(args)

        party = None
        for party_type in self.party_type:
            if self.filters.get(scrub(party_type)):
                party = self.filters.get(scrub(party_type))

        party_advance_amount = (
            get_partywise_advanced_payment_amount(
                self.party_type,
                self.filters.report_date,
                self.filters.show_future_payments,
                self.filters.company,
                party=party,
            )
            or {}
        )

        if self.filters.show_gl_balance:
            gl_balance_map = get_gl_balance(self.filters.report_date, self.filters.company, self.account_type)

        for party, party_dict in self.party_total.items():
            if flt(party_dict.outstanding, self.currency_precision) == 0:
                continue

            row = frappe._dict()
            row.party = party
            if self.party_naming_by == "Naming Series":
                if self.account_type == "Payable":
                    doctype = "Supplier"
                    fieldname = "supplier_name"
                else:
                    doctype = "Customer"
                    fieldname = "customer_name"
                row.party_name = frappe.get_cached_value(doctype, party, fieldname)

            row.update(party_dict)
            row.advance = party_advance_amount.get(party, 0)
            row.paid -= row.advance

            if self.filters.show_gl_balance:
                row.gl_balance = gl_balance_map.get(party)
                row.diff = flt(row.outstanding) - flt(row.gl_balance)

            if self.filters.show_future_payments:
                row.remaining_balance = flt(row.outstanding) - flt(row.future_amount)

            self.data.append(row)

def execute(filters=None):
	args = {
		"account_type": "Payable",
		"naming_by": ["Buying Settings", "supp_master_name"],
	}
	return RestrictedAccountsReceivableSummary(filters).run(args)