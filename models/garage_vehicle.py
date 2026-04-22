# Copyright 2024 Garage Auto SaaS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class GarageVehicle(models.Model):
    _name = "garage.vehicle"
    _description = "Véhicule du garage"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "license_plate"
    _rec_name = "display_name"

    # ── Identification ──────────────────────────────────────────────────────
    license_plate = fields.Char(
        string="Immatriculation",
        required=True,
        tracking=True,
        index=True,
    )
    vin = fields.Char(
        string="N° VIN",
        index=True,
        copy=False,
        tracking=True,
        help="Numéro d'identification du véhicule (17 caractères)",
    )
    display_name = fields.Char(
        string="Nom",
        compute="_compute_display_name",
        store=True,
    )

    # ── Client ───────────────────────────────────────────────────────────────
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Client",
        required=True,
        index=True,
        tracking=True,
        ondelete="restrict",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Société",
        default=lambda self: self.env.company,
        index=True,
    )

    # ── Caractéristiques ─────────────────────────────────────────────────────
    marque = fields.Char(string="Marque", required=True, tracking=True)
    modele = fields.Char(string="Modèle", required=True, tracking=True)
    annee = fields.Integer(string="Année", tracking=True)
    couleur = fields.Char(string="Couleur", tracking=True)
    energie = fields.Selection(
        selection=[
            ("gasoline", "Essence"),
            ("diesel", "Diesel"),
            ("electric", "Électrique"),
            ("hybrid", "Hybride"),
            ("lpg", "GPL"),
            ("hydrogen", "Hydrogène"),
        ],
        string="Énergie",
        tracking=True,
    )
    mileage = fields.Integer(
        string="Kilométrage actuel",
        tracking=True,
        help="Mis à jour automatiquement à la clôture d'une réparation.",
    )
    image_128 = fields.Image(
        string="Photo",
        max_width=128,
        max_height=128,
    )
    note = fields.Html(string="Notes internes")
    active = fields.Boolean(string="Actif", default=True)

    # ── Liens réparations ─────────────────────────────────────────────────────
    repair_ids = fields.One2many(
        comodel_name="repair.order",
        inverse_name="vehicle_id",
        string="Réparations",
    )
    repair_count = fields.Integer(
        string="Nb réparations",
        compute="_compute_repair_stats",
        store=True,
    )
    last_repair_date = fields.Datetime(
        string="Dernière réparation",
        compute="_compute_repair_stats",
        store=True,
    )

    # ── Calculs ───────────────────────────────────────────────────────────────
    @api.depends("marque", "modele", "license_plate")
    def _compute_display_name(self):
        for rec in self:
            parts = [rec.marque, rec.modele, rec.license_plate]
            rec.display_name = " — ".join(p for p in parts if p)

    @api.depends("repair_ids", "repair_ids.state", "repair_ids.date_checkin")
    def _compute_repair_stats(self):
        for rec in self:
            done = rec.repair_ids.filtered(lambda r: r.state == "done")
            rec.repair_count = len(rec.repair_ids)
            rec.last_repair_date = max(done.mapped("date_checkin"), default=False)

    # ── Contraintes ───────────────────────────────────────────────────────────
    @api.constrains("vin")
    def _check_vin(self):
        for rec in self:
            if not rec.vin:
                continue
            vin = rec.vin.strip().upper()
            if len(vin) != 17:
                raise ValidationError(
                    _("Le VIN doit contenir exactement 17 caractères (actuel : %d).")
                    % len(vin)
                )
            duplicate = self.search(
                [("vin", "=", vin), ("id", "!=", rec.id)], limit=1
            )
            if duplicate:
                raise ValidationError(
                    _("Le VIN « %s » est déjà utilisé par le véhicule %s.")
                    % (vin, duplicate.display_name)
                )

    # ── Actions ───────────────────────────────────────────────────────────────
    def action_view_repairs(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Réparations — %s") % self.display_name,
            "res_model": "repair.order",
            "view_mode": "list,form",
            "domain": [("vehicle_id", "=", self.id)],
            "context": {"default_vehicle_id": self.id},
        }
