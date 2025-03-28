from erpnext.accounts.utils import get_fiscal_year


def before_insert(doc, method=None):
    fiscal_year = get_fiscal_year(doc.transaction_date)
    start_year = fiscal_year[1].strftime("%y")
    end_year = fiscal_year[2].strftime("%y")
    doc.naming_series = f"KNPL/{start_year}-{end_year}/PO-.###"
