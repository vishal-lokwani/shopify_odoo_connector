{
    "name": "Shopify Odoo Connector",
    "version": "1.0.0",
    "category": "Connector",
    "summary": "Connect your Shopify store with Odoo",
    "author": "Vidhema Technologies",
    "website": "https://www.vidhema.com",
     'description': """<div class="container">
    <h1>Shopify-Odoo Connector Module</h1>

    <div class="section">
      <p>This module provides seamless integration between your Shopify store and Odoo ERP system. It enables automatic synchronization of key eCommerce data, streamlining your operations and centralizing management within Odoo.</p>
    </div>

    <div class="section">
      <h2>Key Features</h2>
      <ul>
        <li><strong>Product Synchronization</strong>
          <ul>
            <li>Create and update Shopify products directly from Odoo.</li>
            <li>Sync product details including title, description, price, stock, and images.</li>
          </ul>
        </li>
        <li><strong>Customer Synchronization</strong>
          <ul>
            <li>Automatically import Shopify customers into Odoo.</li>
            <li>Maintain up-to-date customer information across platforms.</li>
          </ul>
        </li>
        <li><strong>Order Synchronization</strong>
          <ul>
            <li>Import Shopify orders in real-time into Odoo Sales.</li>
            <li>Track order status and fulfillment updates within Odoo.</li>
          </ul>
        </li>
        <li><strong>Bidirectional Updates (optional)</strong>
          <ul>
            <li>Push product updates from Odoo to Shopify.</li>
            <li>Fetch orders and customer data from Shopify into Odoo.</li>
          </ul>
        </li>
      </ul>
    </div>

    <div class="section">
      <h2>Benefits</h2>
      <ul>
        <li>Centralized product and order management</li>
        <li>Reduced manual data entry and errors</li>
        <li>Improved workflow automation between platforms</li>
        <li>Enhanced visibility of Shopify operations within Odoo</li>
      </ul>
    </div>

    <div class="section">
      <h2>Ideal For</h2>
      <p>Businesses that manage inventory, sales, and customer data in Odoo and want real-time synchronization with their Shopify storefront.</p>
    </div>
  </div>""",
    "depends": ["base", "sale_management", "stock", "account","delivery"],
    'images': ['static/description/icon.png'],
    "data": [
        'security/ir.model.access.csv',
        'views/config_settings_view.xml',
        'views/shopify_product_views.xml',
        'views/shopify_customer_views.xml',
        'views/shopify_order_views.xml',
        'views/shopify_menus.xml',
    ],
    "assets": {
        'web.assets_backend': [
        'shopify_odoo_connector/static/src/img/logo.png',  # optional for preloading
    ],
    },
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
