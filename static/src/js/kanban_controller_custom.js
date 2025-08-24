/** @odoo-module **/
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { registry } from "@web/core/registry";
import { kanbanView } from "@web/views/kanban/kanban_view";

class FplkanbanViewCustomControllerHideSearch extends KanbanController {
  setup() {
    super.setup();
    this.searchBarToggler.state.showSearchBar = false;
  }
}

const FplkanbanViewCustom = {
  ...kanbanView,
  Controller: KanbanController,
};

const FplkanbanViewCustomHideSearch = {
  ...kanbanView,
  Controller: FplkanbanViewCustomControllerHideSearch,
};

registry.category("views").add("fpl_kanban_view_custom", FplkanbanViewCustom);
registry
  .category("views")
  .add("fpl_kanban_view_custom_hide_search", FplkanbanViewCustomHideSearch);

export default FplkanbanViewCustom;
