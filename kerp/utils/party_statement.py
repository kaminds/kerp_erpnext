# Copyright (c) 2026
# Customer statement + overdue-reminder email utilities.
#
# Whitelisted endpoints:
#   get_statement_pdf(customer, company, report_date)
#     -> streams the full branded PDF statement (all outstanding invoices)
#        straight to the browser — nothing is saved as a File
#   send_overdue_reminder(customer, company, report_date)
#     -> emails one customer's overdue invoices only (table in the email body,
#        same PDF statement attached but filtered to overdue invoices)
#   send_overdue_reminders(company, report_date)
#     -> loops send_overdue_reminder over every customer with an overdue invoice
#
# get_statement_pdf is a raw-response endpoint (sets frappe.local.response.filecontent),
# not a JSON one, so it can't go through frappe.call — open it directly as a GET:
#   window.open(
#     "/api/method/kerp.utils.party_statement.get_statement_pdf?" +
#     new URLSearchParams({ customer: "Bright Lifecare Pvt Ltd" })
#   )
# or wire it to a "Download Statement" / "Send Overdue Reminder" button on the
# Customer form / the Party-wise Outstanding Summary report.

import frappe
from frappe import _
from frappe.utils import add_days, cint, fmt_money, getdate, nowdate, flt
from frappe.utils.pdf import get_pdf

from kerp.kerp.doctype.kerp_accounts_settings.kerp_accounts_settings import get_settings
from kerp.overrides.communication import get_sales_team_emails_for_invoice

AGEING_RANGES = (30, 60, 90)

# fallback only — the real value comes from KERP Accounts Settings; this
# just covers a fresh install before that singleton has been saved once
DEFAULT_DUE_SOON_WINDOW_DAYS = 3


def _get_due_soon_window_days():
	settings = get_settings()
	return settings.outstanding_reminder_due_soon_window_days or DEFAULT_DUE_SOON_WINDOW_DAYS


def _get_sender_email():
	"""None (Frappe's own default-outgoing resolution) unless a specific
	Email Account is configured in KERP Accounts Settings."""
	settings = get_settings()
	if not settings.outstanding_reminder_sender_email_account:
		return None
	return frappe.db.get_value(
		"Email Account", settings.outstanding_reminder_sender_email_account, "email_id"
	)


def _get_cc_emails(invoices):
	"""CC list for a reminder: the static addresses configured in KERP
	Accounts Settings, plus the sales team (+ their managers) for every
	invoice this reminder covers — reuses the same resolver
	kerp.overrides.communication uses to CC the sales team on Sales Invoice
	Communications, so both places stay in sync with one lookup."""
	emails = set(frappe.utils.split_emails(get_settings().outstanding_reminder_cc_addresses))
	for inv in invoices:
		emails.update(get_sales_team_emails_for_invoice(inv["name"]) or [])
	return sorted(emails)


def _get_invoice_rows(customer, company, report_date, overdue_only=False):
	"""Shared source of truth for both the full statement and the overdue
	reminder — same query, same ageing-bucket logic, just an extra filter."""
	SalesInvoice = frappe.qb.DocType("Sales Invoice")
	Contact = frappe.qb.DocType("Contact")

	# join to Contact rather than trust Sales Invoice's own contact_email —
	# that field is a snapshot taken when the invoice was saved, so it goes
	# stale the moment the contact's email is updated afterwards
	query = (
		frappe.qb.from_(SalesInvoice)
		.left_join(Contact)
		.on(Contact.name == SalesInvoice.contact_person)
		.select(
			SalesInvoice.name,
			SalesInvoice.posting_date,
			SalesInvoice.due_date,
			SalesInvoice.outstanding_amount.as_("outstanding"),
			Contact.email_id.as_("contact_email"),
		)
		.where(SalesInvoice.docstatus == 1)
		.where(SalesInvoice.company == company)
		.where(SalesInvoice.customer == customer)
		.where(SalesInvoice.outstanding_amount != 0)
		.where(SalesInvoice.posting_date <= report_date)
		.orderby(SalesInvoice.due_date)
	)
	if overdue_only:
		query = query.where(SalesInvoice.due_date.isnotnull()).where(SalesInvoice.due_date < report_date)

	rows = query.run(as_dict=True)

	invoices = []
	total_due = 0.0
	total_overdue = 0.0
	buckets = {"1-30": 0.0, "31-60": 0.0, "61-90": 0.0, "90+": 0.0}

	for r in rows:
		overdue_days = (report_date - getdate(r.due_date)).days if r.due_date else 0
		is_overdue = bool(r.due_date and overdue_days > 0)
		total_due += flt(r.outstanding)

		age_bucket = 0
		if is_overdue:
			total_overdue += flt(r.outstanding)
			if overdue_days <= AGEING_RANGES[0]:
				buckets["1-30"] += flt(r.outstanding)
				age_bucket = 1
			elif overdue_days <= AGEING_RANGES[1]:
				buckets["31-60"] += flt(r.outstanding)
				age_bucket = 2
			elif overdue_days <= AGEING_RANGES[2]:
				buckets["61-90"] += flt(r.outstanding)
				age_bucket = 3
			else:
				buckets["90+"] += flt(r.outstanding)
				age_bucket = 4

		invoices.append({
			"name": r.name,
			"posting_date": r.posting_date,
			"due_date": r.due_date,
			"outstanding": r.outstanding,
			"is_overdue": is_overdue,
			"overdue_days": overdue_days if is_overdue else 0,
			"age_bucket": age_bucket,
			"contact_email": r.contact_email,
		})

	# oldest / most overdue first, matches the report's sort order
	invoices.sort(key=lambda x: x["overdue_days"], reverse=True)
	return invoices, total_due, total_overdue, buckets


