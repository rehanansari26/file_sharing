# Copyright (c) 2024, Rehan Ansari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from io import BytesIO
import math

class DrawingPermission(Document):
	def before_insert(self):
		self.status = 'Draft'
		for item in self.files:
			if item.file_url:
				item.child_status = 'Draft'

	def before_save(self): #exceptional case
		if not self.attached_to_name:
			return
		self.email_id = frappe.db.get_value('Supplier', self.attached_to_name, 'email_id')

		if not self.item_code:
			return
		if not self.files: #clash with client side call
			file_urls = frappe.db.get_all('File', {'attached_to_doctype': 'Item', 'attached_to_name': self.item_code}, ['file_url'])
			if not file_urls:
				self.files = []

			existing_file_urls = [row.file_url for row in self.files]
			for file in file_urls:
				if file.file_url not in existing_file_urls:
					row = self.append('files', {})
					row.child_item_code = self.item_code
					row.file_url = file.file_url
					row.child_status = 'Draft'
		for item in self.files:
			if item.view_based_sharing == 1 and item.views_allowed == 0:
				frappe.throw('Please specify the number of views allowed for row ${item.idx} to enable sharing')
			elif item.date_based_sharing == 1 and not item.from_date and not item.to_date:
				frappe.throw('Please specify the To Date for row ${item.idx} to enable sharing')

	def before_submit(self):
		drawing_permission_names = frappe.db.get_all(
			'Drawing Permission', 
			filters={
				'attached_to_name': 'Element14', 
				'item_code': '301010232', 
				'status': 'Shared'
			},
			pluck='name'
		)
		if not drawing_permission_names:
			return

		shared_file_urls = frappe.db.get_all(
			'Drawing Permission Item', 
			filters={
				'parent': ['in', drawing_permission_names], 
				'child_status': 'Shared'
			},
			fields=['file_url'],
			pluck='file_url'
		)
		for item in self.files:
			if item.file_url in shared_file_urls:
				frappe.throw(f'Duplicate entry: The file {frappe.bold(item.file_url)} is already shared')

		if not self.attached_to_name:
			frappe.throw('To share, we need you to enter the supplier name first')
			
		if not self.files:
			frappe.throw('To share, there must be a file in the files table. Please add a file before proceeding.')

		self.status = 'Shared'
		for item in self.files:
			if not frappe.db.count('File', {'file_url': item.file_url, 'attached_to_name': item.child_item_code}) == 1:
				frappe.msgprint(
					'The file {1} has been attached multiple times to item {0}.'.format(
						frappe.bold(item.child_item_code), frappe.bold(item.file_url)
					),
					title='Duplicate File Warning',
					indicator='red'
				)
			item.child_status = 'Shared'

		if self.email_id and self.send_email == 1:
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

			subject = f"Drawings Shared for {self.item_code}"

			frappe.sendmail(
				recipients=[self.email_id],
				subject=subject,
				message=message
			)
	
	def before_cancel(self):
		self.status = 'Cancelled'
		for item in self.files:
			item.child_status = 'Cancelled'

@frappe.whitelist()
def get_item_drawing_file_urls(item_code):
	file_data = frappe.db.get_all('File', {'attached_to_doctype': 'Item', 'attached_to_name': item_code}, ['file_url'])
	if not file_data:
		return None
	file_urls = [file_entry['file_url'] for file_entry in file_data]
	unique_file_urls = list(set(file_urls))
	return unique_file_urls
	
@frappe.whitelist()
def log_view_if_not_expired(reference_name):
	DP = frappe.db.get_value('Drawing Permission Item', reference_name, 'parent')
	status = frappe.db.get_value('Drawing Permission', DP, 'status')
	if status != 'Expired':
		doc = frappe.get_doc({
            "doctype": "Drawing View Log",
			"viewed_by": frappe.session.user,
			"reference_document": "Drawing Permission",
			"reference_name": DP,
			"child_reference_name": reference_name
        	}).insert(ignore_permissions=True,ignore_mandatory=True)
		doc.save()

def auto_expire_drawings_by_date():
	sharedDrawingsToExpire = frappe.db.get_all('Drawing Permission Item', {'status': 'Shared', 'to_date': ['<', frappe.utils.nowdate()]}, pluck='name')
	if not sharedDrawingsToExpire:
		return
	frappe.db.set_value('Drawing Permission Item', sharedDrawingsToExpire, 'child_status', 'Expired')

@frappe.whitelist()	
def get_watermarked_pdf(file_url, supplier_name):
    input_pdf = PdfReader(frappe.get_site_path('public', 'files', file_url.split('/')[-1]))
    watermark_text = supplier_name
    watermark_opacity = 0.3
    watermark_angle = 45
    watermark_font_size = 18
    text_width = 100
    text_height = 100

    watermark = BytesIO()
    c = canvas.Canvas(watermark)

    page_width = input_pdf.pages[0].mediabox[2]
    page_height = input_pdf.pages[0].mediabox[3]
    diagonal = int(math.sqrt(page_width ** 2 + page_height ** 2))
    x_offset = -diagonal
    while x_offset < diagonal:
        y_offset = -diagonal
        while y_offset < diagonal:
            c.saveState()
            c.translate(x_offset, y_offset)
            c.rotate(watermark_angle)
            c.setFillColorRGB(0, 0, 0, watermark_opacity)
            c.setFont("Helvetica", watermark_font_size)
            c.drawString(0, 0, watermark_text)
            c.restoreState()
            y_offset += text_height
        x_offset += text_width

    c.save()
    watermark.seek(0)

    output_pdf = PdfWriter()

    for i in range(len(input_pdf.pages)):
        page = input_pdf.pages[i]
        watermark_reader = PdfReader(watermark)
        watermark_page = watermark_reader.pages[0]
        page.merge_page(watermark_page)
        output_pdf.add_page(page)

    pdf_bytes = BytesIO()
    output_pdf.write(pdf_bytes)
    pdf_bytes.seek(0)

    return pdf_bytes.getvalue()