import frappe
from datetime import date
import json
no_cache = 1

def get_context(context):
    if not 'Supplier' in frappe.get_roles():
        frappe.throw("This page is only accessible to suppliers.", frappe.PermissionError)

    context.user_type = frappe.db.get_value('User', frappe.session.user, 'user_type')
    if not context.user_type == "Website User":
        frappe.throw("You are not a valid user for this operation.", frappe.PermissionError)

    context.supplier = frappe.db.get_value('Portal User', {'user': frappe.session.user, 'parenttype': 'Supplier'}, 'parent')
    if not context.supplier:
        frappe.throw("You are not registered as a portal user.", frappe.PermissionError)

    context.drawing_permissions = frappe.db.get_all('File Permission',{'user_reference': context.supplier, 'docstatus': 1, 'status': 'Shared'}, pluck='name') or None
    if not context.drawing_permissions:
        frappe.throw("No drawings have been shared with you.", frappe.PermissionError)

    context.drawing_permission_details = frappe.db.get_all('File Permission Item',{'parent': ['in', context.drawing_permissions], 'child_status': 'Shared'},['name', 'child_file_reference', 'child_file_reference.item_name as item_name', 'file_url', 'views_seen', 'views_allowed', 'date_based_sharing', 'view_based_sharing', 'parent'])
