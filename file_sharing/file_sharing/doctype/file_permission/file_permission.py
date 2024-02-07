# Copyright (c) 2024, Rehan Ansari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import math
import re

class FilePermission(Document):
	def before_save(self):
		#isFileAlreadyShared(self)
		setStatusForFilesWithUrl(self, 'Draft')
		fetchEmailToSend(self)
		#fetch_and_append_files(self)

	def before_submit(self):
		validate_files_before_sharing(self)
		setStatusForFilesWithUrl(self, 'Shared')

		if self.email_id and self.send_email == 1:
			send_email_with_file_details(self)
	
	def before_cancel(self):
		setStatusForFilesWithUrl(self, 'Cancelled')

def isFileAlreadyShared(self):
	active_shared_permissions = frappe.db.get_all(
		'File Permission', 
		{
			'user_reference': self.user_reference,
			'file_reference': self.file_reference, 
			'status': 'Shared',
			'docstatus': 1
		},
		pluck='name'
	)
	if not active_shared_permissions:
		return
	
	shared_file_urls = frappe.db.get_all(
		'File Permission Item', 
		{
			'parent': ['in', active_shared_permissions],
			'child_status': 'Shared',
			'docstatus': 1
		},
		['file_url'],
		pluck='file_url'
	)
	for file in self.files:
		if file.file_url in shared_file_urls:
			frappe.throw(f'Duplicate entry: The file {frappe.bold(file.file_url)} is already shared')

def setStatusForFilesWithUrl(self, status):
	if self.status == status:
		return
	self.status = status
	for item in self.files:
		if item.child_status == status:
			return
		if item.file_url:
			item.child_status = status

def fetchEmailToSend(self):
	if not self.user_doctype or not self.user_reference:
		return
	self.email_id = frappe.db.get_value(self.user_doctype, self.user_reference, 'email_id') or None

# def fetch_and_append_files(self):
# 	if not self.file_doctype or not self.file_reference:
# 		return
# 	if not self.files: #clash with client side call
# 		file_data = frappe.db.get_all('File', {'attached_to_doctype': self.file_doctype, 'attached_to_name': self.file_reference}, ['file_url', 'is_private'])
# 		if not file_data:
# 			self.files = []
# 		existing_file_urls = [row.file_url for row in self.files]
# 		for file in file_data:
# 			if file.file_url not in existing_file_urls:
# 				row = self.append('files', {})
# 				row.child_file_reference = self.file_reference
# 				row.file_url = file.file_url
# 				row.is_private = file.is_private
# 				row.child_status = 'Draft'

def validate_files_before_sharing(self):
	if not self.user_reference:
		frappe.throw(f'To share, we need you to enter the {self.user_doctype} first')
	
	portal_user = frappe.db.get_value('Portal User', {'parent': self.user_reference, 'parenttype': self.user_doctype}, 'user')
	if not portal_user:
		frappe.throw(f"{self.user_doctype} are not registered as a portal user")
		
	if not self.files:
		frappe.throw('To share, there must be a file in the files table. Please add a file before proceeding.')

	for item in self.files:
		if item.view_based_sharing == 1 and item.views_allowed == 0:
			frappe.throw(f'Please specify the number of views allowed for row {item.idx} to enable sharing')

		elif item.date_based_sharing == 1 and not item.to_date:
			frappe.throw(f'Please specify the To Date for row {item.idx} to enable sharing')

		if not frappe.db.count('File', {'file_url': item.file_url, 'attached_to_name': item.child_file_reference}) == 1:
			frappe.msgprint(
				'The file {1} has been attached multiple times to item {0}.'.format(
					frappe.bold(item.child_file_reference), frappe.bold(item.file_url)
				),
				title='Duplicate File Warning',
				indicator='red'
			)

