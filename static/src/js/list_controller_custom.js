/** @odoo-module **/
import { ListController } from "@web/views/list/list_controller";
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";


class FplListViewCustomControllerHideSearch extends ListController {
  setup() {
    super.setup();
    this.searchBarToggler.state.showSearchBar = false;
    
  }
}

const FplListViewCustom = {
    ...listView,
    Controller: ListController,
};

const FplListViewCustomHideSearch = {
    ...listView,
    Controller: FplListViewCustomControllerHideSearch,
};

registry.category("views").add("fpl_list_view_custom", FplListViewCustom);
registry.category("views").add("fpl_list_view_custom_hide_search", FplListViewCustomHideSearch);

export default FplListViewCustom;