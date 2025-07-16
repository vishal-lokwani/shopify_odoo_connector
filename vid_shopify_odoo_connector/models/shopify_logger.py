from odoo import models, fields

class ShopifyLogger(models.Model):
    _name = 'shopify.logger'
    _description = 'Shopify API Log'

    name = fields.Char(string="Log Title")
    log_type = fields.Selection([('info', 'Info'), ('error', 'Error')], default='info')
    message = fields.Text(string="Message")
    record_id = fields.Integer(string="Record ID")
    timestamp = fields.Datetime(string="Timestamp", default=fields.Datetime.now)