def _get_due_soon_invoices(customer, company, report_date, days_ahead=None):
	"""Invoices that aren't overdue yet but fall due within `days_ahead` days —
	a courtesy heads-up alongside the overdue table, not a replacement for it."""
	# can't default days_ahead straight to the settings value — default args
	# are evaluated once at import time, so a later settings change would
	# never be picked up without an app restart
	if days_ahead is None:
		days_ahead = _get_due_soon_window_days()

	SalesInvoice = frappe.qb.DocType("Sales Invoice")
	Contact = frappe.qb.DocType("Contact")
	due_before = add_days(report_date, days_ahead)

	rows = (
		frappe.qb.from_(SalesInvoice)
		.left_join(Contact)
		.on(Contact.name == SalesInvoice.contact_person)
		.select(
			SalesInvoice.name,
			SalesInvoice.posting_date,
			SalesInvoice.due_date,
			SalesInvoice.outstanding_amount.as_("outstanding"),
			Contact.email_id.as_("contact_email"),
		)
		.where(SalesInvoice.docstatus == 1)
		.where(SalesInvoice.company == company)
		.where(SalesInvoice.customer == customer)
		.where(SalesInvoice.outstanding_amount != 0)
		.where(SalesInvoice.posting_date <= report_date)
		.where(SalesInvoice.due_date.isnotnull())
		.where(SalesInvoice.due_date >= report_date)
		.where(SalesInvoice.due_date <= due_before)
		.orderby(SalesInvoice.due_date)
	).run(as_dict=True)

	return [{
		"name": r.name,
		"posting_date": r.posting_date,
		"due_date": r.due_date,
		"outstanding": r.outstanding,
		"days_until_due": (getdate(r.due_date) - report_date).days,
		"contact_email": r.contact_email,
	} for r in rows]


def _render_statement_pdf(company, customer, report_date, invoices, total_due, total_overdue, buckets, currency):
	customer_name = frappe.get_cached_value("Customer", customer, "customer_name") or customer
	context = {
		"company_name": company,
		"party": customer_name,
		"report_date": report_date,
		"invoices": invoices,
		"total_due": total_due,
		"total_overdue": total_overdue,
		"not_due": total_due - total_overdue,
		"buckets": buckets,
		"currency": currency,
		"frappe": frappe,
	}
	html = frappe.render_template("kerp/kerp/print_format/party_statement___knpl/party_statement.html", context)
	return get_pdf(html)


