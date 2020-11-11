from __future__ import unicode_literals
import frappe
from frappe import msgprint
from frappe.utils.file_manager import save_url, save_file, get_file_name, remove_all, remove_file
import json
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
			mt = frappe.get_doc({
			"doctype": "User Permission",
			"user": d.user,
			"allow": proj.doctype,
			"for_value": proj.project_name,
			"apply_to_all_doctypes": 1
			})
			mt.insert(ignore_mandatory = True,ignore_permissions=True)

@frappe.whitelist(allow_guest=True)
def createTask(name):
	proj = frappe.get_doc('Project', name)
	for d in proj.task_details:
		if not d.task_created and d.task:
			mt = frappe.get_doc({
			"doctype": "Task",
			"branch" : proj.branch,
			"subject": d.reference_name +" / "+ d.subject,
			"reference_type": d.reference_type,
			"reference_name": d.reference_name,
			"exp_start_date": d.start_date,
			"exp_end_date": d.end_date,
			"type": d.task_type,
			"employee": d.employee,
			"employee_name": d.employee_name,
			"assigned_to": d.user,
			"project": name,
			"department": proj.department
			})
			mt.insert(ignore_mandatory = True,ignore_permissions=True)


@frappe.whitelist()
def updateSerialNO():
	data = frappe.db.sql("""select name
				from `tabSerial No` where status = "Delivered" and delivered_warehouse is null;""",as_list=True)

	if data:
		for d in data:
			doc = frappe.get_doc("Serial No", d[0])
			doc.delivered_warehouse = "Delivered - LIL"
			doc.save(ignore_permissions=True)

@frappe.whitelist()
def attach_all_docs(document):
	"""This function attaches drawings to the purchase order based on the items being ordered"""
	document = json.loads(document)
	document2 = frappe._dict(document)

	current_attachments = []

	for file_url in frappe.db.sql("""select file_url from `tabFile` where attached_to_doctype = %(doctype)s and attached_to_name = %(docname)s""", {'doctype': document2.doctype, 'docname': document2.name}, as_dict=True ):
		current_attachments.append(file_url.file_url)

	# add the directly linked drawings
	items = []
	for item in document["items"]:
		#frappe.msgprint(str(item))
		if item["send_drawing"]:
			items.append(item["item_code"])

	count = 0
	for item_doc in items:
		#frappe.msgprint(item_doc)
		item = frappe.get_doc("Item",item_doc)

		attachments = []
		# Get the path for the attachments
		if item.drawing_attachment:
			attachments.append(item.drawing_attachment)

		for attach in attachments:
			# Check to see if this file is attached to the one we are looking for
			if not attach in current_attachments:
				count = count + 1
				myFile = save_url(attach, attach, document2.doctype, document2.name, "Home/Attachments",1)
				myFile.file_name = attach
				myFile.save()
				current_attachments.append(attach)
	frappe.msgprint("Attached {0} files".format(count))
