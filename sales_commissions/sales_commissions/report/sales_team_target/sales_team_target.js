// Copyright (c) 2016, Peter Maged and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Team Target"] = {
  filters: [
    {
    	"fieldname":"company",
    	"label": __("Company"),
    	"fieldtype": "Link",
    	"options": "Company",
    	"default": frappe.defaults.get_user_default("Company"),
    	"reqd":1
    },
    {
      fieldname: "period",
      label: __("Payroll Period"),
      fieldtype: "Link",
      options: "Payroll Period",
      reqd: 1,
      change: function () {
        let period = frappe.query_report.get_filter_value("period");
        if (period) {
          frappe.call({
            method: "frappe.client.get",
            args: {
              doctype: "Payroll Period",
              name: frappe.query_report.get_filter_value("period"),
            },
            callback: function (r) {
              frappe.query_report.set_filter_value("from_date", r.message.start_date);
              frappe.query_report.set_filter_value("to_date", r.message.end_date);
              frappe.query_report.refresh();
            },
          });
        } else {
          frappe.query_report.set_filter_value("from_date", "");
          frappe.query_report.set_filter_value("to_date", "");
          frappe.query_report.refresh();
        }
      },
			"get_query": function() {
				var company = frappe.query_report.get_filter_value('company');
				return {
					filters: {
						"company": company
					}
				};
			}
    },
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      // options: "Payroll Period",
      read_only: 1,
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
      // options: "Payroll Period",
      read_only: 1,
    },
    // {
    // 	"fieldname":"customer",
    // 	"label": __("Customer"),
    // 	"fieldtype": "Link",
    // 	"options": "Customer"
    // },

    {
      fieldname: "sales_person",
      label: __("Sales Person"),
      fieldtype: "Link",
      options: "Sales Person",
    },
  ],
  onload: function (report) {
    report.page
      .add_inner_button(__("Submit"), function () {
        if (!frappe.query_report.get_filter_value("period"))
          frappe.throw(__("Please set Payroll Period"));
        frappe.call({
          method:
            "sales_commissions.sales_commissions.report.sales_team_target.sales_team_target.submit_additional_salaries",
          args: {
            data: frappe.query_report.data || [],
            period: frappe.query_report.get_filter_value("period"),
          },
          callback: function (r) {
            frappe.query_report.refresh();
          },
        });
      })
      .addClass("btn-primary");

    report.page
      .add_inner_button(__("Show"), function () {
        if (!frappe.query_report.get_filter_value("period"))
          frappe.throw(__("Please set Payroll Period"));
        frappe.call({
          method: "frappe.client.get",
          args: {
            doctype: "Payroll Period",
            name: frappe.query_report.get_filter_value("period"),
          },
          callback: function (r) {
            frappe.set_route("List", "Additional Salary", {
              payroll_date: [
                "between",
                [r.message.start_date, r.message.end_date],
              ],
              commission: 1,
            });
          },
        });
      })
      .addClass("btn-primary");
  },
};