def _get_reminder_recipients(customer, invoices):
	"""Everyone who should get the reminder: the customer's primary contact,
	its billing contact, and whoever was the named contact on each invoice
	being reminded about (covers customers where different invoices/branches
	route to different people, not just one designated contact)."""
	emails = set()

	Contact = frappe.qb.DocType("Contact")
	DynamicLink = frappe.qb.DocType("Dynamic Link")

	contact_rows = (
		frappe.qb.from_(Contact)
		.inner_join(DynamicLink)
		.on((DynamicLink.parent == Contact.name) & (DynamicLink.parenttype == "Contact"))
		.select(Contact.email_id)
		.where(DynamicLink.link_doctype == "Customer")
		.where(DynamicLink.link_name == customer)
		# same as the original coalesce(email_id, '') != '' — excludes both
		# NULL and empty-string emails
		.where(Contact.email_id.isnotnull())
		.where(Contact.email_id != "")
		.where((Contact.is_primary_contact == 1) | (Contact.is_billing_contact == 1))
	).run(as_dict=True)
	emails.update(row.email_id for row in contact_rows)

	emails.update(inv["contact_email"] for inv in invoices if inv.get("contact_email"))

	return sorted(emails)


def _get_thread_message_id(customer, report_date):
	"""One deterministic Message-ID per customer per calendar month, so every
	reminder sent that month threads together instead of landing as N separate
	unrelated emails.

	frappe.sendmail's own `communication` linking only works against an
	*existing* Communication record — plain sendmail() calls don't create one
	on their own — so we look one up (and create it, the first time) by this
	same deterministic id ourselves.

	Returns (message_id, in_reply_to):
	  - no Communication for this customer+month yet: (new root id, None) —
	    caller should pass message_id=<that id> to sendmail and log a
	    Communication with it so later sends this month can find it.
	  - one already exists: (None, <that Communication's name>) — caller
	    should pass in_reply_to=<name> instead, and let sendmail generate a
	    fresh Message-ID for this send as normal.
	"""
	customer_code = frappe.get_cached_value("Customer", customer, "customer_code_kerp") or customer
	# RFC 5322 Message-IDs are id-left@id-right — the @domain isn't optional.
	# frappe.local.site matches what Frappe's own auto-generated IDs use
	# (see email_body.get_message_id -> email.utils.make_msgid(domain=...))
	root_message_id = f"{customer_code}-outstandings-{report_date.strftime('%m%Y')}@{frappe.local.site}"

	existing = frappe.db.get_value("Communication", {"message_id": root_message_id}, "name")
	if existing:
		return None, existing
	return root_message_id, None


def _due_soon_section_html(due_soon_invoices, currency):
	"""Single table for everything due soon — each row tagged 'Due Today' /
	'Due in N Days' — followed by a running Total Due Soon."""
	if not due_soon_invoices:
		return ""

	def due_in_label(days):
		return "Due Today" if days == 0 else f"Due in {days} Days"

	rows = "".join(f"""
		<tr>
			<td style="padding:6px 10px;border-bottom:1px solid #E3E8EF;word-break:break-word;overflow-wrap:break-word;word-wrap:break-word;">{inv['name']}</td>
			<td style="padding:6px 10px;border-bottom:1px solid #E3E8EF;word-break:break-word;overflow-wrap:break-word;word-wrap:break-word;">{frappe.utils.formatdate(inv['posting_date'])}</td>
			<td style="padding:6px 10px;border-bottom:1px solid #E3E8EF;word-break:break-word;overflow-wrap:break-word;word-wrap:break-word;">{frappe.utils.formatdate(inv['due_date'])}</td>
			<td style="padding:6px 10px;border-bottom:1px solid #E3E8EF;word-break:break-word;overflow-wrap:break-word;word-wrap:break-word;text-align:center;">{due_in_label(inv['days_until_due'])}</td>
			<td style="padding:6px 10px;border-bottom:1px solid #E3E8EF;word-break:break-word;overflow-wrap:break-word;word-wrap:break-word;text-align:right;">{fmt_money(inv['outstanding'], currency=currency)}</td>
		</tr>
	""" for inv in due_soon_invoices)

	total_due_soon = sum(flt(inv["outstanding"]) for inv in due_soon_invoices)

	return f"""
		<hr style="border:none;border-top:2px solid #8F9CB2;margin:20px 0;">
		<div style="margin-top:6px;">
			<p style="font-weight:700;color:#1F3864;font-size:18px;margin-bottom:8px;">Upcoming Due Invoices</p>
			<table style="width:100%;border-collapse:collapse;margin-bottom:4px;">
				<thead>
					<tr style="background:#F2F5FA;color:#1F3864;">
						<th style="padding:6px 10px;text-align:left;">Invoice No.</th>
						<th style="padding:6px 10px;text-align:left;">Invoice Date</th>
						<th style="padding:6px 10px;text-align:left;">Due Date</th>
						<th style="padding:6px 10px;text-align:center;">Due In</th>
						<th style="padding:6px 10px;text-align:right;">Amount</th>
					</tr>
				</thead>
				<tbody>{rows}</tbody>
			</table>
			<p style="font-size:14px;"><b>Total Due Soon: {fmt_money(total_due_soon, currency=currency)}</b></p>
		</div>
	"""


