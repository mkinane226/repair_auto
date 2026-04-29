# Copyright 2024 Garage Auto SaaS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import fields, models


class GarageVehicleBrand(models.Model):
    _name = "garage.vehicle.brand"
    _description = "Marque de véhicule"
    _order = "name"

    name = fields.Char(string="Marque", required=True)
    image_128 = fields.Image(
        string="Logo",
        max_width=128,
        max_height=128,
    )
