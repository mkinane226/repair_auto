# Copyright 2024 Garage Auto SaaS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    repair_vehicle_ids = fields.Many2many(
        comodel_name="garage.vehicle",
        string="Véhicule(s) en réparation",
        compute="_compute_repair_vehicle_ids",
        store=False,
    )
    repair_vehicle_info = fields.Char(
        string="Kilométrage",
        compute="_compute_repair_vehicle_info",
        store=False,
    )

    @api.depends("order_line")
    def _compute_repair_vehicle_ids(self):
        for order in self:
            if not order.id:
                order.repair_vehicle_ids = False
                continue
            repairs = self.env["repair.order"].search(
                [("sale_order_id", "=", order.id)]
            )
            order.repair_vehicle_ids = repairs.mapped("vehicle_id").filtered(bool)

    @api.depends("order_line")
    def _compute_repair_vehicle_info(self):
        for order in self:
            vehicles = order.repair_vehicle_ids
            mileages = [
                "%s km" % "{:,}".format(v.mileage).replace(",", "\u202f")
                for v in vehicles if v.mileage
            ]
            order.repair_vehicle_info = "  |  ".join(mileages) if mileages else False
