# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, scrub
from frappe.utils import flt, cint ,get_link_to_form
from six import iteritems
import json
def execute(filters=None):
	data,columns=[],[]
	columns = get_columns(filters)
	data = get_data(filters)
	return columns,data

def get_columns(filters):
    columns=[
		{
			"fieldname":"sales_person",
			"label":_("Sales Person"),
			"fieldtype":"Link",
			"options":"Sales Person",
			"width":150
		},
  		{
			"fieldname":"sales_person_name",
			"label":_("Sales Person"),
			"fieldtype":"Data",
			# "options":"Sales Person",
			"width":150
		},
  		{
			"fieldname":"employee",
			"label":_("Employee"),
			"fieldtype":"Link",
			"options":"Employee",
			"width":150
		},
		# {
		# 	"fieldname":"advance_amount",
		# 	"label":_("Invoices Advance"),
		# 	"fieldtype":"Float",
		# 	# "options":"Sales Person",
		# 	"width":150
		# },
		{
			"fieldname":"invoices_amount",
			"label":_("Invoices Amount"),
			"fieldtype":"Float",
			# "options":"Sales Person",
			"width":150
		},

  		{
			"fieldname":"paid_amount",
			"label":_("Invoices Paid Amount"),
			"fieldtype":"Float",
			# "options":"Sales Person",
			"width":250
		},
		
		{
			"fieldname":"outstanding_amount",
			"label":_("Invoices Outstanding Amount"),
			"fieldtype":"Float",
			# "options":"Sales Person",
			"width":250
		},
    ##########################################3
    
  		{
			"fieldname":"total_payments",
			"label":_("Total Payments"),
			"fieldtype":"Float",
			# "options":"Sales Person",
			"width":150
		},
		{
		
			"fieldname":"collect_percent",
			"label":_("Collect Percent"),
			"fieldtype":"Percent",
			# "options":"Sales Person",
			"width":150
		},
		
		{
			"fieldname":"target_rate",
			"label":_("Target Percent"),
			"fieldtype":"Percent",
			# "options":"Sales Person",
			"width":150
		},
    	{
			"fieldname":"required_target",
			"label":_("Required Target"),
			"fieldtype":"Float",
			# "options":"Sales Person",
			"width":150
		},
		{
			"fieldname":"commission_rate",
			"label":_("Commission Rate"),
			"fieldtype":"Percent",
			# "options":"Sales Person",
			"width":150
		},
  
		{
			"fieldname":"commission_amount",
			"label":_("Commission Amount"),
			"fieldtype":"Float",
			# "options":"Sales Person",
			"width":150
		},
		{
			"fieldname":"paid_commission",
			"label":_("Paid Commission"),
			"fieldtype":"Float",
			# "options":"Sales Person",
			"width":150
		},
		{
			"fieldname":"remaining_commission",
			"label":_("Remaining Commission"),
			"fieldtype":"Float",
			# "options":"Sales Person",
			"width":150
		},
		

	]
    return columns

