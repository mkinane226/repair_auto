# Copyright 2024 Garage Auto SaaS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    garage_require_vehicle = fields.Boolean(
        string="Immatriculation obligatoire",
        config_parameter="garage.require_vehicle",
        help="Rendre le champ véhicule obligatoire sur les ordres de réparation.",
    )
    garage_require_mileage = fields.Boolean(
        string="Kilométrage obligatoire à l'entrée",
        config_parameter="garage.require_mileage",
        help="Obliger la saisie du kilométrage lors de la prise en charge.",
    )
    garage_sms_notifications = fields.Boolean(
        string="Notifications SMS client",
        config_parameter="garage.sms_notifications",
        help="Envoyer des SMS automatiques au client (confirmation, livraison).",
    )
    garage_auto_close_on_payment = fields.Boolean(
        string="Clôture automatique après paiement",
        config_parameter="garage.auto_close_on_payment",
        help="Marquer l'ordre terminé dès que la facture est payée.",
    )
