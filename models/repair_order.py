# Copyright 2024 Garage Auto SaaS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class RepairOrder(models.Model):
    _inherit = "repair.order"

    # ── Véhicule ──────────────────────────────────────────────────────────────
    vehicle_id = fields.Many2one(
        comodel_name="garage.vehicle",
        string="Véhicule",
        tracking=True,
        index=True,
        ondelete="restrict",
    )
    mileage_in = fields.Integer(
        string="Km à l'entrée",
        tracking=True,
    )
    mileage_out = fields.Integer(
        string="Km à la sortie",
        tracking=True,
    )
    fuel_level = fields.Selection(
        selection=[
            ("empty", "Vide"),
            ("quarter", "1/4"),
            ("half", "1/2"),
            ("three_quarters", "3/4"),
            ("full", "Plein"),
        ],
        string="Niveau carburant",
        default="quarter",
    )
    date_checkin = fields.Datetime(
        string="Date d'entrée",
        default=fields.Datetime.now,
    )
    date_checkout = fields.Datetime(
        string="Date de sortie",
    )

    vehicle_brand_id = fields.Many2one(
        comodel_name="garage.vehicle.brand",
        related="vehicle_id.brand_id",
        string="Marque du véhicule",
        readonly=True,
    )
    schedule_date_only = fields.Date(
        string="Date planifiée",
        compute="_compute_schedule_date_only",
    )

    # Force l'ordre des colonnes kanban (draft → confirmed → under_repair → done → cancel)
    state = fields.Selection(group_expand="_group_expand_states")

    # Date planifiée : par défaut J+1
    schedule_date = fields.Datetime(
        default=lambda self: fields.Datetime.now() + timedelta(days=1),
    )

    # ── Retour atelier (comeback) ─────────────────────────────────────────────
    repair_origin_id = fields.Many2one(
        comodel_name="repair.order",
        string="Réparation d'origine",
        ondelete="set null",
        copy=False,
        index=True,
        help="Ordre de réparation initial dont découle ce retour atelier.",
    )
    comeback_count = fields.Integer(
        string="Retours atelier",
        compute="_compute_comeback_count",
    )

    # ── Diagnostic ────────────────────────────────────────────────────────────
    customer_complaint = fields.Text(
        string="Plainte client",
        help="Description du problème signalé par le client.",
    )
    diagnosis_notes = fields.Text(
        string="Diagnostic technicien",
        help="Observations et conclusions du technicien.",
    )
    estimated_completion = fields.Datetime(
        string="Fin estimée",
    )

    # ── Facturation (computed) ────────────────────────────────────────────────
    invoice_ids = fields.Many2many(
        comodel_name="account.move",
        string="Liste factures",
        compute="_compute_invoice_stats",
    )
    invoice_count = fields.Integer(
        string="Factures",
        compute="_compute_invoice_stats",
    )
    invoice_state = fields.Char(
        string="État facturation",
        compute="_compute_invoice_stats",
    )


    # ── Devise (relatée depuis la société) ───────────────────────────────────
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="company_id.currency_id",
        string="Devise",
        store=True,
        readonly=True,
    )

    # ── Totaux (computed) ─────────────────────────────────────────────────────
    labor_total = fields.Monetary(
        string="Total main-d'œuvre",
        compute="_compute_totals",
        currency_field="currency_id",
    )
    parts_total = fields.Monetary(
        string="Total pièces",
        compute="_compute_totals",
        currency_field="currency_id",
    )

    # ── Onchange ──────────────────────────────────────────────────────────────
    @api.onchange("vehicle_id")
    def _onchange_vehicle_id(self):
        if not self.vehicle_id:
            return
        vehicle = self.vehicle_id
        # Auto-fill client
        if vehicle.partner_id:
            self.partner_id = vehicle.partner_id
        # Auto-fill kilométrage
        if vehicle.mileage:
            self.mileage_in = vehicle.mileage
        # Auto-fill produit générique "VEHICULE" si aucun produit sélectionné
        if not self.product_id:
            product = self.env.ref(
                "repair_auto.product_vehicle_generic", raise_if_not_found=False
            )
            if product:
                self.product_id = product.product_variant_id

    # ── Calculs facturation ───────────────────────────────────────────────────
    def _compute_invoice_stats(self):
        for rec in self:
            # Les factures liées via sale_order_id → account.move
            invoices = self.env["account.move"]
            if rec.sale_order_id:
                invoices = rec.sale_order_id.invoice_ids
            rec.invoice_ids = invoices
            rec.invoice_count = len(invoices)
            if not invoices:
                rec.invoice_state = _("Non facturé")
            elif all(inv.payment_state == "paid" for inv in invoices):
                rec.invoice_state = _("Payé")
            elif any(inv.state == "posted" for inv in invoices):
                rec.invoice_state = _("Facturé")
            else:
                rec.invoice_state = _("Brouillon")

    # ── Calculs totaux ────────────────────────────────────────────────────────
    def _compute_totals(self):
        for rec in self:
            # Main-d'œuvre = lignes de service (repair_service OCA)
            labor = 0.0
            if hasattr(rec, "service_ids"):
                labor = sum(
                    line.price_subtotal
                    for line in rec.service_ids
                )
            # Pièces = mouvements de type "add"
            parts = sum(
                move.product_id.standard_price * move.product_uom_qty
                for move in rec.move_ids.filtered(
                    lambda m: m.repair_line_type == "add"
                )
            )
            rec.labor_total = labor
            rec.parts_total = parts

    # ── Actions ───────────────────────────────────────────────────────────────
    def action_view_invoices(self):
        self.ensure_one()
        if not self.invoice_ids:
            raise UserError(_("Aucune facture associée à cet ordre de réparation."))
        action = {
            "type": "ir.actions.act_window",
            "name": _("Factures"),
            "res_model": "account.move",
            "view_mode": "list,form",
            "domain": [("id", "in", self.invoice_ids.ids)],
        }
        if len(self.invoice_ids) == 1:
            action.update(
                {
                    "view_mode": "form",
                    "res_id": self.invoice_ids.id,
                }
            )
        return action

    # ── Override action_repair_done ───────────────────────────────────────────
    def action_repair_done(self):
        result = super().action_repair_done()
        for rec in self:
            if rec.vehicle_id:
                # Mettre à jour le kilométrage du véhicule
                if rec.mileage_out and rec.mileage_out > (rec.vehicle_id.mileage or 0):
                    rec.vehicle_id.mileage = rec.mileage_out
                # Dater la restitution
                if not rec.date_checkout:
                    rec.date_checkout = fields.Datetime.now()
        return result

    # ── Kanban column ordering ────────────────────────────────────────────────
    @api.model
    def _group_expand_states(self, states, domain):
        """Force les colonnes kanban dans l'ordre du workflow."""
        return ["draft", "confirmed", "under_repair", "done", "cancel"]

    def _compute_comeback_count(self):
        for rec in self:
            rec.comeback_count = self.search_count([("repair_origin_id", "=", rec.id)])

    def action_view_comebacks(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Retours atelier",
            "res_model": "repair.order",
            "view_mode": "list,form",
            "domain": [("repair_origin_id", "=", self.id)],
            "context": {"default_repair_origin_id": self.id},
        }

    @api.depends("schedule_date")
    def _compute_schedule_date_only(self):
        for rec in self:
            rec.schedule_date_only = rec.schedule_date.date() if rec.schedule_date else False
