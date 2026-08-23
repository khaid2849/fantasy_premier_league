/** @odoo-module **/
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { registry } from "@web/core/registry";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { onWillDestroy } from "@odoo/owl";

const FIXTURES_LIVE_CHANNEL = "fantasy_premier_league.fixtures_live";
const FIXTURES_LIVE_NOTIFICATION = "fpl.fixtures/update";

class FplkanbanViewCustomControllerHideSearch extends KanbanController {
  setup() {
    super.setup();
    this.searchBarToggler.state.showSearchBar = false;

    // Live scoreboard: reload as soon as the fixtures cron pushes an
    // update, instead of waiting for the user to manually refresh.
    this.busService = this.env.services.bus_service;
    this.onFixturesUpdate = () => this.model.load();
    this.busService.subscribe(FIXTURES_LIVE_NOTIFICATION, this.onFixturesUpdate);
    this.busService.addChannel(FIXTURES_LIVE_CHANNEL);

    onWillDestroy(() => {
      this.busService.unsubscribe(FIXTURES_LIVE_NOTIFICATION, this.onFixturesUpdate);
      this.busService.deleteChannel(FIXTURES_LIVE_CHANNEL);
    });
  }
}

const FplkanbanViewCustomHideSearch = {
  ...kanbanView,
  Controller: FplkanbanViewCustomControllerHideSearch,
};

registry
  .category("views")
  .add("fpl_kanban_view_custom_hide_search", FplkanbanViewCustomHideSearch);

