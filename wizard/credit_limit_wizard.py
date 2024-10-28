from odoo import fields, models, api


class CreditLimitWizard(models.TransientModel):
    _name = "credit.limit.wizard"
    _description = "Credit Limit Details"
    _inherit = ["mail.thread", 'mail.activity.mixin']

    manager_id = fields.Many2one("res.users")
    order_id = fields.Many2one("sale.order")
    customer_id = fields.Many2one("res.partner", string="Customer")
    credit_limit = fields.Float(string="Credit Limit")
    is_on_hold = fields.Boolean(string="Credit Limit on hold")

    total_receivable = fields.Float(string="Total Receivable")
    sale_orders = fields.Char(string="Sale Orders")
    invoices = fields.Char(string="Invoices")
    current_quotation = fields.Float(string="Current Quotation")
    exceeded_amt = fields.Float(string="Exceeded Amount")

    @api.model
    def default_get(self, fields_list):
        res = super(CreditLimitWizard, self).default_get(fields_list)
        order_id_id = self.env.context.get("default_order_id")
        order_id = self.env["sale.order"].browse(order_id_id)
        customer_id = order_id.partner_id.id
        credit_limit = order_id.partner_id.credit_limit
        is_on_hold = order_id.partner_id.credit_limit_on_hold

        total_receivable = order_id.amount_total

        pending_so = self.env["sale.order"].search([("state", "=", 'draft')])
        sale_order_worth = sum(pending_so.mapped("amount_total"))
        no_of_pending_so = self.env["sale.order"].search_count([("state", "=", 'draft')])
        sale_orders = f"{no_of_pending_so} Sales Order Worth: {sale_order_worth}"

        pending_inv = self.env["account.move"].search([("state", "=", 'draft')])
        inv_worth = sum(pending_inv.mapped("amount_total_signed"))
        no_of_pending_inv = self.env["account.move"].search_count([("state", "=", 'draft')])
        invoices = f"{no_of_pending_inv} Draft Invoice Worth: {inv_worth}"

        current_quotation = order_id.amount_total
        exceeded_amt = total_receivable + sale_order_worth + inv_worth + current_quotation - credit_limit

        # taking manager id
        manager_id = self.env["res.users"].search([
            ("groups_id", "in", self.env.ref("customer_credit_limit.group_credit_limit_manager").id)
        ], limit=1)

        res.update({
            "manager_id": manager_id.id,
            "order_id": order_id_id,
            "customer_id": customer_id,
            "credit_limit": credit_limit,
            "is_on_hold": is_on_hold,
            "total_receivable": total_receivable,
            "sale_orders": sale_orders,
            "invoices": invoices,
            "current_quotation": current_quotation,
            "exceeded_amt": exceeded_amt,
        })
        print(manager_id, "++++++++++++")
        return res

    def action_snd_request(self):
        # sending approval request to manager of the user
        self.order_id.state = "credit"
        template = self.env.ref('customer_credit_limit.email_template_credit_limit_request', raise_if_not_found=True)
        template.send_mail(self, email_layout_xmlid='mail.mail_notification_light', force_send=True)
