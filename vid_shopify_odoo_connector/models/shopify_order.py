from odoo import models, fields


class ShopifyOrder(models.Model):
    _name = 'shopify.order'
    _description = 'Shopify Order'

    shopify_order_id = fields.Char(string="Shopify Order ID", required=True, index=True)
    name = fields.Char(string="Order Name")
    email = fields.Char(string="Customer Email")
    customer_name = fields.Char(string="Customer Name")
    total_price = fields.Float(string="Total Price")
    subtotal_price = fields.Float(string="Subtotal Price")
    shipping_price = fields.Float(string="Shipping Price")
    currency = fields.Char(string="Currency")
    financial_status = fields.Char(string="Financial Status")
    fulfillment_status = fields.Char(string="Fulfillment Status")
    order_date = fields.Datetime(string="Order Date")
    processed_at = fields.Datetime(string="Processed At")
    tags = fields.Char(string="Tags")
    total_discount = fields.Float(string="Total Discount")

    # Raw JSON fields (optional)
    line_items = fields.Text(string="Line Items (Raw JSON)")
    
    # Shipping address - parsed fields
    shipping_name = fields.Char(string="Shipping Name")
    shipping_phone = fields.Char(string="Shipping Phone")
    shipping_company = fields.Char(string="Company")
    shipping_address1 = fields.Char(string="Address Line 1")
    shipping_address2 = fields.Char(string="Address Line 2")
    shipping_city = fields.Char(string="City")
    shipping_province = fields.Char(string="State/Province")
    shipping_zip = fields.Char(string="ZIP")
    shipping_country = fields.Char(string="Country")
    shipping_tracking_number = fields.Char(string="Tracking Number")
    shipping_carrier = fields.Char(string="Shipping Carrier")
    # Parsed Billing Address Fields
    billing_name = fields.Char(string="Billing Name")
    billing_phone = fields.Char(string="Billing Phone")
    billing_company = fields.Char(string="Billing Company")
    billing_address1 = fields.Char(string="Billing Address Line 1")
    billing_address2 = fields.Char(string="Billing Address Line 2")
    billing_city = fields.Char(string="Billing City")
    billing_zip = fields.Char(string="Billing ZIP")
    billing_province = fields.Char(string="Billing State/Province")
    billing_country = fields.Char(string="Billing Country")

    order_lines = fields.One2many('shopify.order.line', 'order_id', string="Order Line Items")

    _sql_constraints = [
        ('unique_shopify_order_id', 'unique(shopify_order_id)', 'This Shopify Order ID already exists!')
    ]
