import logging
import requests
import json
from dateutil.parser import isoparse
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    shopify_store_url = fields.Char(
        string='Shopify Store URL',
        config_parameter='shopify_odoo_connector.shopify_store_url')

    shopify_api_key = fields.Char(
        string='Shopify API Key',
        config_parameter='shopify_odoo_connector.shopify_api_key')

    shopify_password = fields.Char(
        string='Shopify Password',
        config_parameter='shopify_odoo_connector.shopify_password')

    shopify_shared_secret = fields.Char(
        string='Shopify Shared Secret',
        config_parameter='shopify_odoo_connector.shopify_shared_secret')

    shopify_default_sales_team_id = fields.Many2one(
        'crm.team',
        string='Default Sales Team',
        related='company_id.shopify_default_sales_team_id',
        readonly=False)

    shopify_default_payment_method = fields.Many2one(
        'account.payment.method',
        string='Default Payment Method',
        related='company_id.shopify_default_payment_method',
        readonly=False)

    shopify_default_shipping_method = fields.Many2one(
        'delivery.carrier',
        string='Default Shipping Method',
        related='company_id.shopify_default_shipping_method',
        readonly=False)

    sync_products = fields.Boolean(string="Sync Products", config_parameter='shopify.sync_products')
    sync_orders = fields.Boolean(string="Sync Orders", config_parameter='shopify.sync_orders')
    sync_customers = fields.Boolean(string="Sync Customers", config_parameter='shopify.sync_customers')
    
    def action_test_connection(self):

        self.ensure_one()

        if not self.shopify_store_url or not self.shopify_api_key:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Missing Credentials',
                    'message': 'Please fill in both the Shopify Store URL and API Access Token.',
                    'type': 'danger',
                    'sticky': False,
                }
            }

        try:
            # Clean the store URL
            domain = self.shopify_store_url.strip().replace("https://", "").replace("http://", "").strip("/")

            url = f"https://{domain}/admin/api/unstable/graphql.json"
            headers = {
                "Content-Type": "application/json",
                "X-Shopify-Access-Token": self.shopify_api_key.strip()
            }
            query = {
                "query": "{ shop { name } }"
            }

            response = requests.post(url, headers=headers, data=json.dumps(query), timeout=10)

            if response.status_code == 200:
                data = response.json()
                shop_name = data.get("data", {}).get("shop", {}).get("name", "Unknown")
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': '✅ Shopify Connected',
                        'message': f'Successfully connected to Shopify store: {shop_name}',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': '❌ Shopify Connection Failed',
                        'message': f"Failed with status {response.status_code}: {response.text}",
                        'type': 'danger',
                        'sticky': True,
                    }
                }

        except requests.exceptions.RequestException as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Connection Error',
                    'message': f'Exception occurred: {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }
    def action_sync_shopify_products(self):
        self.ensure_one()

        if not self.shopify_store_url or not self.shopify_api_key:
            raise UserError("Missing Shopify credentials.")

        domain = self.shopify_store_url.strip().replace("https://", "").replace("http://", "").strip("/")
        url = f"https://{domain}/admin/api/2023-10/products.json"
        headers = {
            "X-Shopify-Access-Token": self.shopify_api_key.strip(),
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            _logger.info("Shopify API success: %s", response.text)
        except requests.exceptions.RequestException as e:
            _logger.error("Shopify API error: %s", str(e))
            raise UserError(f"Error during Shopify API call: {e}")

        products = response.json().get('products', [])
        Product = self.env['product.product'].sudo()
        ShopifyProduct = self.env['shopify.product'].sudo()

        synced_count = 0

        for product in products:
            # Extract common product-level fields
            product_id = str(product.get('id'))
            product_type = product.get('product_type', '')
            vendor = product.get('vendor', '')
            tags = product.get('tags', '')
            status = product.get('status', '')
            handle = product.get('handle', '')
            body_html = product.get('body_html', '')
            created_at_str = product.get('created_at')
            updated_at_str = product.get('updated_at')
            created_at = isoparse(created_at_str).replace(tzinfo=None) if created_at_str else False
            updated_at = isoparse(updated_at_str).replace(tzinfo=None) if updated_at_str else False
            image = product.get('image') or {}
            image_url = image.get('src', '')

            for variant in product.get('variants', []):
                sku = variant.get('sku') or str(variant.get('id'))
                price = float(variant.get('price', 0))
                variant_id = str(variant.get('id'))
                title = product.get('title') or variant.get('title')            

                # Prepare values
                values = {
                    'shopify_product_id': product_id,
                    'shopify_variant_id': variant_id,
                    'sku': sku,
                    'title': title,
                    'price': price,
                    'image_url': image_url,
                    'product_type': product_type,
                    'vendor': vendor,
                    'tags': tags,
                    'status': status,
                    'handle': handle,
                    'body_html': body_html,
                    'created_at': created_at,
                    'updated_at': updated_at,
                    'shopify_data': variant  # You could merge product + variant if needed
                }

                # Create or update Shopify product mapping
                mapping = ShopifyProduct.search([('shopify_variant_id', '=', variant_id)], limit=1)
                if mapping:
                    mapping.write(values)
                else:
                    ShopifyProduct.create(values)

                synced_count += 1    

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '✅ Product Sync Complete',
                'message': f'{synced_count} Shopify product variants synced successfully!',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_sync_shopify_customers(self):
        self.ensure_one()

        if not self.shopify_store_url or not self.shopify_api_key:
            raise UserError("Missing Shopify credentials.")

        domain = self.shopify_store_url.strip().replace("https://", "").replace("http://", "").strip("/")
        url = f"https://{domain}/admin/api/2023-10/customers.json"
        headers = {
            "X-Shopify-Access-Token": self.shopify_api_key.strip(),
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise UserError(f"Shopify API Error: {e}")

        customers = response.json().get('customers', [])
        ShopifyCustomer = self.env['shopify.customer'].sudo()
        Partner = self.env['res.partner'].sudo()
        created_count = 0

        for customer in customers:
            shopify_id = str(customer.get('id'))
            email = customer.get('email')
            first = customer.get('first_name') or ''
            last = customer.get('last_name') or ''
            name = f"{first} {last}".strip() or email or 'Unnamed Customer'
            phone = customer.get('phone')

            address = customer.get('default_address') or {}
            city = address.get('city')
            country_name = address.get('country')
            province = address.get('province')
            zip_code = address.get('zip')
            address1 = address.get('address1')
            address2 = address.get('address2')

            # Resolve country
            country = self.env['res.country'].search([('name', '=', country_name)], limit=1)

            # Still create or update partner if needed (optional)
            if email:
                partner = Partner.search([('email', '=', email)], limit=1)
                if not partner:
                    Partner.create({
                        'name': name,
                        'email': email,
                        'phone': phone,
                        'city': city,
                        'country_id': country.id if country else False,
                        'customer_rank': 1
                    })

            values = {
                'shopify_customer_id': shopify_id,
                'name': name,
                'email': email,
                'phone': phone,
                'city': city,
                'province': province,
                'country': country_name,
                'zip_code': zip_code,
                'address1': address1,
                'address2': address2,
                'tags': customer.get('tags'),
                'state': customer.get('state'),
                'verified_email': customer.get('verified_email', False),
                'total_spent': float(customer.get('total_spent', 0.0)),
                'orders_count': int(customer.get('orders_count', 0)),
                'customer_since': isoparse(customer.get('created_at')).replace(tzinfo=None) if customer.get('created_at') else False,
                'updated_at': isoparse(customer.get('updated_at')).replace(tzinfo=None) if customer.get('updated_at') else False,
                'shopify_data': customer,
            }

            existing = ShopifyCustomer.search([('shopify_customer_id', '=', shopify_id)], limit=1)
            if existing:
                existing.write(values)
            else:
                ShopifyCustomer.create(values)
                created_count += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '✅ Customer Sync Complete',
                'message': f'{created_count} new customers synced!',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_sync_shopify_orders(self):
        self.ensure_one()

        if not self.shopify_store_url or not self.shopify_api_key:
            raise UserError("Missing Shopify credentials.")

        domain = self.shopify_store_url.strip().replace("https://", "").replace("http://", "").strip("/")
        url = f"https://{domain}/admin/api/2024-01/orders.json?status=any"
        headers = {
            'Content-Type': 'application/json',
            'X-Shopify-Access-Token': self.shopify_api_key.strip(),
        }

        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise UserError(f"Failed to sync Shopify orders: {e}")

        orders = response.json().get('orders', [])
        OrderModel = self.env['shopify.order'].sudo()
        LineModel = self.env['shopify.order.line'].sudo()

        created = 0
        for order in orders:
            shopify_order_id = str(order.get('id'))
            existing = OrderModel.search([('shopify_order_id', '=', shopify_order_id)], limit=1)
    
            shipping_address = order.get('shipping_address', {}) or {}
            billing_address = order.get('billing_address', {}) or {}
            customer = order.get('customer') or {}
            fulfillments = order.get('fulfillments', [])
            tracking_number = ''
            carrier = ''

            if fulfillments:
                fulfillment = fulfillments[0]
                tracking_number = fulfillment.get('tracking_number', '')
                carrier = fulfillment.get('tracking_company', '')

            values = {
                'shopify_order_id': shopify_order_id,
                'name': order.get('name'),
                'email': order.get('email'),
                'customer_name': f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip(),
                'total_price': float(order.get('total_price', 0.0)),
                'subtotal_price': float(order.get('subtotal_price', 0.0)),
                'shipping_price': float(order.get('total_shipping_price_set', {}).get('shop_money', {}).get('amount', 0.0)),
                'currency': order.get('currency'),
                'financial_status': order.get('financial_status'),
                'fulfillment_status': order.get('fulfillment_status'),
                'order_date': isoparse(order.get('created_at')).replace(tzinfo=None) if order.get('created_at') else False,
                'processed_at': isoparse(order.get('processed_at')).replace(tzinfo=None) if order.get('processed_at') else False,
                'tags': order.get('tags'),

                # Raw data
                'total_discount': float(order.get('total_discounts', 0.0)),

                # Parsed shipping address fields
                'shipping_name': shipping_address.get('name'),
                'shipping_phone': shipping_address.get('phone'),
                'shipping_address1': shipping_address.get('address1'),
                'shipping_address2': shipping_address.get('address2'),
                'shipping_city': shipping_address.get('city'),
                'shipping_zip': shipping_address.get('zip'),
                'shipping_province': shipping_address.get('province'),
                'shipping_country': shipping_address.get('country'),
                'shipping_company': shipping_address.get('company'),
                'shipping_tracking_number': tracking_number,
                'shipping_carrier': carrier,
                'billing_name': billing_address.get('name'),
                'billing_phone': billing_address.get('phone'),
                'billing_company': billing_address.get('company'),
                'billing_address1': billing_address.get('address1'),
                'billing_address2': billing_address.get('address2'),
                'billing_city': billing_address.get('city'),
                'billing_zip': billing_address.get('zip'),
                'billing_province': billing_address.get('province'),
                'billing_country': billing_address.get('country'),
            }

            if existing:
                existing.write(values)
                existing.order_lines.unlink()
                order_record = existing
            else:
                order_record = OrderModel.create(values)
                created += 1

            # Create line items
            line_vals = []
            for line in order.get('line_items', []):
                line_vals.append((0, 0, {
                    'title': line.get('title'),
                    'variant_title': line.get('variant_title'),
                    'quantity': line.get('quantity'),
                    'price': float(line.get('price', 0.0)),
                    'vendor': line.get('vendor'),
                    'sku': line.get('sku'),
                    'taxable': line.get('taxable'),
                    'requires_shipping': line.get('requires_shipping'),
                    'total_discount': float(line.get('total_discount', 0.0)),
                    'properties': json.dumps(line.get('properties', []), indent=2),
                    'tax_lines': json.dumps(line.get('tax_lines', []), indent=2),
                }))

            order_record.write({'order_lines': line_vals})

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '✅ Order Sync Complete',
                'message': f'{created} new Shopify orders synced successfully!',
                'type': 'success',
                'sticky': False,
            }
        }
