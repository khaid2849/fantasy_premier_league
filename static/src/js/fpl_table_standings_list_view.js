/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

class FplTableStandingsListController extends ListController {
    setup() {
        super.setup();
        this.searchBarToggler.state.showSearchBar = false;
        this.orm = useService("orm");
        this.notification = useService("notification");

        // Refresh from the live Premier League standings/team-form APIs
        // every time this menu is opened, since fpl.teams's own standings
        // fields are no longer kept current by the FPL API sync.
        this.syncStandings();
    }

    async syncStandings() {
        try {
            await this.orm.call("fpl.table.standings", "action_sync_standings", []);
            await this.model.load();
        } catch (error) {
            console.error("Error syncing table standings:", error);
            this.notification.add(
                _t("Failed to refresh live standings - showing the last known data."),
                { type: "warning" }
            );
        }
    }
}

const FplTableStandingsListView = {
    ...listView,
    Controller: FplTableStandingsListController,
};

registry.category("views").add("fpl_table_standings_list_view", FplTableStandingsListView);
