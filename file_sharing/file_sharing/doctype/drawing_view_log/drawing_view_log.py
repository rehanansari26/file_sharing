# Copyright (c) 2024, Rehan Ansari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DrawingViewLog(Document):
	def after_insert(self):
		if self.reference_document == "Drawing Permission":

			views_allowed, current_views, view_based_sharing = frappe.db.get_value(
				'Drawing Permission Item', 
				self.child_reference_name, 
				['views_allowed', 'views', 'view_based_sharing']
			)

			# if not view_based_sharing:
			# 	return

			#case 1 view_based_sharing
			new_views = current_views + 1
			
			if new_views == views_allowed:
				frappe.db.set_value('Drawing Permission Item', self.child_reference_name, 'views', new_views)
				frappe.db.set_value('Drawing Permission Item', self.child_reference_name, 'child_status', 'Expired')
				status_list = frappe.db.get_all('Drawing Permission Item', {'parent': self.reference_name}, ['child_status'], group_by='child_status')

				if len(status_list) == 1 and status_list[0]['child_status'] == 'Expired':
    				# Your code for the 'Expired' condition
					frappe.db.set_value('Drawing Permission', self.reference_name, 'status', 'Expired')
			elif not views_allowed or new_views < views_allowed:
				frappe.db.set_value('Drawing Permission Item', self.child_reference_name, 'views', new_views)

			#case 2 date_based_sharing
