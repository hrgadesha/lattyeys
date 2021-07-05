from __future__ import unicode_literals
import frappe
import datetime
from datetime import datetime, timedelta
from datetime import date
from frappe import msgprint
from frappe.utils.file_manager import save_url, save_file, get_file_name, remove_all, remove_file
import json
from frappe.model.document import Document

@frappe.whitelist(allow_guest=True)
def updateSE(doc,method):
	if doc.stock_entry_type == "Receive From Job work" and doc.recieve_against_job_work:
		for d in doc.items:
			sv = frappe.get_doc("Stock Entry Detail",d.job_work_id)
			sv.sent_qty += d.qty
			sv.save()

@frappe.whitelist(allow_guest=True)
def cancelSE(doc,method):
        if doc.stock_entry_type == "Receive From Job work" and doc.recieve_against_job_work:
                for d in doc.items:
                        sv = frappe.get_doc("Stock Entry Detail",d.job_work_id)
                        sv.sent_qty -= d.qty
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
			"subject": d.task_type +" - "+ d.reference_type +" - "+ d.reference_name,
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

@frappe.whitelist()
def insertSO(doc,method):
	if doc.is_branch_transfer:
		warehouse = frappe.db.sql("""select name from `tabWarehouse` where company = '{0}' and warehouse_name LIKE '%Fresh%'
				;""".format(doc.supplier),as_list=1)

		items = []
		for i in doc.items:
			item_li = {
				"item_code": i.item_code,
				"item_name": i.item_name,
				"description": i.item_name,
				"delivery_size": i.delivery_size,
				"cable_size": i.cable_size,
				"cable_length": i.cable_length,
				"voltage_range": i.voltage_range,
				"connection_type": i.connection_type,
				"qty": i.qty,
				"uom": i.uom,
				"rate": i.rate,
				"item_tax_template":i.item_tax_template.replace(doc.branch,doc.abbr)}
			items.append(item_li)
		taxes = []
		for d in doc.taxes:
			tax_li = {"charge_type": d.charge_type,"description":d.account_head.replace(doc.branch,doc.abbr),"rate": d.rate,"tax_amount": d.tax_amount,"account_head":d.account_head.replace(doc.branch,doc.abbr),"cost_center":d.cost_center.replace(doc.branch,doc.abbr)}
			taxes.append(tax_li)

		sales_order = frappe.get_doc({
		"doctype": "Sales Order",
		"customer": doc.company,
		"company": doc.supplier,
		"branch": doc.abbr,
		"set_warehouse": warehouse[0][0],
		"transaction_date": doc.transaction_date,
		"inter_company_order_reference": doc.name,
		"delivery_date": doc.schedule_date,
		"tax_category" : doc.tax_category.replace(doc.branch,doc.abbr),
		"items": items,
		"taxes": taxes
		})
		sales_order.insert(ignore_permissions=True,ignore_mandatory = True)
		sales_order.save()
		frappe.msgprint("Inter Company Sales Order Genrated")


@frappe.whitelist()
def insertPI(doc,method):
	if doc.is_branch_transfer:
		warehouse = frappe.db.sql("""select name from `tabWarehouse` where company = '{0}' and warehouse_name LIKE '%Fresh%'
				;""".format(doc.customer),as_list=1)

		items = []
		for i in doc.items:
			item_li = {"item_code": i.item_code,"item_name": i.item_name,"description": i.item_name,"qty": i.qty,"uom": i.uom,"rate": i.rate,"item_tax_template":i.item_tax_template.replace(doc.branch,doc.abbr),"serial_no":i.serial_no,"cost_center": frappe.db.get_value('Company', {'name': doc.customer}, ['cost_center']),}
			items.append(item_li)
		taxes = []
		for d in doc.taxes:
			tax_li = {"charge_type": d.charge_type,"description":d.account_head.replace(doc.branch,doc.abbr),"rate": d.rate,"tax_amount": d.tax_amount,"account_head":d.account_head.replace(doc.branch,doc.abbr),"cost_center":d.cost_center.replace(doc.branch,doc.abbr)}
			taxes.append(tax_li)

		purchase_invoice = frappe.get_doc({
		"doctype": "Purchase Invoice",
		"supplier": doc.company,
		"company": doc.customer,
		"branch": doc.abbr,
		"update_stock": doc.update_stock,
		"set_warehouse": warehouse[0][0],
		"posting_date": doc.posting_date,
		"inter_company_invoice_reference": doc.name,
		"due_date": doc.due_date,
		"tax_category" : doc.tax_category.replace(doc.branch,doc.abbr),
		"cost_center": frappe.db.get_value('Company', {'name': doc.customer}, ['cost_center']),
		"items": items,
		"taxes": taxes
		})
		purchase_invoice.insert(ignore_permissions=True,ignore_mandatory = True)
		purchase_invoice.save()
		frappe.msgprint("Inter Company Purchase Invoice Genrated")