def _build_overdue_email_body(
	company, customer_name, invoices, total_due, total_overdue, currency, report_date, only_overdue,
	due_soon_invoices=None, has_attachment=False,
):
	# Inline styles only — most email clients (Outlook, Gmail) strip <style>
	# blocks from message bodies, so anything in a <head> block (like the
	# print format's CSS) would silently not render here.
	status_cell = "" if only_overdue else """
			<td style="padding:6px 10px;border-bottom:1px solid #E3E8EF;word-break:break-word;overflow-wrap:break-word;word-wrap:break-word;text-align:center;">{status}</td>"""

	def row_html(inv):
		# only redden overdue-days/amount for rows that are actually overdue —
		# in the "all invoices" mode not every row qualifies
		flag_color = "#9C0006" if inv["is_overdue"] else "#1a1a1a"
		return f"""
			<tr>
				<td style="padding:6px 10px;border-bottom:1px solid #E3E8EF;word-break:break-word;overflow-wrap:break-word;word-wrap:break-word;">{inv['name']}</td>
				<td style="padding:6px 10px;border-bottom:1px solid #E3E8EF;word-break:break-word;overflow-wrap:break-word;word-wrap:break-word;">{frappe.utils.formatdate(inv['posting_date'])}</td>
				<td style="padding:6px 10px;border-bottom:1px solid #E3E8EF;word-break:break-word;overflow-wrap:break-word;word-wrap:break-word;">{frappe.utils.formatdate(inv['due_date']) if inv['due_date'] else '-'}</td>
				<td style="padding:6px 10px;border-bottom:1px solid #E3E8EF;word-break:break-word;overflow-wrap:break-word;word-wrap:break-word;text-align:center;color:{flag_color};font-weight:600;">{inv['overdue_days'] or '-'}</td>
				<td style="padding:6px 10px;border-bottom:1px solid #E3E8EF;word-break:break-word;overflow-wrap:break-word;word-wrap:break-word;text-align:right;color:{flag_color};font-weight:600;">{fmt_money(inv['outstanding'], currency=currency)}</td>
				{status_cell.format(status="Overdue" if inv["is_overdue"] else "Not Due")}
			</tr>
		"""

	due_soon_invoices = due_soon_invoices or []
	has_overdue = bool(invoices)

	rows_html = "".join(row_html(inv) for inv in invoices)
	overdue_table_html = f"""
		<table style="width:100%;border-collapse:collapse;margin:14px 0;">
			<thead>
				<tr style="background:#1F3864;color:#ffffff;">
					<th style="padding:6px 10px;text-align:left;">Invoice No.</th>
					<th style="padding:6px 10px;text-align:left;">Invoice Date</th>
					<th style="padding:6px 10px;text-align:left;">Due Date</th>
					<th style="padding:6px 10px;text-align:center;">Overdue Days</th>
					<th style="padding:6px 10px;text-align:right;">Amount</th>
					{"" if only_overdue else '<th style="padding:6px 10px;text-align:center;">Status</th>'}
				</tr>
			</thead>
			<tbody>
				{rows_html}
			</tbody>
		</table>
	""" if has_overdue else ""

	if only_overdue and not has_overdue:
		# nothing overdue this cycle — this email exists purely for the due-soon heads-up
		intro = (
			f"You have no overdue invoices with {company} at present. As a heads-up, the "
			f"following invoice(s) will fall due soon, as on {frappe.utils.formatdate(report_date)}:"
		)
	elif only_overdue:
		intro = (
			f"Our records show the following invoice(s) from {company} are now overdue for payment, "
			f"as on {frappe.utils.formatdate(report_date)}:"
		)
	else:
		intro = (
			f"Please find below a complete summary of your outstanding invoices with {company}, "
			f"as on {frappe.utils.formatdate(report_date)}:"
		)

	totals_html = ""
	if has_overdue:
		totals_html = (
			f'<p style="font-size:14px;"><b>Total Overdue: '
			f'<span style="color:#9C0006;">{fmt_money(total_overdue, currency=currency)}</span></b></p>'
			if only_overdue
			else (
				f'<p style="font-size:14px;"><b>Total Due: {fmt_money(total_due, currency=currency)}</b>'
				+ (
					f' (of which <b><span style="color:#9C0006;">{fmt_money(total_overdue, currency=currency)}'
					f'</span></b> is overdue)'
					if total_overdue
					else ""
				)
				+ "</p>"
			)
		)

	due_soon_html = _due_soon_section_html(due_soon_invoices, currency) if only_overdue else ""

	closing = (
		"If payment has already been made, please disregard this notice and share the payment "
		"reference with us for our records. For any questions about this statement, please reach "
		"out to our accounts team — we're happy to help."
		if only_overdue
		else "If you have any questions about this statement or notice a discrepancy, please reach "
		"out to our accounts team — we're happy to help."
	)

	attachment_note = "A detailed statement is attached for your reference. " if has_attachment else ""

	return f"""
		<div style="font-family:Arial,sans-serif;font-size:13px;color:#1a1a1a;">
			<p>Dear {customer_name},</p>
			<p>{intro}</p>
			{overdue_table_html}
			{totals_html}
			{due_soon_html}
			<p>{attachment_note}{closing}</p>
			<p>Warm regards,<br>{company}<br>Accounts Team</p>
		</div>
	"""


