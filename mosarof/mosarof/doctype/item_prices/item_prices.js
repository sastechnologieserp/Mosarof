// Copyright (c) 2024, rawasrazak and contributors
// For license information, please see license.txt

frappe.ui.form.on('Item Prices', {
    refresh(frm) {
        frm.fields_dict['purchase_invoice'].get_query = function() {
            return {
                filters: {
                    docstatus: 1
                }
            };
        };
    },
    purchase_invoice(frm) {
        if (frm.doc.purchase_invoice) {
            fetchItemCodes(frm.doc.purchase_invoice, frm);
        }
    },
    item_prices_table_add(frm, cdt, cdn) {
        const child = locals[cdt][cdn];
        if (child.item_code) {
            frappe.call({
                method: "mosarof.mosarof.doctype.item_prices.item_prices.get_stock_uom",
                args: { item_code: child.item_code },
                callback: function (r) {
                    if (r.message) {
                        child.uom = r.message;
                        fetchItemPrices(child.item_code, child.uom, frm, cdt, cdn);
                    }
                }
            });
        }
        frm.refresh_field('item_prices_table');
    },
    scan_barcode: function(frm) {
        let barcode = frm.doc.scan_barcode;
        if (!barcode) return;

        frappe.call({
            method: "mosarof.mosarof.doctype.item_prices.item_prices.get_item_from_barcode",
            args: {
                barcode: barcode
            },
            callback: function(r) {
                if (r.message) {
                    let item_code = r.message;
                    let existing_row = frm.doc.item_prices_table.find(row => row.item_code === item_code);

                    if (existing_row) {
                        frappe.show_alert("item already added");
                    } else {
                        let row = frm.add_child("item_prices_table");
                        row.item_code = item_code;
                        frm.script_manager.trigger("item_code", row.doctype, row.name);
                    }

                    frm.refresh_field("item_prices_table");
                    frm.set_value("scan_barcode", "");
                } else {
                    frappe.msgprint("No item found for this barcode");
                }
            }
        });
    }
});

frappe.ui.form.on('Item Prices Table', {
    item_code(frm, cdt, cdn) {
        const child = locals[cdt][cdn];

        if (!child.item_code) return;

        frappe.call({
            method: "mosarof.mosarof.doctype.item_prices.item_prices.get_stock_uom",
            args: { item_code: child.item_code },
            callback: function (r) {
                child.uom = r.message;
                fetchItemPrices(child.item_code, child.uom, frm, cdt, cdn);
                frm.refresh_field('item_prices_table');
            }
        });

        frappe.call({
            method: "mosarof.mosarof.doctype.item_prices.item_prices.item_name",
            args: { item_code: child.item_code },
            callback: function (r) {
                child.item_name = r.message;
                frm.refresh_field('item_prices_table');
            }
        });
    },

    uom(frm, cdt, cdn) {
        const child = locals[cdt][cdn];
        if (child.item_code && child.uom) {
            fetchItemPrices(child.item_code, child.uom, frm, cdt, cdn);
        }
    }
});

function fetchItemCodes(purchase_invoice, frm) {
    frappe.call({
        method: 'mosarof.mosarof.doctype.item_prices.item_prices.fetch_item_codes',
        args: { purchase_invoice },
        callback: function(r) {
            if (r.message) {
                frm.fields_dict['item_prices_table'].grid.remove_all();
                r.message.forEach(item => {
                    const row = frappe.model.add_child(frm.doc, 'Item Prices Table', 'item_prices_table');
                    row.item_code = item.item_code;
                    row.item_name = item.item_name;
                    row.uom = item.uom;
                    fetchItemPrices(item.item_code, item.uom, frm, 'Item Prices Table', row.name);
                });
                frm.refresh_field('item_prices_table');
            }
        }
    });
}

function fetchItemPrices(item_code, uom, frm, cdt, cdn) {
    const child = locals[cdt][cdn];

    // Fetch valuation rate
    frappe.call({
        method: "mosarof.mosarof.doctype.item_prices.item_prices.valuation_rate",
        args: { item_code },
        callback: function (r) {
            child.valuation_rate = r.message || 0;
            frm.refresh_field('item_prices_table');
        }
    });

    // Fetch incoming rate
    frappe.call({
        method: "mosarof.mosarof.doctype.item_prices.item_prices.incoming_rate",
        args: { item_code },
        callback: function (r) {
            child.cost_price = r.message || 0;
            frm.refresh_field('item_prices_table');
        }
    });

    const price_lists = [
        { field: 'selling_price_1', name: 'Retail Price Br1' },
        { field: 'selling_price_2', name: 'Retail Price Br2' },
        { field: 'selling_price_3', name: 'Wholesale Rate' },
    ];

    price_lists.forEach(p => {
        frappe.call({
            method: "mosarof.mosarof.doctype.item_prices.item_prices.get_price",
            args: {
                item_code: item_code,
                price_list: p.name,
                uom: uom
            },
            callback: function (r) {
                child[p.field] = r.message || 0;
                frm.refresh_field('item_prices_table');
            }
        });
    });
}
