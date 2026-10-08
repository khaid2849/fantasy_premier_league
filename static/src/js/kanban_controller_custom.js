/** @odoo-module **/
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { registry } from "@web/core/registry";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { onMounted, onWillDestroy } from "@odoo/owl";

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

class FplKanbanRendererScrollToOpenGroup extends KanbanRenderer {
  setup() {
    super.setup();
    // Bring the unfolded gameweek (nearest upcoming one) into view on open,
    // instead of making the user scroll right to find e.g. GW38.
    onMounted(() => {
      const openGroup = this.rootRef.el?.querySelector(".o_kanban_group:not(.o_column_folded)");
      openGroup?.scrollIntoView({ inline: "start", block: "nearest" });
    });
  }
}

const FplkanbanViewCustomHideSearch = {
  ...kanbanView,
  Controller: FplkanbanViewCustomControllerHideSearch,
  Renderer: FplKanbanRendererScrollToOpenGroup,
};

registry
  .category("views")
  .add("fpl_kanban_view_custom_hide_search", FplkanbanViewCustomHideSearch);

