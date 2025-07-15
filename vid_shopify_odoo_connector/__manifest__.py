{
    "name": "Shopify Odoo Connector",
    "version": "1.0.0",
    "category": "Connector",
    "summary": "Connect your Shopify store with Odoo",
    "author": "Your Company",
    "website": "https://yourcompany.com",
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
