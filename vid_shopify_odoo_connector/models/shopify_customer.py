from odoo import models, fields


class ShopifyCustomer(models.Model):
    _name = 'shopify.customer'
    _description = 'Shopify Customer'

    shopify_customer_id = fields.Char(string="Shopify Customer ID", required=True, index=True)
    name = fields.Char(string="Customer Name")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    city = fields.Char(string="City")
    province = fields.Char(string="Province/State")
    country = fields.Char(string="Country")
    zip_code = fields.Char(string="ZIP/Postal Code")
    address1 = fields.Char(string="Address Line 1")
    address2 = fields.Char(string="Address Line 2")
    customer_since = fields.Datetime(string="Created At")
    updated_at = fields.Datetime(string="Updated At")
    tags = fields.Char(string="Tags")
    verified_email = fields.Boolean(string="Verified Email")
    state = fields.Selection([
        ('enabled', 'Enabled'),
        ('disabled', 'Disabled'),
        ('invited', 'Invited'),
        ('declined', 'Declined')
    ], string="State")
    total_spent = fields.Float(string="Total Spent")
    orders_count = fields.Integer(string="Orders Count")

    odoo_partner_id = fields.Many2one('res.partner', string="Linked Odoo Partner", ondelete='set null')

    shopify_data = fields.Json(string="Raw Shopify Customer Data")  # Store full raw data

    _sql_constraints = [
        ('unique_shopify_customer_id', 'unique(shopify_customer_id)', 'This Shopify Customer ID already exists!')
    ]
