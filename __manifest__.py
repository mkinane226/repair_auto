{
    'name': 'Repair Auto — Gestion de garage',
    'version': '18.0.1.0.0',
    'category': 'Manufacturing/Repair',
    'summary': 'Gestion professionnelle de garage automobile — étend les ordres de réparation',
    'description': """
Repair Auto
===========
Module professionnel SaaS pour les garages automobiles.
Étend les ordres de réparation natifs d'Odoo 18 avec :

* Fiche véhicule (immatriculation, VIN, marque, modèle, énergie, kilométrage)
* Lien véhicule ↔ ordre de réparation avec historique complet
* Réception / restitution (km entrée/sortie, niveau carburant)
* Plainte client et notes de diagnostic
* Rapport d'intervention PDF professionnel
* Configuration par garage (immatriculation obligatoire, SMS…)
    """,
    'author': 'Garage Auto SaaS',
    'website': 'https://github.com/',
    'license': 'LGPL-3',
    'depends': [
        'repair',
        'repair_service',
        'repair_order_template',
        'base_repair_config',
        'repair_type',
        'repair_stock',
        'mail',
    ],
    'data': [
        'security/garage_security.xml',
        'security/ir.model.access.csv',
        'data/product_data.xml',
        'data/repair_tags_data.xml',
        'data/mail_templates.xml',
        'views/garage_vehicle_views.xml',
        'views/repair_order_views.xml',
        'views/repair_kanban_views.xml',
        'views/res_config_settings_views.xml',
        'views/menu_views.xml',
        'report/repair_order_report.xml',
        'report/repair_order_template.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
    'images': ['static/description/banner.png'],
}
