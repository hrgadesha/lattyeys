# Copyright (c) 2013, B2Grow and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _

def execute(filters=None):
        conditions, filters = get_conditions(filters)
        columns = get_column()
        data = get_data(conditions,filters)
        return columns,data

def get_column():
        return [_("Company") + ":Link/Company:300",
		_("Date") + ":Date:130",
                _("Type") + ":Data:80",
		_("Party") + ":Data:170",
                _("Account") + ":Link/Account:140",
		_("Debit") + ":Currency:140",
		_("Credit") + ":Currency:140",
		_("Balance") + ":Currency:140"]

def get_data(conditions,filters):
        ledger = frappe.db.sql("""select company,posting_date,party_type,party,
    			account, sum(debit_in_account_currency), sum(credit_in_account_currency),
			(sum(debit_in_account_currency) - sum(credit_in_account_currency))
			from `tabGL Entry` where (is_cancelled = 0 or is_cancelled = "") and party != "" %s
			order by posting_date, party;"""%conditions, filters, as_list=1)
        return ledger

def get_conditions(filters):
	conditions = ""
	if filters.get("company") and filters.get("group_by_company") and filters.get("group_by_party"):
		conditions += "and company = %(company)s group by company,party,party_type"

	if filters.get("company") and filters.get("group_by_company") and not filters.get("group_by_party"):
		conditions += "and company = %(company)s group by company,party_type"

	if filters.get("company") and not filters.get("group_by_company") and filters.get("group_by_party"):
		conditions += "and company = %(company)s group by party,party_type"

	if filters.get("company") and not filters.get("group_by_company") and not filters.get("group_by_party"):
		conditions += "and company = %(company)s group by company,party_type"

	if not filters.get("company") and filters.get("group_by_company") and filters.get("group_by_party"):
		conditions += "group by company,party,party_type"

	if not filters.get("company") and not filters.get("group_by_company") and filters.get("group_by_party"):
		conditions += "group by party,party_type"

	if not filters.get("company") and filters.get("group_by_company") and not filters.get("group_by_party"):
		conditions += "group by company,party_type"

	if not filters.get("company") and not filters.get("group_by_company") and not filters.get("group_by_party"):
		conditions += "and docstatus = 1"

	return conditions, filters
