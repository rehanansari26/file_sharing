# Copyright (c) 2024, Rehan Ansari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FileViewLog(Document):
	def after_insert(self):
		if self.reference_document == "File Permission":

			views_allowed, views_seen, view_based_sharing = frappe.db.get_value(
				'File Permission Item', 
				self.child_reference_name,
				['views_allowed', 'views_seen', 'view_based_sharing']
			)

			# if not view_based_sharing:
			# 	return

			#case 1 view_based_sharing
			new_views = views_seen + 1
			
			if new_views == views_allowed:
				frappe.db.set_value('File Permission Item', self.child_reference_name, 
					{
    					'views_seen': new_views,
    					'child_status': 'Expired'
					}
				)
				child_status_list = frappe.db.get_all('File Permission Item', {'parent': self.reference_name}, ['child_status'], pluck='child_status')
				result = all(map(lambda x: x == 'Expired', child_status_list))
				if result:
					frappe.db.set_value('File Permission', self.reference_name, 'status', 'Expired')
					
			elif not views_allowed or new_views < views_allowed:
				frappe.db.set_value('File Permission Item', self.child_reference_name, 'views_seen', new_views)

			#case 2 date_based_sharing

			#schedular