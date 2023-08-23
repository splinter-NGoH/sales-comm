# -*- coding: utf-8 -*-
# Copyright (c) 2021, Peter Maged and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SalesPersonTargets(Document):
	def validate (self):
		if self.default :
			frappe.db.sql(f"""
					update `tabSales Person Targets` set `default` = 0 
     				where sales_person = '{self.sales_person}'
					and name <> '{self.name}'
					""")
			frappe.db.commit()
