from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    check_credit = fields.Boolean(string="Check Credit")
    credit_limit = fields.Float(string="Credit Limit")
    credit_limit_on_hold = fields.Boolean(string="Credit Limit on hold")
