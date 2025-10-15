// Copyright (c) 2025, market and contributors
// For license information, please see license.txt

frappe.ui.form.on('Barcode Generate', {
    purchase_invoice: function(frm) {
        frm.clear_table("items");

        if (frm.doc.purchase_invoice) {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Purchase Invoice",
                    name: frm.doc.purchase_invoice
                },
                callback: function(r) {
                    if (r.message) {
                        $.each(r.message.items, function(index, item) {
                            let row = frm.add_child("items");
                            row.item_code = item.item_code;
                            row.item_name = item.item_name;
                            row.qty = item.qty;
                        });
                        frm.refresh_field("items");
                    }
                }
            });
        }
    },

    scan_barcode: function(frm) {
        if (frm.doc.scan_barcode) {
            // Use the custom server-side function to get the parent item code
            frappe.call({
                method: "mosarof.mosarof.doctype.barcode_generate.barcode_generate.item_barcode", // Update with the actual path
                args: {
                    item_barcode: frm.doc.scan_barcode
                },
                callback: function(r) {
                    if (r.message) {
                        let item_code = r.message;

                        // Fetch the item details based on the returned item_code
                        frappe.call({
                            method: "frappe.client.get",
                            args: {
                                doctype: "Item",
                                name: item_code
                            },
                            callback: function(item_result) {
                                if (item_result.message) {
                                    let item = item_result.message;

                                    // Ensure that frm.doc.items is defined before accessing it
                                    if (!frm.doc.items) {
                                        frm.doc.items = [];
                                    }

                                    // Check if item already exists in the child table
                                    let existing_item = frm.doc.items.find(d => d.item_code === item.item_code);
                                    if (existing_item) {
                                        existing_item.qty += 1;
                                    } else {
                                        let row = frm.add_child("items");
                                        row.item_code = item.item_code;
                                        row.item_name = item.item_name;
                                        row.qty = 1;
                                    }

                                    frm.refresh_field("items");
                                }
                            }
                        });
                    } else {
                        frappe.msgprint(__('No item found with the scanned barcode.'));
                    }
                }
            });

            frm.set_value('scan_barcode', '');
        }
    }
});
