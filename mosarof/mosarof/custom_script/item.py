
import frappe

def add_custom_barcode_to_child(doc, method):
    """Always barcode to Barcodes child table"""
    if doc.custom_barcode:
        doc.append("barcodes", {"barcode": doc.custom_barcode})

def create_opening_stock_entry(doc, method):
    
    if not doc.is_stock_item:
        return

    # Only run if Opening Stock and Warehouse are set
    if doc.opening_stock and doc.custom_warehouse:
        opening_qty = doc.opening_stock

        # Get default warehouse from Item Defaults
        default_warehouse = frappe.db.get_value(
            "Item Default", {"parent": doc.name}, "default_warehouse"
        )

        # Check if transfer already exists
        existing_entry = frappe.db.exists("Stock Entry", {
            "stock_entry_type": "Material Transfer",
            "item_code": doc.name
        })
        if existing_entry:
            return

        # Create Material Transfer from default warehouse to selected custom warehouse
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.stock_entry_type = "Material Transfer"
        stock_entry.purpose = "Material Transfer"

        stock_entry.append("items", {
            "item_code": doc.name,
            "qty": opening_qty,
            "s_warehouse": default_warehouse,
            "t_warehouse": doc.custom_warehouse,
            "basic_rate": doc.valuation_rate or 0
        })

        stock_entry.insert(ignore_permissions=True)
        stock_entry.submit()

