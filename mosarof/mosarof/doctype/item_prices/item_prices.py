
# Copyright (c) 2025, rawasrazak and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document

class ItemPrices(Document):
    def on_update(self):
        update_item_price_entries(self.name)

@frappe.whitelist()
def valuation_rate(item_code):
    entries = frappe.get_all(
        'Stock Ledger Entry',
        filters={'item_code': item_code, 'is_cancelled': 0},
        fields=['valuation_rate'],
        order_by='posting_date DESC, posting_time DESC, creation DESC',
        limit=1
    )
    return entries[0].get('valuation_rate') if entries else 0

@frappe.whitelist()
def incoming_rate(item_code):
    entries = frappe.get_all(
        'Stock Ledger Entry',
        filters={'item_code': item_code, 'is_cancelled': 0},
        fields=['incoming_rate'],
        order_by='posting_date DESC, posting_time DESC',
        limit=1
    )
    return entries[0].get('incoming_rate') if entries else 0

@frappe.whitelist()
def get_price(item_code, price_list, uom):
    price = frappe.get_value(
        'Item Price',
        {
            'item_code': item_code,
            'price_list': price_list,
            'uom': uom
        },
        'price_list_rate'
    )
    return price or 0

@frappe.whitelist()
def get_stock_uom(item_code):
    return frappe.get_value('Item', item_code, 'stock_uom') or ""

@frappe.whitelist()
def item_name(item_code):
    return frappe.db.get_value('Item', {'item_code': item_code}, 'item_name') or ""

@frappe.whitelist()
def fetch_item_codes(purchase_invoice):
    items_data = []
    pi_doc = frappe.get_doc('Purchase Invoice', purchase_invoice)
    for item in pi_doc.items:
        items_data.append({
            'item_code': item.item_code,
            'item_name': item.item_name,
            'uom': item.uom
        })
    return items_data

@frappe.whitelist()
def stock_bal(item_code):
    entries = frappe.get_all(
        'Stock Ledger Entry',
        filters={'item_code': item_code, 'is_cancelled': 0},
        fields=['qty_after_transaction'],
        order_by='posting_date DESC, posting_time DESC',
        limit=1
    )
    return entries[0].get('qty_after_transaction') if entries else 0

@frappe.whitelist()
def update_item_price_entries(docname):
    doc = frappe.get_doc("Item Prices", docname)
    price_map = {
        "Retail Price Br1": "selling_price_1",
        "Retail Price Br2": "selling_price_2",
        "Wholesale Rate": "selling_price_3",
    }

    if not doc.item_prices_table:
        return

    for row in doc.item_prices_table:
        for price_list, field in price_map.items():
            price_list_rate = getattr(row, field, 0)
            if not price_list_rate:
                continue

            existing_price = frappe.db.exists("Item Price", {
                "item_code": row.item_code,
                "price_list": price_list,
                "uom": row.uom
            })

            if existing_price:
                item_price_doc = frappe.get_last_doc("Item Price", {
                    "item_code": row.item_code,
                    "price_list": price_list,
                    "uom": row.uom
                })
                item_price_doc.price_list_rate = price_list_rate
                item_price_doc.save()
            else:
                item_price_doc = frappe.new_doc("Item Price")
                item_price_doc.item_code = row.item_code
                item_price_doc.uom = row.uom
                item_price_doc.price_list_rate = price_list_rate
                item_price_doc.selling = 1
                item_price_doc.price_list = price_list
                item_price_doc.insert()

@frappe.whitelist()
def get_item_from_barcode(barcode):
    item_code = frappe.db.get_value("Item Barcode", {"barcode": barcode}, "parent")
    return item_code