/** @odoo-module **/
/**
 * Widget repair_remaining_days
 * Étend remaining_days pour ne pas colorier en rouge les ordres
 * dont le statut est « done » (Réparé) ou « cancel » (Annulé).
 */
import { registry } from "@web/core/registry";
import {
    RemainingDaysField,
    remainingDaysField,
} from "@web/views/fields/remaining_days/remaining_days_field";

class RepairRemainingDaysField extends RemainingDaysField {
    get classNames() {
        const state = this.props.record.data["state"];
        if (state === "done" || state === "cancel") {
            return null; // aucune couleur pour les ordres terminés/annulés
        }
        return super.classNames;
    }
}

registry.category("fields").add("repair_remaining_days", {
    ...remainingDaysField,
    component: RepairRemainingDaysField,
});
