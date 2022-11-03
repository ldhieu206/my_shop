from odoo import models, fields, api


class Product(models.Model):
    _name = 'my_shop.product'
    _description = 'My Shop Product'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    price = fields.Float(string='Price', required=True)
    image = fields.Binary(string='Image')
    product_count = fields.Integer(string='Product Count')
    category_id = fields.Many2one('my_shop.category', string='Category')
    priority = fields.Selection([('1', 'Low'), ('2', 'Medium'), ('3', 'High')], string='Priority', default='1')
    sold = fields.Integer(string='Sold', default=0)


class Category(models.Model):
    _name = 'my_shop.category'
    _description = 'My Shop Category'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