@frappe.whitelist(allow_guest=True)
def createSupplier(doc,method):
	if doc.has_double_ledger and not frappe.db.exists("Supplier", doc.customer_name):
		spl = frappe.get_doc({
		"doctype": "Supplier",
		"supplier_name": doc.customer_name,
		"supplier_group": doc.supplier_group,
		"branch": doc.branch,
		"territory": doc.territory
		})
		spl.insert(ignore_mandatory = True,ignore_permissions=True)

		dbl = frappe.get_doc({
		"doctype": "Double Ledger Parties",
		"primary_role": "Customer",
		"customer": doc.customer_name,
		"supplier": doc.customer_name
		})
		dbl.insert(ignore_mandatory = True,ignore_permissions=True)
		frappe.msgprint("Double Ledger Party Created")


@frappe.whitelist(allow_guest=True)
def createCustomer(doc,method):
	if doc.has_double_ledger and not frappe.db.exists("Customer", doc.supplier_name):
		cus = frappe.get_doc({
		"doctype": "Customer",
		"customer_name": doc.supplier_name,
		"customer_group": doc.customer_group,
		"branch": doc.branch,
		"territory": doc.territory
		})
		cus.insert(ignore_mandatory = True,ignore_permissions=True)

		dbl = frappe.get_doc({
		"doctype": "Double Ledger Parties",
		"primary_role": "Supplier",
		"customer": doc.supplier_name,
		"supplier": doc.supplier_name
		})
		dbl.insert(ignore_mandatory = True,ignore_permissions=True)
		frappe.msgprint("Double Ledger Party Created")


@frappe.whitelist()
def insertDN(doc,method):
	if doc.is_replacement:
		warehouse = frappe.db.sql("""select name from `tabWarehouse` where company = '{0}' and warehouse_name LIKE '%Fresh%'
				;""".format(doc.company),as_list=1)

		items = []
		for i in doc.items:
			item_li = {"item_code": i.item_code,"item_name": i.item_name,"description": i.item_name,"qty": i.qty,"uom": i.uom,"rate": i.rate,"item_tax_template":i.item_tax_template,"return_serial_no":i.serial_no}
			items.append(item_li)
		taxes = []
#		for d in doc.taxes:
#			tax_li = {"charge_type": d.charge_type,"description":d.account_head.replace(doc.branch,doc.abbr),"rate": d.rate,"tax_amount": d.tax_amount,"account_head":d.account_head.replace(doc.branch,doc.abbr),"cost_center":d.cost_center.replace(doc.branch,doc.abbr)}
#			taxes.append(tax_li)

		delivery_note = frappe.get_doc({
		"doctype": "Delivery Note",
		"branch": doc.branch,
		"company": doc.company,
		"customer": doc.supplier,
		"set_warehouse": warehouse[0][0],
		"posting_date": doc.posting_date,
		"replacement_against": doc.name,
		"tax_category" : doc.tax_category,
		"items": items,
		"taxes": doc.taxes
		})
		delivery_note.insert(ignore_permissions=True,ignore_mandatory = True)
		delivery_note.save()
		frappe.msgprint("Delivery Note Created For Replacement")


@frappe.whitelist()
def insertPrice(self,method):
	for d in self.items:
		item_price = frappe.db.sql("""select name from `tabItem Price` where item_code = %s and price_list = %s 
		and valid_from = %s;""",(d.item_code,self.buying_price_list,self.posting_date))
		if item_price:
			ip = frappe.get_doc("Item Price",item_price[0][0])
			ip.price_list_rate = d.rate
			ip.save()

		if not item_price:
			doc = frappe.get_doc(dict(
			doctype = "Item Price",
			item_code = d.item_code,
			buying = 1,
			price_list = self.buying_price_list,
			price_list_rate = d.rate,
			valid_from = self.posting_date
			)).insert(ignore_permissions = True,ignore_mandatory = True)
			doc.save()

@frappe.whitelist(allow_guest=True)
def createPIG(doc,method):
	if not frappe.db.exists('Parent Item Group', doc.name) and doc.is_group == 1:
		cus = frappe.get_doc({
		"doctype": "Parent Item Group",
		"parent_item_group": doc.item_group_name
		})
		cus.insert(ignore_mandatory = True,ignore_permissions=True)

@frappe.whitelist(allow_guest=True)
def getContact(supplier):
	data = frappe.db.sql("""select c.mobile_no,c.email_id from `tabContact` c, 
				`tabDynamic Link` dl
				where c.name = dl.parent and dl.link_name = %s;""",(supplier),as_list=1)
	return data


@frappe.whitelist()
def getCustomerItemCode(item,customer):
	customer_item_code = frappe.db.sql("""select ref_code from `tabItem Customer Detail` where parent = %s 
		and customer_name = %s;""",(item,customer),as_list = True)
	if customer_item_code:
		return customer_item_code
	else:
		""

@frappe.whitelist()
def getDepartment(user):
	department = frappe.db.sql("""select department from `tabEmployee` where prefered_email = %s;""",(user),as_list = True)
	if department:
		return department
	else:
		""

@frappe.whitelist()
def getJOBcheck(wo):
	jc = frappe.db.sql("""select IF((SELECT count(name) from `tabJob Card` where docstatus = 0 and 
		work_order = %s),1,0);""",(wo),as_list = True)
	return jc