@frappe.whitelist()
def get_statement_pdf(customer, company=None, report_date=None):
	company = company or frappe.defaults.get_user_default("Company")
	report_date = getdate(report_date or nowdate())
	currency = frappe.get_cached_value("Company", company, "default_currency")

	invoices, total_due, total_overdue, buckets = _get_invoice_rows(customer, company, report_date)
	pdf = _render_statement_pdf(
		company, customer, report_date, invoices, total_due, total_overdue, buckets, currency
	)

	# stream straight to the browser instead of saving a permanent File record
	# on every click — nothing left behind to clean up afterwards
	frappe.local.response.filename = f"Statement-{customer}-{report_date}.pdf"
	frappe.local.response.filecontent = pdf
	frappe.local.response.type = "pdf"
	frappe.response["display_content_as"] = "inline"


@frappe.whitelist()
def send_overdue_reminder(customer, company=None, report_date=None, only_overdue=1):
	"""Email one customer their invoices — table in the email body, plus the
	same statement PDF. only_overdue=1 (default): overdue invoices only, for
	payment-reminder use. only_overdue=0: every outstanding invoice for that
	customer, overdue or not — same idea, just the full statement instead."""
	if not get_settings().outstanding_reminder_enabled:
		frappe.throw(_("Overdue reminders are disabled in KERP Accounts Settings."))

	company = company or frappe.defaults.get_user_default("Company")
	report_date = getdate(report_date or nowdate())
	currency = frappe.get_cached_value("Company", company, "default_currency")
	only_overdue = bool(cint(only_overdue))

	invoices, total_due, total_overdue, _buckets = _get_invoice_rows(
		customer, company, report_date, overdue_only=only_overdue
	)
	# due-soon is a bonus heads-up on top of the overdue reminder cadence only —
	# the full-statement mode already lists every invoice, overdue or not
	due_soon_invoices = _get_due_soon_invoices(customer, company, report_date) if only_overdue else []

	if not invoices and not due_soon_invoices:
		message = (
			_("{0} has no overdue or upcoming-due invoices as on {1}")
			if only_overdue
			else _("{0} has no outstanding invoices as on {1}")
		)
		frappe.throw(message.format(customer, frappe.utils.formatdate(report_date)))

	emails = _get_reminder_recipients(customer, invoices + due_soon_invoices)
	if not emails:
		frappe.throw(
			_(
				"No email address found for {0} — checked the primary contact, billing contact, "
				"and each invoice's contact. Add an email on a Contact linked to this Customer."
			).format(customer)
		)

	customer_name = frappe.get_cached_value("Customer", customer, "customer_name") or customer

	# the attachment is always the same full statement get_statement_pdf would
	# produce for this customer/date — independent of only_overdue, which only
	# controls what the email body talks about (overdue-only vs everything)
	pdf_invoices, pdf_total_due, pdf_total_overdue, pdf_buckets = _get_invoice_rows(
		customer, company, report_date
	)
	attachments = []
	if pdf_invoices:
		pdf = _render_statement_pdf(
			company, customer, report_date, pdf_invoices, pdf_total_due, pdf_total_overdue, pdf_buckets, currency
		)
		attachments.append({"fname": f"Statement-{customer}-{report_date}.pdf", "fcontent": pdf})

	message = _build_overdue_email_body(
		company, customer_name, invoices, total_due, total_overdue, currency, report_date, only_overdue,
		due_soon_invoices=due_soon_invoices, has_attachment=bool(pdf_invoices),
	)

	# Byte-identical for every send to this customer within the same month —
	# some clients (Gmail in particular) also group conversations by subject
	# match, not just In-Reply-To/References, so a subject that varies with
	# the invoice count (which changes as invoices get paid through the
	# month) would risk splitting the thread even with correct headers. The
	# per-send detail (counts, due-soon breakdown) lives in the body instead.
	month_label = report_date.strftime("%B %Y")
	subject = (
		_("Payment Reminder - {0} | {1}").format(month_label, company)
		if only_overdue
		else _("Statement of Account - {0} | {1}").format(month_label, company)
	)

	new_message_id, in_reply_to = _get_thread_message_id(customer, report_date)

	frappe.sendmail(
		sender=_get_sender_email(),
		recipients=emails,
		cc=_get_cc_emails(invoices + due_soon_invoices),
		subject=subject,
		message=message,
		attachments=attachments,
		reference_doctype="Customer",
		reference_name=customer,
		message_id=new_message_id,
		in_reply_to=in_reply_to,
	)

	if new_message_id:
		# first reminder this customer+month — logged standalone (no
		# reference_doctype/reference_name) purely so later sends this same
		# month can find it via _get_thread_message_id and thread onto it
		frappe.get_doc({
			"doctype": "Communication",
			"communication_type": "Communication",
			"communication_medium": "Email",
			"sent_or_received": "Sent",
			"subject": subject,
			"content": message,
			"message_id": new_message_id,
			"recipients": ", ".join(emails),
		}).insert(ignore_permissions=True)

	return {
		"customer": customer,
		"emails": emails,
		"invoice_count": len(invoices),
		"due_soon_count": len(due_soon_invoices),
		"total_due": total_due,
		"total_overdue": total_overdue,
	}


