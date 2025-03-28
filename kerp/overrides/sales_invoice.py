from erpnext.accounts.utils import get_fiscal_year


def before_insert(doc, method=None):
    fiscal_year = get_fiscal_year(doc.posting_date)
    start_year = fiscal_year[1].strftime("%y")
    end_year = fiscal_year[2].strftime("%y")
    if doc.is_return:
        doc.naming_series = f"KNPL/{start_year}-{end_year}/CN.##"
    elif doc.is_debit_note:
        doc.naming_series = f"KNPL/{start_year}-{end_year}/DN.##"
    else:
        doc.naming_series = f"KNPL/{start_year}-{end_year}/.###"
