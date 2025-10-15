
import frappe

def add_custom_barcode_to_child(doc, method):
    """Always barcode to Barcodes child table"""
    if doc.custom_custom_barcode:
        doc.append("barcodes", {"barcode": doc.custom_custom_barcode})
