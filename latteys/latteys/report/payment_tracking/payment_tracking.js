// Copyright (c) 2016, B2Grow and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Payment Tracking"] = {
	"filters": [
		{
                    "fieldname": "company",
                    "label": __("Company"),
                    "fieldtype": "Link",
                    "options": "Company"
                },
		{
        	    "fieldname": "bank_account",
       		    "label": __("Bank Account"),
        	    "fieldtype": "Link",
		    "options": "Bank Account"
        	}
	]
};
