// Copyright (c) 2024, Rehan Ansari and contributors
// For license information, please see license.txt

frappe.ui.form.on('File Permission', {
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
	refresh: function(frm) {

		$('.grid-add-row').hide()

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
                    messages.push(`'${file.file_url}': User can view this unlimited times`);
                }
            });
        
            var introMessage = messages.length > 0 ? messages.join("<br>") : "No notifications.";
            frm.set_intro(introMessage, messages.length > 0 ? "blue" : "green");
        }           

		// if (frm.doc.docstatus == 0) {
		// 	//remove (!frm.doc.files || frm.doc.files.length === 0) condition
		// 	frm.add_custom_button(__('Fetch File'), function () {
		// 		frappe.call({
		// 			method: "file_sharing.file_sharing.doctype.file_permission.file_permission.get_unique_file_urls_for_document",
		// 			args: {
		// 				"file_doctype": frm.doc.file_doctype,
		// 				"file_reference": frm.doc.file_reference
		// 			},
		// 			callback: function (res) {
		// 				if (res.message && res.message.length > 0) {
		// 					frm.set_value('files', []);
		// 					res.message.forEach(data => {
		// 						let child = frm.add_child('files');
		// 						child.c_file_reference = frm.doc.file_reference;
		// 						child.file_url = data.file_url;
		// 						child.is_private = data.is_private;
		// 						child.child_status = 'Draft';
		// 					});
		// 					frm.refresh_field('files');
		// 					$('.grid-add-row').hide();
		// 				}
		// 				else{
		// 					frm.set_value('files', [])
		// 					frappe.msgprint({
		// 						title: __('File Not Found'),
		// 						message: __(`No files available for file reference <b>${frm.doc.file_reference}</b>. Please verify the file reference or upload files.`),
		// 						indicator: 'orange'
		// 					});
		// 				}
		// 			}
		// 		})
		// 	});
		// }

		if (frm.doc.__islocal && frm.doc.amended_from) {
			frm.doc.files.forEach(function(file) {
				file.child_status = null;
			});
			frm.refresh_field('files');
		}    
	},
	file_reference: function(frm) {
		if (frm.doc.file_reference){
			frappe.call({
				method: "file_sharing.file_sharing.doctype.file_permission.file_permission.get_unique_file_urls_for_document",
				args: {
					"file_doctype": frm.doc.file_doctype,
					"file_reference": frm.doc.file_reference
				},
				callback: function (res) {
					if (res.message && res.message.length > 0) {
						frm.set_value('files', []);
						res.message.forEach(data => {
							let child = frm.add_child('files');
							child.c_file_reference = frm.doc.file_reference;
							child.file_url = data.file_url;
							child.is_private = data.is_private;
							// child.child_status = 'Draft';
						});
						frm.refresh_field('files');
						$('.grid-add-row').hide();
					}
					else{
						frm.set_value('files', [])
						frappe.msgprint({
							title: __('File Not Found'),
							message: __(`No files available for ${frm.doc.file_doctype} <b>${frm.doc.file_reference}</b>. Please verify the ${frm.doc.file_doctype} or upload files.`),
							indicator: 'orange'
						});
					}
				}
			})
		}
	},
});
frappe.ui.form.on('File Permission Item', {
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
	open_file: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		let baseUrl = window.location.origin;
		window.open(`${baseUrl}${d.file_url}`, '_blank');
	},	
    open_view_log: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
        let baseUrl = window.location.origin;
		window.location.href = `${baseUrl}/app/file-view-log?child_reference_name=${d.name}`
	}
})