def send_email_with_file_details(self):
	email = self.email_id
	if is_valid_email(email_id):
		frappe.msgprint(f"{email_id} is not a valid email address.")
		return

	item_details = []
	for item in self.files:
		details = f"File: {item.file_url}"
		if item.date_based_sharing == 1:
			valid_from = formatdate(item.from_date)
			valid_to = formatdate(item.to_date)
			details += f", valid from {valid_from} to {valid_to}"
			if item.view_based_sharing == 1:
				details += f", valid for {item.views_allowed} views"
			item_details.append(details)

			message = f"Dear Supplier,<br><br>The following drawings have been shared with you:<br><br>"
			message += "<br>".join(item_details)
			message += f"<br><br>To view these shared drawings, please <a href='https://${frappe.utils.get_url()}'>visit the supplier portal</a>.<br><br>Regards,<br>ERP Team"

			subject = f"Drawings Shared for {self.file_reference}"

			frappe.sendmail(
				recipients=[self.email_id],
				subject=subject,
				message=message
			)

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def auto_expire_drawings_by_date():
	sharedDrawingsToExpire = frappe.db.get_all('File Permission Item', {'date_based_sharing': 1, 'status': 'Shared', 'to_date': ['<', frappe.utils.nowdate()], 'docstatus': 1}, pluck='name')
	if not sharedDrawingsToExpire:
		return
	frappe.db.set_value('File Permission Item', sharedDrawingsToExpire, 'child_status', 'Expired')
	sharedParentList = frappe.db.get_all('File Permission', {'status': 'Shared', 'docstatus': 1})
	if not sharedParentList:
		return
	for fs in sharedParentList:
		child_status_list = frappe.db.get_all('File Permission Item', {'parent': fs.name}, ['child_status'], pluck='child_status')
		result = all(map(lambda x: x == 'Expired', child_status_list))
		if result:
			frappe.db.set_value('File Permission', fs.name, 'status', 'Expired')

#JS
@frappe.whitelist()
def get_unique_file_urls_for_document(file_doctype, file_reference):
	file_data = frappe.db.get_all('File',{'attached_to_doctype': file_doctype, 'attached_to_name': file_reference},['file_url', 'is_private'], group_by='file_url')	
	if not file_data:
		return None
	return file_data

#Web Page	
@frappe.whitelist()
def log_view_if_not_expired(reference_name):
	status, FP = frappe.db.get_value('File Permission Item', reference_name, ['child_status', 'parent'])
	if status != 'Expired':
		doc = frappe.get_doc({
            "doctype": "File View Log",
			"viewed_by": frappe.session.user,
			"reference_document": "File Permission",
			"reference_name": FP,
			"child_reference_name": reference_name
        	}).insert(ignore_permissions=True,ignore_mandatory=True)
		doc.save()

@frappe.whitelist()	
def get_watermarked_pdf(file_url, supplier_name, is_private):
    status = 'private' if int(is_private) == 1 else 'public'
    # Replace this with your actual file path retrieval
    input_pdf = PdfReader(frappe.get_site_path(status, 'files', file_url.split('/')[-1]))  # file_url should be the local path to the PDF file
    watermark_text = supplier_name
    watermark_opacity = 0.1  # Reduced opacity for better readability of the original content
    watermark_angle = 45
    watermark_font_size = 18  # Adjust as needed

    output_pdf = PdfWriter()

    for page in input_pdf.pages:
        page_width = page.mediabox[2]
        page_height = page.mediabox[3]

        # Create a watermark canvas that matches the size of the current page
        watermark = BytesIO()
        c = canvas.Canvas(watermark, pagesize=(page_width, page_height))

        # Increase the step size to add more space between watermarks
        step_size = max(watermark_font_size * 4, 100)  # Adjust as needed
        num_watermarks_x = int(page_width / step_size) + 2
        num_watermarks_y = int(page_height / step_size) + 2

        # Loop to cover the page diagonally with watermarks
        for x in range(num_watermarks_x):
            for y in range(num_watermarks_y):
                c.saveState()
                # Translate to the position where the watermark will be drawn
                c.translate((x - 1) * step_size, (y - 1) * step_size)
                c.rotate(watermark_angle)
                c.setFillColorRGB(0, 0, 0, watermark_opacity)
                c.setFont("Helvetica", watermark_font_size)
                # Draw the watermark text
                c.drawString(0, 0, watermark_text)
                c.restoreState()

        c.save()
        watermark.seek(0)

        watermark_reader = PdfReader(watermark)
        watermark_page = watermark_reader.pages[0]

        # Merge the watermark page with the current page
        page.merge_page(watermark_page)
        output_pdf.add_page(page)

    pdf_bytes = BytesIO()
    output_pdf.write(pdf_bytes)
    pdf_bytes.seek(0)

    return pdf_bytes.getvalue()
