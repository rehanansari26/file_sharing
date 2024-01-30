import frappe

def get_context(context):
    context.file_url, context.allow_download, context.parent, context.child_status = frappe.db.get_value('Drawing Permission Item', frappe.form_dict.get('query'), ['file_url','allow_download', 'parent', 'child_status'])
    context.supplier_name = frappe.db.get_value('Drawing Permission', context.parent, 'attached_to_name')