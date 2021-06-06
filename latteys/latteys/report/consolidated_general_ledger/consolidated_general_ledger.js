// Copyright (c) 2016, B2Grow and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Consolidated General Ledger"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company"
		},
		{
                        "fieldname": "group_by_company",
                        "label": __("Group By Company"),
                        "fieldtype": "Check",
			"default": 1,
			"read_only": 0
                },
		{
                        "fieldname": "group_by_party",
                        "label": __("Group By Party"),
                        "fieldtype": "Check",
                        "default": 1,
			"read_only": 0
                }
	]
};
