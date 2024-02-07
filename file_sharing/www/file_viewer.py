import frappe

def get_context(context):
    context.file_url, context.allow_download, context.parent,
    context.child_status, context.is_private = frappe.db.get_value(
        'File Permission Item',
        frappe.form_dict.get('query'),
        ['file_url', 'allow_download', 'parent', 'child_status', 'is_private']
    )

    context.supplier_name = frappe.db.get_value(
        'File Permission',
        context.parent,
        'user_reference'
    )