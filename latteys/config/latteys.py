from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
                        "label": _("Masters"),
                        "items": [
                                {
                                        "type": "doctype",
                                        "name": "Discount Type",
                                        "label": "Discount Type",
                                        "description": _("Discount Type"),
                                        "onboard": 1
                                },
                                {
                                        "type": "doctype",
                                        "name": "Product Sold By Customer",
                                        "label": "Product Sold By Customer",
                                        "description": _("Product Sold By Customer"),
                                        "onboard": 1
                                },
				{
                                        "type": "doctype",
                                        "name": "Competitor Company",
                                        "label": "Competitor Company",
                                        "description": _("Competitor Company"),
                                        "onboard": 1
                                }
                        ]
                },
		{
                        "label": _("Accounts Reports"),
                        "items": [
                                {
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "Branch Wise Accounts Receivable Summary",
					"doctype": "Sales Invoice"
                                },
                                {
                                        "type": "report",
                                        "is_query_report": True,
					"name": "Branch Wise Accounts Receivable",
                                        "doctype": "Sales Invoice"
                                },
                                {
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "Branch Wise Sales Register",
					"doctype": "Sales Invoice"
                                }
                        ]
                },
		{
                        "label": _("Sales Reports"),
                        "items": [
                                {
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "Branch Wise Gross Profit",
					"doctype": "Sales Invoice"
                                },
                                {
                                        "type": "report",
                                        "is_query_report": True,
					"name": "Branch Wise Customer Credit Balance",
                                        "doctype": "Customer"
                                },
                                {
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "Branch Wise Customer Ledger Summary",
					"doctype": "Sales Invoice"
                                },
				{
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "Branch Wise Ordered Items To Be Billed",
                                        "doctype": "Sales Invoice"
                                },
				{
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "Branch Wise Ordered Items To Be Billed",
                                        "doctype": "Sales Invoice"
                                },
				{
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "Branch Wise Inactive Customers",
                                        "doctype": "Sales Order"
                                }
                        ]
                }
]
