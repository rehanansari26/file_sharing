import frappe

def get_context(context):
    context.user_type = frappe.db.get_value('User', frappe.session.user, 'user_type')

    if context.user_type == "Website User":
        context.supplier = frappe.db.get_value('Portal User', {'user': frappe.session.user}, 'parent')

        context.drawing_permission_names = frappe.db.get_all(
            'Drawing Permission',
            {'attached_to_name': context.supplier, 'status': 'Shared'},   
            pluck='name'
        ) or None

        # Fetch the first set of data
        drawing_permission_details_1 = frappe.db.get_all(
            'Drawing Permission Item',
            {'parent': ['in', context.drawing_permission_names], 'child_status': 'Shared', 'date_based_sharing': 0},
            ['name', 'child_item_code', 'child_item_code.item_name as item_name', 'file_url', 'views', 'views_allowed', 'parent', '']
        )   

        # Fetch the second set of data
        drawing_permission_details_2 = frappe.db.get_all(
            'Drawing Permission Item',
            {'parent': ['in', context.drawing_permission_names], 'child_status': 'Shared', 'date_based_sharing': 1, 'from_date': ['<=', frappe.utils.nowdate()]},
            ['name', 'child_item_code', 'child_item_code.item_name as item_name', 'file_url', 'views', 'views_allowed', 'parent']
        )

        # Combine the two lists
        combined_drawing_permission_details = drawing_permission_details_1 + drawing_permission_details_2

        # Remove duplicates
        unique_drawing_permission_details = {v['name']: v for v in combined_drawing_permission_details}.values()

        # Assign the unique list back to context
        context.drawing_permission_details = list(unique_drawing_permission_details)
    else:
        frappe.throw("This page is only accessible to suppliers.", frappe.PermissionError)

