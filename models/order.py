from odoo import models, fields, api


class Order(models.Model):
    _name = 'my_shop.order'
    _description = 'My Shop Order'
    _rec_name = 'code'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    code = fields.Char(string='Code', default=lambda self: self._generate_code(), required=True)
    customer_id = fields.Many2one('my_shop.customer', string='Customer')
    order_date = fields.Date(string='Date Order', required=True, default=fields.Date.today())
    total = fields.Float(string='Total', compute='_compute_total')
    order_line_ids = fields.One2many('my_shop.order_line', 'order_id', string='Order Lines')
    #     state order
    state = fields.Selection([('1', 'Pending'), ('2', 'In Progress'), ('3', 'Done'), ('4', 'Cancel')], string='State',
                             default='1')
    cancel_reason = fields.Text(string='Cancel Reason')

    # generate code ascending
    @api.model
    def _generate_code(self):
        last_code = self.search([], order='id desc', limit=1)
        if last_code:
            return 'ORD' + str(int(last_code.code[3:]) + 1).zfill(4)
        else:
            return 'ORD0001'

    @api.depends('order_line_ids')
    def _compute_total(self):
        for record in self:
            total = 0
            for line in record.order_line_ids:
                total += line.sub_total
            record.total = total

    def action_pending(self):
        self.state = '1'

    def action_in_progress(self):
        self.state = '2'

    def action_done(self):
        self.state = '3'
        for record in self:
            for line in record.order_line_ids:
                line.product_id.sold += line.quantity
                line.product_id.product_count -= line.quantity

    def action_cancel(self):
        action = self.env.ref('my_shop.action_cancel_order').read()[0]
        action['context'] = {
            'default_order_id': self.id,
        }
        return action

    def action_view_order(self):
        return {
            'name': 'Order',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'my_shop.order',
            'res_id': self.id,
            'target': 'current',
        }

    def send_email(self):
        template = self.env.ref('my_shop.email_template_order')
        template.send_mail(self.id, force_send=True)


class OrderLine(models.Model):
    _name = 'my_shop.order_line'
    _description = 'My Shop Order Line'

    order_id = fields.Many2one('my_shop.order', string='Order')
    product_id = fields.Many2one('my_shop.product', string='Product')
    quantity = fields.Integer(string='Quantity', required=True)
    price = fields.Float(string='Price', required=True)
    sub_total = fields.Float(string='Sub Total', compute='_compute_sub_total')
    customer_id = fields.Many2one('my_shop.customer', string='Customer', related='order_id.customer_id')

    @api.depends('quantity', 'price')
    def _compute_sub_total(self):
        for record in self:
            record.sub_total = record.quantity * record.price

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.price = self.product_id.price

    @api.onchange('action_view_order')
    def action_view_order(self):
        return {
            'name': 'Orders',
            'type': 'ir.actions.act_window',
            'res_model': 'my_shop.order',
            'view_mode': 'tree,form',
            'domain': [('customer_id', '=', self.customer_id)]
        }


class CancelOrder(models.TransientModel):
    _name = 'my_shop.cancel_order.wizard'
    _description = 'My Shop Cancel Order'

    reason = fields.Text(string='Reason', required=True)
    order_id = fields.Many2one('my_shop.order', string='Order')

    def action_cancel_order(self):
        for record in self:
            record.order_id.state = '4'
            record.order_id.cancel_reason = record.reason
            record.order_id.order_line_ids.product_id.product_count += record.order_id.order_line_ids.quantity
            warning = {
                'title': 'Cancel Order',
                'message': 'Order has been canceled',
            }
            return {'warning': warning}
