# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "latteys"
app_title = "Latteys"
app_publisher = "B2Grow"
app_description = "Customisation"
app_icon = "icon manufacture-blue"
app_color = "grey"
app_email = "mail@b2grow.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/latteys/css/latteys.css"
# app_include_js = "/assets/latteys/js/latteys.js"

# include js, css files in header of web template
# web_include_css = "/assets/latteys/css/latteys.css"
# web_include_js = "/assets/latteys/js/latteys.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "latteys.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "latteys.install.before_install"
# after_install = "latteys.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "latteys.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
# 	"Stock Entry": {
 #		"on_submit": "latteys.latteys.doctype.replaced_qty.updateSE"
#	},
        "Sales Invoice": {
                "on_submit": "latteys.latteys.doctype.replaced_qty.insertPI"
        },
	"Event": {
                "validate": "latteys.latteys.doctype.auto_mail.sendMail"
        },
	"Purchase Order": {
                "on_submit": "latteys.latteys.doctype.replaced_qty.insertSO"
        },
	"Purchase Receipt": {
                "on_submit": "latteys.latteys.doctype.replaced_qty.insertDN"
        },
	"Customer": {
                "validate": "latteys.latteys.doctype.replaced_qty.createSupplier"
        },
	"Supplier": {
                "validate": "latteys.latteys.doctype.replaced_qty.createCustomer"
        },
	"Item Group": {
                "validate": "latteys.latteys.doctype.replaced_qty.createPIG"
        },
	"Purchase Invoice": {
                "on_submit": "latteys.latteys.doctype.replaced_qty.insertPrice",
        }
#,
#	"Project": {
#		"autoname": "latteys.latteys.doctype.replaced_qty.addPerm",
#               "validate": "latteys.latteys.doctype.replaced_qty.addPerm_validate"
#        }
}

"""scheduler_events = {
	"cron": {
		"*/5 * * * *":[
			"latteys.latteys.doctype.replaced_qty.updateSerialNO"
		]
	}

}"""

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"latteys.tasks.all"
# 	],
# 	"daily": [
# 		"latteys.tasks.daily"
# 	],
# 	"hourly": [
# 		"latteys.tasks.hourly"
# 	],
# 	"weekly": [
# 		"latteys.tasks.weekly"
# 	]
# 	"monthly": [
# 		"latteys.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "latteys.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "latteys.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "latteys.task.get_dashboard_data"
# }
