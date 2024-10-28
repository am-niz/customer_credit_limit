from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    state = fields.Selection(
        selection_add=[('credit', 'Credit Limit')]
    )

    def action_confirm(self):
        for rec in self:
            total = rec.amount_total  # checking the total amount of current quotation
            if total > rec.partner_id.credit_limit and not self.env.user.has_group("customer_credit_limit.group_credit_limit_manager"):
                # if total amount quotation greater than credit limit and current user is not manger, then display wizard
                return {
                    "name": "Credit Limit Details",
                    "type": "ir.actions.act_window",
                    "res_model": "credit.limit.wizard",
                    "view_mode": "form",
                    "context": {"default_order_id": rec.id},
                    "target": "new",
                }
            else:
                return super(SaleOrder, self).action_confirm()
