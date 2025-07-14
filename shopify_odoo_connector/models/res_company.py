from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    shopify_default_sales_team_id = fields.Many2one('crm.team', string="Shopify Sales Team")
    shopify_default_payment_method = fields.Many2one('account.payment.method', string="Shopify Payment Method")
    shopify_default_shipping_method = fields.Many2one('delivery.carrier', string="Shopify Shipping Method")
