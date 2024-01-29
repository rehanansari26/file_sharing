import frappe

def get_context(context):
    context.drawing_details = frappe.db.get_value('Drawing Permission Item', frappe.form_dict.get('query'), ['file_url','allow_download', 'parent', 'child_status'])
    context.supplier_name = frappe.db.get_value('Drawing Permission', context.drawing_details[2], 'attached_to_name')