def get_data(filters):
	data=[]
	conditions = "where 1 =1"
	company = filters.get("company")
	filter = filters.get("period")
	if filter:
		period = frappe.get_doc("Payroll Period" , filter)
		start_date ,end_date = period.start_date , period.end_date
		# conditions += f" and date(pe.due_date) between date('{period.start_date}') and date('{period.end_date}')"
		
		# filter = filters.get("company")
		# if filter:
		# 	conditions += f" and si.company = '{filter}'"
		# filter = filters.get("customer")
		# if filter:
		# 	conditions += f" and si.customer = '{filter}'"
		filter = filters.get("sales_person")
		if filter:
			conditions += f" and person.name = '{filter}'"
		
		
		sql = f"""
		select
		person.name as sales_person ,person.sales_person_name , person.employee,
		(
			select SUM(base_grand_total) from `tabSales Invoice` invoice inner join `tabSales Team` team on team.parent = invoice.name
			where invoice.docstatus = 1 and team.sales_person =  person.name and invoice.company = '{company}'
			and date(invoice.posting_date) between  date ('{start_date}') and  date ('{end_date}')
			) as 'invoices_amount',

		(
		select SUM(outstanding_amount) from `tabSales Invoice` invoice inner join 
  `tabSales Team` team on team.parent = invoice.name
			where invoice.docstatus = 1 and invoice.company = '{company}' and
   team.sales_person =  person.name 
   and date(invoice.posting_date) between  date ('{start_date}') and  date ('{end_date}')
			) as 'outstanding_amount' ,


		( select
				sum(credit)
			from
				`tabGL Entry`
			where
				voucher_type in ('Journal Entry', 'Payment Entry')
				and party_type ='Customer'
				and company = '{company}'
				and against_voucher_type = "Sales Invoice"
				and posting_date BETWEEN date ('{start_date}') and  date ('{end_date}')
				and against_voucher in (
						select invoice.name from `tabSales Invoice` invoice inner join `tabSales Team` team on team.parent = invoice.name
						where invoice.docstatus = 1 and team.sales_person = person.name)
		) as 'total_payments' ,

		 (
        select SUM(case when type ='Deduction' then (amount * -1) else amount end ) from `tabAdditional Salary` where docstatus < 2 and commission = 1
        and date(payroll_date)  between  date ('{start_date}') and  date ('{end_date}')
        and employee = person.employee
		and company = '{company}'
    ) as 'paid_commission'



		from `tabSales Person` person

		{conditions}
		"""
		# frappe.msgprint(sql)
		data = frappe.db.sql(sql,as_dict=1) or []
		if data :
			
			for row in data :
				row.target_rate = 0
				row.collect_percent = 0
				row.invoices_amount = row.invoices_amount or 0
				row.total_payments = row.total_payments or 0
				row.outstanding_amount = row.outstanding_amount or 0
				row.paid_commission = row.paid_commission or 0
				row.commission_rate,row.required_target,row.commission_amount = get_commission_rate (row.sales_person , period , row.invoices_amount , row.total_payments)
				row.paid_amount = row.invoices_amount - row.outstanding_amount
				row.remaining_commission = round(row.commission_amount - row.paid_commission)
				if row.required_target > 0 :
					row.target_rate = (row.invoices_amount / (row.required_target ))*100
				if row.invoices_amount > 0 :
					row.collect_percent = (row.total_payments / (row.invoices_amount ))*100
	return data



def get_commission_rate (person , period , total_invoices ,total_payments):
    
	rate,target,commission = 0,0 ,0
	target_doc = frappe.db.get_value ("Sales Person Targets" ,{"sales_person":person 
									, "payroll_period" : period.name},['name']) or\
             frappe.db.get_value ("Sales Person Targets" ,{"sales_person":person 
									, "default" : 1},['name'])
	if not target_doc :
		target_doc = frappe.db.get_value ("Sales Person Targets" ,{"sales_person":person 
									, "default" : 1},['name'])
	if target_doc :
		doc = frappe.get_doc("Sales Person Targets" , target_doc)
		target = doc.target
		rates = sorted(getattr(doc,'rates',[]), key=lambda d: d.target) or []
		row = None
		for i in rates :
			if total_invoices >= ((i.target * doc.target )/100) :
				row = i
			else :
				break 
		if row :
			rate = row.rate
	commission = rate * total_payments / 100
	return rate,target,commission







@frappe.whitelist()
def submit_additional_salaries (data,period) :
	period = frappe.get_doc("Payroll Period",period)
	component = frappe.db.get_single_value ("Commission Settings","salary_component") or None
	if not component :
		frappe.throw(_("Please set Salary Component in Commission Settings"))
	if not period :
		frappe.throw(_("Please set Payroll Period"))

	data = json.loads(data)
	if len(data)>1 :
		data.remove(data[-1])
	for i in data :
		row = frappe._dict(i)
		if row.employee and row.remaining_commission > 0:
			try:
				# frappe.msgprint(str(row.remaining_commission))
				doc = frappe.new_doc("Additional Salary")
				doc.employee = row.employee
				doc.commission = 1
				doc.amount = abs(row.remaining_commission)
				doc.type = "Deduction" if row.remaining_commission < 0 else "Earning"
				doc.payroll_date = period.end_date
				doc.salary_component = component
				doc.overwrite_salary_structure_amount=0
				doc.commission_rate = row.commission_rate
				doc.target = row.total_payments
				doc.previuos_commission = row.paid_amount
				if doc.amount > 0:
					doc.insert()
					lnk = get_link_to_form("Additional Salary" , doc.name , doc.name)
					frappe.msgprint(_(f"{row.sales_person}'s Additional Salary {lnk} was Created"),indicator='green')
			except Exception as e :
				frappe.msgprint(_(f"Error with {row.sales_person} : ")+_(str(e)),indicator='red')
				# frappe.msgprint(_(str(e)),indicator='red')
		else :
			if not row.employee :
					frappe.msgprint(_(f"{row.sales_person} doesn't have employee"))








    