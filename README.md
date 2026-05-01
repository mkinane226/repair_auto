# repair_auto — Gestion de garage automobile

Module Odoo 18 professionnel pour les garages automobiles.  
Extension du module natif `repair` (OCA) avec fiche véhicule, réception/restitution, diagnostic, et rapports PDF d'intervention.

---

## Fonctionnalités

- **Fiche véhicule** — immatriculation, VIN, marque, modèle, année, couleur, énergie, kilométrage, photo
- **Réception / restitution** — km entrée/sortie, niveau carburant, dates check-in/check-out
- **Plainte client & diagnostic technicien** — champs dédiés sur l'ordre de réparation
- **Retour atelier** — lien vers la réparation d'origine, compteur de retours
- **Facturation** — smart button factures, état de paiement calculé
- **Rapport d'intervention PDF** — en-tête véhicule, liste pièces + MO, totaux
- **Bloc véhicule sur factures et devis** — affiché automatiquement sur les PDF
- **Vue kanban** — colonnes par statut avec logo marque, km, niveau carburant
- **Configuration** — immatriculation obligatoire, kilométrage obligatoire, SMS, clôture auto

---

## Compatibilité

| | |
|---|---|
| Odoo | 18.0 Community |
| Licence | LGPL-3 |
| Catégorie | Manufacturing/Repair |

---

## Dépendances

### Modules OCA (dossier `my-addons/repair/`)

- `repair` — module OCA de base
- `repair_service` — lignes de service (main-d'œuvre)
- `repair_order_template` — modèles d'ordre
- `base_repair_config` — configuration de base
- `repair_type` — types de réparation
- `repair_stock` — gestion des pièces/mouvements de stock

### Modules Odoo natifs

`mail`, `sale`, `account`, `spreadsheet_dashboard`, `utm`

---

## Installation

1. Cloner ce dépôt dans votre dossier `addons` ou `my-addons`
2. S'assurer que tous les modules OCA `repair` listés ci-dessus sont disponibles
3. Mettre à jour la liste des modules dans les paramètres Odoo
4. Installer `repair_auto`

### Avec Docker (dev)

```powershell
docker compose stop odoo

docker run --rm --network odoo-180_default \
  -v "./my-addons/repair:/mnt/extra-addons/repair:ro" \
  -v "./my-addons:/mnt/extra-addons/my-addons:ro" \
  -v "./config:/etc/odoo:ro" \
  -v "odoo-180_odoo-web-data:/var/lib/odoo" \
  odoo:18.0 odoo \
  -d odoo-dev --db_host=db --db_user=odoo --db_password=odoo \
  -u repair_auto --stop-after-init --no-http

docker compose start odoo
```

---

## Structure du module

```
repair_auto/
├── models/
│   ├── garage_vehicle.py        # Modèle garage.vehicle
│   ├── garage_vehicle_brand.py  # Modèle garage.vehicle.brand
│   ├── repair_order.py          # Héritage repair.order
│   ├── account_move.py          # Héritage account.move
│   ├── sale_order.py            # Héritage sale.order
│   └── res_config_settings.py   # Paramètres de configuration
├── views/
│   ├── garage_vehicle_views.xml
│   ├── repair_order_views.xml
│   ├── repair_kanban_views.xml
│   └── menu_views.xml
├── report/
│   ├── repair_order_template.xml   # Rapport d'intervention
│   └── report_invoice_vehicle.xml  # Bloc véhicule sur factures/devis
├── security/
│   ├── garage_security.xml         # Groupes Technicien / Responsable
│   └── ir.model.access.csv
├── data/
│   ├── garage_vehicle_brands_data.xml  # Marques pré-chargées
│   ├── repair_tags_data.xml
│   └── mail_templates.xml
└── static/src/
    ├── js/
    │   ├── repair_remaining_days_field.js  # Widget dates sans rouge sur done/cancel
    │   ├── kanban_brand_logo.js             # Logo marque en kanban
    │   └── color_selection_field.js         # Sélecteur couleur avec aperçu visuel
    └── img/
        └── repair_icon.png                  # Icône du menu
```

---

## Modèles

### `garage.vehicle`

Fiche véhicule cliente du garage.

| Champ | Description |
|---|---|
| `license_plate` | Immatriculation (requis) |
| `vin` | Numéro de châssis (VIN, 17 car.) |
| `partner_id` | Client propriétaire |
| `brand_id` | Marque (modèle structuré avec logo) |
| `modele` | Modèle du véhicule |
| `annee` | Année |
| `couleur` | Couleur (liste + saisie libre si "Autre") |
| `energie` | Essence / Diesel / Électrique / Hybride / GPL / Hydrogène |
| `mileage` | Kilométrage actuel (mis à jour à la clôture) |
| `repair_ids` | Historique des interventions |

### `repair.order` (extension)

| Champ | Description |
|---|---|
| `vehicle_id` | Véhicule lié (auto-remplit client et km) |
| `mileage_in` / `mileage_out` | Km entrée/sortie |
| `fuel_level` | Niveau carburant |
| `date_checkin` | Date d'entrée atelier |
| `schedule_date` | Date planifiée (défaut : J+1) |
| `customer_complaint` | Plainte client |
| `diagnosis_notes` | Diagnostic technicien |
| `repair_origin_id` | Réparation d'origine (retour atelier) |
| `invoice_count` / `invoice_state` | Suivi facturation |

---

## Sécurité

| Groupe | Accès |
|---|---|
| `garage_group_user` (Technicien) | Lecture + écriture véhicules et ordres |
| `garage_group_manager` (Responsable) | + configuration + suppression |

---

## Licence

[LGPL-3](https://www.gnu.org/licenses/lgpl-3.0.html) — Garage Auto SaaS
