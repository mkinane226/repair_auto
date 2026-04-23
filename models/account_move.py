# Copyright 2024 Garage Auto SaaS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    repair_vehicle_ids = fields.Many2many(
        comodel_name="garage.vehicle",
        string="Véhicules réparés",
        compute="_compute_repair_vehicle_ids",
        store=False,
    )

    @api.depends("invoice_line_ids")
    def _compute_repair_vehicle_ids(self):
        for move in self:
            if not move.id:
                move.repair_vehicle_ids = False
                continue
            # Étape 1 : devis liés à cette facture
            sale_orders = self.env["sale.order"].search(
                [("invoice_ids", "in", move.ids)]
            )
            if not sale_orders:
                move.repair_vehicle_ids = False
                continue
            # Étape 2 : ordres de réparation liés à ces devis
            repairs = self.env["repair.order"].search(
                [("sale_order_id", "in", sale_orders.ids)]
            )
            move.repair_vehicle_ids = repairs.mapped("vehicle_id").filtered(bool)
