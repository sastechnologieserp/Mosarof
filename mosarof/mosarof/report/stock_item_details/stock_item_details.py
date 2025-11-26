# Copyright (c) 2025, market and contributors
# For license information, please see license.txt

# import frappe


import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data()
    return columns, data


def get_columns():
    return [
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link","options" : "Item" ,"width": 150},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": "Barcode", "fieldname": "barcode", "fieldtype": "Data", "width": 150},
        {"label": "Purchase Price", "fieldname": "purchase_price", "fieldtype": "Currency", "width": 120},
        {"label": "Valuation Rate", "fieldname": "valuation_rate", "fieldtype": "Currency", "width": 120},
        {"label": "Selling Price", "fieldname": "selling_price", "fieldtype": "Currency", "width": 120},
         {"label": "Available Quantity", "fieldname": "actual_qty", "fieldtype": "Float", "width": 120},
        {"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Data", "width": 150},     
    ]


def get_data():
    query = """
        SELECT
            i.item_code AS item_code,
            i.item_name AS item_name,
            i.custom_barcode AS barcode,

            (
                SELECT ip.price_list_rate
                FROM `tabItem Price` ip
                WHERE ip.item_code = i.item_code
                  AND ip.price_list = 'Standard Buying'
                ORDER BY ip.creation DESC
                LIMIT 1
            ) AS purchase_price,

            b.valuation_rate AS valuation_rate,

            (
                SELECT ip.price_list_rate
                FROM `tabItem Price` ip
                WHERE ip.item_code = i.item_code
                  AND ip.price_list = 'Retail price Br2'
                ORDER BY ip.creation DESC
                LIMIT 1
            ) AS selling_price,

            b.warehouse AS warehouse,
            b.actual_qty AS actual_qty

        FROM
            `tabItem` i
        LEFT JOIN
            `tabBin` b ON b.item_code = i.item_code
        ORDER BY
            i.item_code, b.warehouse
    """

    data = frappe.db.sql(query, as_dict=True)
    return data