@frappe.whitelist()
def getStock(warehouse,item):
	stock = frappe.db.sql("""select projected_qty,actual_qty from `tabBin` where warehouse = %s 
		and item_code = %s;""",(warehouse,item),as_list = True)
	if stock:
		return stock
	else:
		0


@frappe.whitelist()
def createPurchaseMR(wo):
	worder = frappe.get_doc('Work Order', wo)
	items = []
	for d in worder.required_items:
		purchase = frappe.get_doc('Item', d.item_code)
		if purchase.is_only_purchase_for_manufacturing == 1:
			if d.required_qty > frappe.db.get_value("Bin", filters={'item_code':d.item_code,'warehouse':d.source_warehouse},fieldname=['projected_qty']):
				item_li = {"item_code": d.item_code,"qty": d.required_qty - frappe.db.get_value("Bin", filters={'item_code':d.item_code,'warehouse':d.source_warehouse},fieldname=['projected_qty']),"warehouse": d.source_warehouse,"schedule_date": datetime.today() + timedelta(days=1)}
				items.append(item_li)
	if items:
		mr = frappe.get_doc({
		"doctype": "Material Request",
		"company": worder.company,
		"set_warehouse": worder.source_warehouse,
		"type": "Purchase",
		"priority": "High",
		"material_request_type": "Purchase",
		"schedule_date": worder.expected_delivery_date,
		"items": items
		})
		mr.insert(ignore_permissions=True)
		mr.save()
		msgprint("Material Request Generated (Purchase)")

	else:
		msgprint("No Items Found For Purchase Request")

@frappe.whitelist()
def createManufactureMR(wo):
	worder = frappe.get_doc('Work Order', wo)
	items = []
	for d in worder.required_items:
		purchase = frappe.get_doc('Item', d.item_code)
		if purchase.in_house_manufacturing == 1:
			if d.required_qty > frappe.db.get_value("Bin", filters={'item_code':d.item_code,'warehouse':d.source_warehouse},fieldname=['projected_qty']):
				item_li = {"item_code": d.item_code,"qty": d.required_qty - frappe.db.get_value("Bin", filters={'item_code':d.item_code,'warehouse':d.source_warehouse},fieldname=['projected_qty']),"warehouse": d.source_warehouse,"schedule_date": datetime.today() + timedelta(days=1)}
				items.append(item_li)
	if items:
		mr = frappe.get_doc({
		"doctype": "Material Request",
		"company": worder.company,
		"set_warehouse": worder.source_warehouse,
		"type": "Manufacture",
		"priority": "High",
		"material_request_type": "Manufacture",
		"schedule_date": worder.expected_delivery_date,
		"items": items
		})
		mr.insert(ignore_permissions=True)
		mr.save()
		msgprint("Material Request Generated (Manufacture)")

	else:
		msgprint("No Items Found For Manufacture Request")


@frappe.whitelist()
def getConversion(item,uom):
	conversion = frappe.db.sql("""select conversion_factor from `tabUOM Conversion Detail` where 
			parent = %s and uom = %s;""",(item,uom),as_list = True)
	return conversion if conversion else 0

@frappe.whitelist()
def getBankAccount(company,bank_account):
	bank_account = frappe.db.sql("""select account from `tabBank Account Mapping` where company = %s 
			and parent = %s;""",(company,bank_account),as_list = True)
	return bank_account if bank_account else ""


@frappe.whitelist()
def getDefaultSupplier(item):
	vendor = frappe.db.sql("""select default_supplier from `tabItem Default` where parent = %s;""",(item),as_list = True)
	return vendor if vendor else "NA"


@frappe.whitelist(allow_guest=True)
def getBinStock(item,warehouse):
	stock = frappe.db.sql("""select actual_qty from `tabBin` where item_code = %s and 
		warehouse = %s;""",(item,warehouse),as_list = True)
	return stock if stock else 0


@frappe.whitelist(allow_guest=True)
def updateWebContent_InItem(doc,method):
	if doc.show_in_website == 1:
		count_item = 0
		for d in frappe.db.get_list('Item',filters={"item_group": doc.name,'show_in_website': 1,"update_website_content_based_on_item_group":1,"update_website_label_dynamically":1},fields=['name']):
			count_item = count_item + 1
			item = frappe.get_doc("Item",d.name)
			item.web_long_description = doc.description
			item.web_content_description = doc.web_content_description
			item.website_content = doc.website_content
			item.default_material_request_type = doc.default_material_request_type
			item.save()
		frappe.msgprint(str(count_item) + " Item Updated")


@frappe.whitelist(allow_guest=True)
def updateMRtype_InItem(doc,method):
	count_item = 0
	for d in frappe.db.get_list('Item',filters={"item_group": doc.name},fields=['name']):
		count_item = count_item + 1
		item = frappe.get_doc("Item",d.name)
		item.default_material_request_type = doc.default_material_request_type
		item.save()
	frappe.msgprint(str(count_item) + " Item Updated")
