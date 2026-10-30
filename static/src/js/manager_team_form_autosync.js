/** @odoo-module */
import { FormController } from "@web/views/form/form_controller";
import { formView } from "@web/views/form/form_view";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { useEffect, useState } from "@odoo/owl";

export class ManagerTeamFormAutoSyncController extends FormController {
    setup() {
        super.setup();
        this.notification = useService("notification");
        this.syncState = useState({ loading: false });
        this.syncToken = 0;

        // Runs on the first open and whenever the pager switches to another record
        useEffect(
            (resId) => {
                if (resId) {
                    this.syncManagerData(resId);
                }
            },
            () => [this.model.root.resId]
        );
    }

    async syncManagerData(resId) {
        const token = ++this.syncToken;
        this.syncState.loading = true;
        try {
            const warning = await this.orm.call(this.props.resModel, "action_sync_on_open", [[resId]]);
            // The user may have moved to another record meanwhile: only the latest sync updates the view
            if (token !== this.syncToken || this.model.root.resId !== resId) {
                return;
            }
            await this.model.root.load();
            if (warning) {
                this.notification.add(warning, { type: "warning" });
            }
        } catch (error) {
            if (token === this.syncToken) {
                const message = error.data?.message || error.message;
                this.notification.add(message, {
                    title: _t("Could not sync manager data"),
                    type: "danger",
                });
            }
        } finally {
            if (token === this.syncToken) {
                this.syncState.loading = false;
            }
        }
    }
}
ManagerTeamFormAutoSyncController.template = "fantasy_premier_league.ManagerTeamFormAutoSync";

registry.category("views").add("fpl_manager_team_form_autosync", {
    ...formView,
    Controller: ManagerTeamFormAutoSyncController,
});
