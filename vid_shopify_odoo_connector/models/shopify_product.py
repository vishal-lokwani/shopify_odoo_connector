import logging
import json
import requests
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class ShopifyProduct(models.Model):
    _name = 'shopify.product'
    _description = 'Shopify Product'

    shopify_product_id = fields.Char(string="Shopify Product ID", required=True, index=True)
    shopify_variant_id = fields.Char(string="Shopify Variant ID", required=True, index=True)
    sku = fields.Char(string="SKU", index=True)
    title = fields.Char(string="Title")
    price = fields.Float(string="Price")
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    image_url = fields.Char(string="Image URL")

    # Extra standard Shopify fields
    product_type = fields.Char(string="Product Type")
    vendor = fields.Char(string="Vendor")
    tags = fields.Char(string="Tags")
    status = fields.Char(string="Status")
    handle = fields.Char(string="Handle")
    body_html = fields.Html(string="Product Description")
    created_at = fields.Datetime(string="Created At")
    updated_at = fields.Datetime(string="Updated At")
    
    # Store raw Shopify variant or product data for flexibility
    shopify_data = fields.Json(string="Raw Shopify Data")

    _sql_constraints = [
        ('unique_shopify_product_variant', 'unique(shopify_product_id, shopify_variant_id)', 'A Shopify Product Variant with this ID already exists!'),
    ]

    def _get_shopify_credentials(self):
        config = self.env['ir.config_parameter'].sudo()
        return {
            'store_url': config.get_param('shopify_odoo_connector.shopify_store_url'),
            'api_key': config.get_param('shopify_odoo_connector.shopify_api_key'),
        }

    def write(self, vals):
        result = super().write(vals)
        fields_triggering_sync = {'title', 'price', 'sku', 'body_html'}
        if any(field in vals for field in fields_triggering_sync):
            for record in self:
                record._push_update_to_shopify(vals)
        return result

    def _push_update_to_shopify(self, updated_vals):
        creds = self._get_shopify_credentials()
        if not creds['store_url'] or not creds['api_key']:
            _logger.warning("❌ Missing Shopify credentials. Sync skipped.")
            return

        domain = creds['store_url'].strip().replace("https://", "").replace("http://", "").strip("/")
        url = f"https://{domain}/admin/api/2023-10/products/{self.shopify_product_id}.json"

        product_data = {
            "id": int(self.shopify_product_id),
        }

        # Product-level fields
        if 'title' in updated_vals:
            product_data['title'] = self.title
        if 'body_html' in updated_vals:
            product_data['body_html'] = self.body_html
        if 'vendor' in updated_vals:
            product_data['vendor'] = self.vendor
        if 'product_type' in updated_vals:
            product_data['product_type'] = self.product_type
        if 'tags' in updated_vals:
            product_data['tags'] = self.tags
        if 'handle' in updated_vals:
            product_data['handle'] = self.handle
        if 'status' in updated_vals and self.status in ['active', 'draft', 'archived']:
            product_data['status'] = self.status

        # Variant-level fields
        variant_data = {
            "id": int(self.shopify_variant_id),
        }

        if 'price' in updated_vals:
            variant_data['price'] = str(self.price)  # Shopify expects price as string
        if 'sku' in updated_vals:
            variant_data['sku'] = self.sku

        product_data['variants'] = [variant_data]

        payload = {"product": product_data}
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": creds['api_key'],
        }

        try:
            response = requests.put(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            _logger.info(f"✅ Shopify product updated: {self.title} (ID: {self.shopify_product_id})")
        except requests.exceptions.RequestException as e:
            _logger.error(f"❌ Failed to update product in Shopify: {str(e)}")
            if response is not None:
                _logger.error(f"👉 Response content: {response.text}")
