from __future__ import unicode_literals
import frappe
from datetime import datetime
from frappe.model.document import Document

@frappe.whitelist(allow_guest=True)
def sendMail(doc,method):
	if doc.send_email_on_event_creation:
		for d in doc.event_participants:
			if d.reference_doctype == "Employee":
				email = frappe.db.sql("""select prefered_email,employee_name from `tabEmployee` where name = %s;""",(d.reference_docname))
				if email:
					content = "<h4>Dear,</h4><p>"+email[0][1]+"</p><br><br><p>Event : "+str(doc.subject)+"</p><p>Start : "+str(doc.starts_on)+"</p><p>End : "+str(doc.ends_on)+"</p><p>Event Category : "+str(doc.event_category)+"</p><br><p><b>Description : </b><br>"+str(doc.description)+"</p>"
					frappe.sendmail(recipients=email[0][0],sender="notification@latteysindustries.com",subject="Invitation For Event", content=content)


			if d.reference_doctype == "Lead":
				email = frappe.db.sql("""select email_id,lead_name from `tabLead` where name = %s;""",(d.reference_docname))
				if email:
					content = "<h4>Dear,</h4><p>"+email[0][1]+"</p><br><br><p>Event : "+str(doc.subject)+"</p><p>Start : "+str(doc.starts_on)+"</p><p>End : "+str(doc.ends_on)+"</p><p>Event Category : "+str(doc.event_category)+"</p><br><p><b>Description : </b><br>"+str(doc.description)+"</p>"
					frappe.sendmail(recipients=email[0][0],sender="notification@latteysindustries.com",subject="Invitation For Event", content=content)
