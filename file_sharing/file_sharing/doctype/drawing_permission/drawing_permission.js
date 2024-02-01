// Copyright (c) 2024, Rehan Ansari and contributors
// For license information, please see license.txt

frappe.ui.form.on('Drawing Permission', {
	refresh: function(frm) {
		if (frm.doc.__islocal && frm.doc.amended_from) {
			frm.doc.files.forEach(function(file) {
				file.child_status = null;
			});
			frm.refresh_field('files');
		}
        if (frm.doc.docstatus == 1) {
            var messages = [];
            frm.doc.files.forEach(function(file) {
                var toDate = new Date(file.to_date);
                var currentDate = new Date(frappe.datetime.get_today());
                if (file.view_based_sharing == 1 && file.date_based_sharing == 1 && toDate > currentDate && file.views_allowed > 0 && file.child_status == 'Shared') {
                    var views_remaining = file.views_allowed - file.views;
                    var timeDiff = toDate.getTime() - currentDate.getTime();
                    var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24));
        
                    messages.push(`'${file.file_url}': ${views_remaining} view(s) left for remaining ${diffDays} day(s)`);
                }
                else if (file.date_based_sharing == 1 && file.child_status == 'Shared' && toDate > currentDate) {
                    var timeDiff = toDate.getTime() - currentDate.getTime();
                    var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24));
                    
                    messages.push(`'${file.file_url}': ${diffDays} day(s) remaining`);

                } else if (file.view_based_sharing == 1 && file.child_status == 'Shared' && file.views_allowed > 0) {
                    var views_remaining = file.views_allowed - file.views;
                    messages.push(`'${file.file_url}': ${views_remaining} view(s) left`);

                }
				else if (frm.doc.status == 'Expired') {
					messages.push('Expired')
				}
                else {
                    messages.push(`'${file.file_url}': Supplier can view this unlimited times`);
                }
            });
        
            var introMessage = messages.length > 0 ? messages.join("<br>") : "No notifications.";
            frm.set_intro(introMessage, messages.length > 0 ? "blue" : "green");
        }               
		
		$('.grid-add-row').hide()

		if (frm.doc.item_code && frm.doc.docstatus == 0) {
			//remove (!frm.doc.files || frm.doc.files.length === 0) condition
			frm.add_custom_button(__('Fetch File'), function () {
				frappe.call({
					method: "file_sharing.file_sharing.doctype.drawing_permission.drawing_permission.get_item_drawing_file_urls",
					args: {
						"item_code": frm.doc.item_code
					},
					callback: function (res) {
						if (res.message && res.message.length > 0) {
							let fileData = res.message;
							frm.set_value('files', []);
							fileData.forEach(data => {
								let child_row = frm.add_child('files');
								child_row.child_item_code = frm.doc.item_code;
								child_row.file_url = data.file_url;
								child_row.is_private = data.is_private;
								child_row.child_status = 'Draft';
							});
							frm.refresh_field('files');
							$('.grid-add-row').hide();
						}
						else{
							frm.set_value('files', [])
							frappe.msgprint({
								title: __('File Not Found'),
								message: __(`No files available for item code <b>${frm.doc.item_code}</b>. Please verify the code or upload files.`),
								indicator: 'orange'
							});
						}
					}
				})
			});
		}
	},
	item_code: function(frm) {
		if (frm.doc.item_code){
			frappe.call({
				method: "file_sharing.file_sharing.doctype.drawing_permission.drawing_permission.get_item_drawing_file_urls",
				args: {
					"item_code": frm.doc.item_code
				},
				callback: function (res) {
					if (res.message && res.message.length > 0) {
						let fileData = res.message;
						frm.set_value('files', []);
						fileData.forEach(data => {
							let child_row = frm.add_child('files');
							child_row.child_item_code = frm.doc.item_code;
							child_row.file_url = data.file_url;
							child_row.is_private = data.is_private;
							child_row.child_status = 'Draft';
						});
						frm.refresh_field('files');
						$('.grid-add-row').hide();
					}
					else{
						frm.set_value('files', [])
						frappe.msgprint({
							title: __('File Not Found'),
							message: __(`No files available for item code <b>${frm.doc.item_code}</b>. Please verify the code or upload files.`),
							indicator: 'orange'
						});
					}
				}
			})
		}
	},
	onload: function(frm) {
        var css = `
			div[data-fieldname="child_status"]:not([title="Status"]) .static-area.ellipsis {
				background: var(--bg-purple);color: var(--text-on-purple);
				padding: 3px 5px;
				border-radius: 13px;
				display: inline-block;
				text-align: center;
				font-size: 10px;
				line-height: 1.5;
				vertical-align: middle;
			}
        `;
        $("<style>").prop("type", "text/css").html(css).appendTo("head");
    },
	amended_from: function(frm) {
		
	}
});
frappe.ui.form.on('Drawing Permission Item', {
	form_render: function(frm) {
		$('.grid-insert-row-below').hide();
		$('.grid-insert-row').hide();
		$('.grid-duplicate-row').hide();
	},
	files_remove: function(frm) {
		setTimeout(function() {
			$('.grid-add-row').hide();
		}, 100); // 1000 milliseconds = 1 second
	},
	file_display: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		let baseUrl = window.location.origin;
		window.open(`${baseUrl}${d.file_url}`, '_blank');
	},	
    view_log_display: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
        let baseUrl = window.location.origin;
		window.location.href = `${baseUrl}/app/drawing-view-log?child_reference_name=${d.name}`
	},
	to_date: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if (d.from_date && d.to_date && d.to_date < d.from_date) {
			frappe.throw('To Date should be greater than from date')
		}
	}
})
