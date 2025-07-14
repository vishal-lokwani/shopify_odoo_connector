from odoo import models, fields

class ShopifyOrderLine(models.Model):
    _name = 'shopify.order.line'
    _description = 'Shopify Order Line'

    order_id = fields.Many2one('shopify.order', string="Shopify Order", ondelete="cascade")
    title = fields.Char(string="Product Title")
    variant_title = fields.Char(string="Variant Title")
    quantity = fields.Integer(string="Quantity")
    price = fields.Float(string="Price")
    vendor = fields.Char(string="Vendor")
    sku = fields.Char(string="SKU")
    taxable = fields.Boolean(string="Taxable")
    requires_shipping = fields.Boolean(string="Requires Shipping")
    total_discount = fields.Float(string="Total Discount")
    properties = fields.Text(string="Properties (JSON)")
    tax_lines = fields.Text(string="Tax Lines (JSON)")