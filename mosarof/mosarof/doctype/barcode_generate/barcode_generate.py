# Copyright (c) 2025, market and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BarcodeGenerate(Document):
	pass

@frappe.whitelist()
def item_barcode(item_barcode):
    parent_item = frappe.db.get_value("Item Barcode", {"barcode": item_barcode}, "parent")
    return parent_item
