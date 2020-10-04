from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

@frappe.whitelist(allow_guest=True)
def updateSE(doc,method):
	if doc.stock_entry_type == "Material Issue" and doc.replacement:
		for d in doc.items:
			sv = frappe.get_doc("Stock Entry Detail",d.replacement_request_id)
			sv.replaced_qty = d.qty
			sv.save()


@frappe.whitelist(allow_guest=True)
def transferStock(doc,method):
	if doc.is_branch_transfer:
		items = []
		for d in doc.items:
			items.append({"item_code": d.item_code,"qty": d.qty,"basic_rate": d.rate,"s_warehouse":doc.set_warehouse,"t_warehouse":"Branch Transfer - LIL","serial_no":d.serial_no})
		mt = frappe.get_doc({
		"doctype": "Stock Entry",
		"branch": doc.transfer_to_branch,
		"company": doc.company,
		"stock_entry_type": "In Transit",
		"posting_date": doc.posting_date,
		"from_warehouse": doc.set_warehouse,
		"to_warehouse": "Branch Transfer - LIL",
		"items": items
		})
		mt.insert(ignore_mandatory = True,ignore_permissions=True)
		mt.save(ignore_permissions=True)
		mt.submit()


	if doc.is_branch_transfer:
		items = []
		for d in doc.items:
			items.append({"item_code": d.item_code,"qty": d.qty,"basic_rate": d.rate,"s_warehouse":"Branch Transfer - LIL","t_warehouse":doc.transfer_stock_to,"serial_no":d.serial_no})
		mt = frappe.get_doc({
		"doctype": "Stock Entry",
		"branch": doc.transfer_to_branch,
		"sales_invoice_no": doc.name,
		"company": doc.company,
		"stock_entry_type": "Branch Transfer",
		"posting_date": doc.posting_date,
		"from_warehouse": "Branch Transfer - LIL",
		"to_warehouse": doc.transfer_stock_to,
		"items": items
		})
		mt.insert(ignore_mandatory = True,ignore_permissions=True)
		mt.save(ignore_permissions=True)


@frappe.whitelist(allow_guest=True)
def addPerm_validate(name):
	proj = frappe.get_doc('Project', name)
	for d in proj.users:
		if not d.permission_created:
#			d.permission_created = 1
			mt = frappe.get_doc({
			"doctype": "User Permission",
			"user": d.user,
			"allow": proj.doctype,
			"for_value": proj.project_name,
			"apply_to_all_doctypes": 1
			})
			mt.insert(ignore_mandatory = True,ignore_permissions=True)
