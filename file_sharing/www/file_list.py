import frappe
from frappe.utils import formatdate

no_cache = 1

def get_context(context):
    if 'Supplier' not in frappe.get_roles():
        frappe.throw("This page is only accessible to suppliers.", frappe.PermissionError)

    context.user_type = frappe.db.get_value(
        'User', frappe.session.user, 'user_type'
    )
    if context.user_type != "Website User":
        frappe.throw("You are not a valid user for this operation.", frappe.PermissionError)

    context.supplier = frappe.db.get_value(
        'Portal User', 
        {'user': frappe.session.user, 'parenttype': 'Supplier'},
        'parent'
    )
    if not context.supplier:
        frappe.throw("You are not registered as a portal user.", frappe.PermissionError)

    context.file_permissions = frappe.db.get_all(
        'File Permission',
        filters={
            'user_reference': context.supplier, 
            'docstatus': 1, 
            'status': 'Shared'
        }, 
        pluck='name'
    ) or None

    if not context.file_permissions:
        frappe.throw("No file have been shared with you.", frappe.PermissionError)

    file_permission_details = frappe.db.get_all(
        'File Permission Item',
        filters={
            'parent': ['in', context.file_permissions],
            'child_status': 'Shared'
        },
        fields=[
            'name', 
            'c_file_reference',
            'file_url', 
            'views_allowed', 
            'views', 
            'to_date', 
            'date_based_sharing', 
            'view_based_sharing', 
            'parent'
        ]
    )

    for item in file_permission_details:
        if item.get('to_date'):
            item['to_date'] = formatdate(item['to_date'])
        #File DocType = 'Item'
        item['item_name'] = frappe.db.get_value('Item', item.get('c_file_reference'), 'item_name')

    context.file_permission_details = file_permission_details