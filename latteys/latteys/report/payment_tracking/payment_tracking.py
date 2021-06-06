# Copyright (c) 2013, Tech Station and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import msgprint, _
import frappe

def execute(filters=None):
	conditions, filters = get_conditions(filters)
	columns = get_column()
	data = get_data(conditions,filters)
	return columns,data

def get_column():
	return [_("Name") + ":Link/Payment Entry:140",
		_("Date") + ":Date:80",
		_("Bank Account") + ":Link/Bank Account:200",
		_("Mode of Payment") + ":Link/Mode of Payment:200",
		_("Company") + ":Link/Company:300",
		_("Party Type") + ":Data:120",
		_("Party") + ":Data:200",
		_("Paid Amount") + ":Currency:180",
		_("Received Amount") + ":Currency:180"]

def get_data(conditions,filters):
	pe = frappe.db.sql("""select name as "name1" ,posting_date,bank_account,mode_of_payment,company,party_type,party_name,
			(select paid_amount from `tabPayment Entry` where name = name1 and payment_type = "Pay"),
			(select paid_amount from `tabPayment Entry` where name = name1 and payment_type = "Receive")
				from `tabPayment Entry` where docstatus = 1 %s
				order by posting_date asc;"""%conditions, filters, as_list=1)
	return pe

def get_conditions(filters):
	conditions = ""
	if filters.get("company"): conditions += " and company = %(company)s"
	if filters.get("bank_account"): conditions += " and bank_account = %(bank_account)s"

	return conditions, filters

