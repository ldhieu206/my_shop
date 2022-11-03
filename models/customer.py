from odoo import models, fields, api


class Customer(models.Model):
    _name = 'my_shop.customer'
    _description = 'My Shop Customer'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email', required=True)
    image = fields.Binary(string='Image')
    phone = fields.Char(string='Phone', required=True)
    address = fields.Text(string='Address', required=True)
    customer_count = fields.Integer(string='Customer Count')
    order_ids = fields.One2many('my_shop.order', 'customer_id', string='Orders')
    order_line_ids = fields.One2many('my_shop.order_line', 'customer_id', string='Order Lines')
    sold = fields.Float(string='Sold', compute='_compute_sold')

    @api.model
    def customer_count(self):
        self.customer_count = len(self.order_ids)