@frappe.whitelist()
def send_overdue_reminders(company=None, report_date=None):
	"""Bulk wrapper: finds every customer with an overdue invoice, or one
	falling due within the configured due-soon window, and sends each a
	reminder via send_overdue_reminder. One customer's failure (no email,
	etc.) doesn't stop the rest of the run."""
	if not get_settings().outstanding_reminder_enabled:
		# checked once here rather than letting every customer hit the same
		# throw inside send_overdue_reminder and pile up N near-identical
		# entries in "skipped"
		return {"sent": [], "skipped": [], "message": _("Overdue reminders are disabled in KERP Accounts Settings.")}

	company = company or frappe.defaults.get_user_default("Company")
	report_date = getdate(report_date or nowdate())
	due_soon_before = add_days(report_date, _get_due_soon_window_days())

	# a due_date up to due_soon_before covers both "already overdue" (any date
	# before report_date) and "due soon" (report_date..due_soon_before) in one go
	SalesInvoice = frappe.qb.DocType("Sales Invoice")
	customers = (
		frappe.qb.from_(SalesInvoice)
		.select(SalesInvoice.customer)
		.distinct()
		.where(SalesInvoice.docstatus == 1)
		.where(SalesInvoice.company == company)
		.where(SalesInvoice.outstanding_amount != 0)
		.where(SalesInvoice.posting_date <= report_date)
		.where(SalesInvoice.due_date.isnotnull())
		.where(SalesInvoice.due_date <= due_soon_before)
	).run(pluck=True)

	sent, skipped = [], []
	for customer in customers:
		try:
			sent.append(send_overdue_reminder(customer, company, report_date))
		except Exception:
			skipped.append({"customer": customer, "reason": frappe.get_traceback()})
			frappe.log_error(title="Overdue reminder failed", message=frappe.get_traceback())

	return {"sent": sent, "skipped": skipped}
