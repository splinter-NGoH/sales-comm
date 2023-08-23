from __future__ import unicode_literals
from frappe import _
import frappe


def get_data():
	return [
		{
			"label": _("Sales Person Targets"),
			"icon": "fa fa-table",
			"items": [
       
				{
					"type": "doctype",
					"label": _("Commission Settings"),
					"name": "Commission Settings",
					"description": _("Commission Settings")
				},
       
				{
					"type": "doctype",
					"label": _("Sales Person Targets"),
					"name": "Sales Person Targets",
					"description": _("Sales Person Targets")
				},
				{
					"type": "doctype",
					"label": _("Sales Person"),
					"name": "Sales Person",
					"description": _("Sales Person")
				},
				{
					"type": "doctype",
					"label": _("Payroll Period"),
					"name": "Payroll Period",
					"description": _("Payroll Period")
				},
				{
					"type": "doctype",
					"label": _("Additional Salary"),
					"name": "Additional Salary",
					"description": _("Additional Salary")
				},
    

			]
		}, 
        {
            "label": _("Reports"),
            "icon": "fa fa-table",
            "items" : [

                    {
                        "type": "report",
                        "doctype":"Sales Invoice",
                        "is_query_report":1,
                        "label": _("Sales Team Target Report"),
                        "name": "Sales Team Target",
                        "description": _("Sales Team Target Report")
                    },
            ]
        }
	]