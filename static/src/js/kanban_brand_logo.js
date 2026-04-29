/** @odoo-module **/

import { KanbanHeader } from "@web/views/kanban/kanban_header";
import { patch } from "@web/core/utils/patch";
import { useState, onWillStart } from "@odoo/owl";

/**
 * Extends the KanbanHeader component to display a brand logo (40px height)
 * to the left of the group title when the kanban is grouped by `brand_id`.
 */
patch(KanbanHeader.prototype, {
    setup() {
        super.setup();
        this._brandLogo = useState({ src: null });

        onWillStart(async () => {
            const { groupByField, value } = this.props.group;
            if (groupByField.name === "brand_id" && value) {
                try {
                    const [record] = await this.orm.silent.read(
                        "garage.vehicle.brand",
                        [value],
                        ["image_128"]
                    );
                    if (record && record.image_128) {
                        this._brandLogo.src = `data:image/png;base64,${record.image_128}`;
                    }
                } catch {
                    // silently ignore errors (access rights, missing record, …)
                }
            }
        });
    },

    get brandLogoSrc() {
        return this._brandLogo.src;
    },
});
