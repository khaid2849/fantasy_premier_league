/** @odoo-module */

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";
import { FplPicksBoard } from "./gameweek_picks_board";

/** "Gameweek Picks" tab of the manager team form: the picks board of the record's manager. */
export class ManagerGameweekPicks extends Component {
    static template = "fantasy_premier_league.ManagerGameweekPicks";
    static components = { FplPicksBoard };
    static props = { ...standardWidgetProps };
}

registry.category("view_widgets").add("fpl_manager_gameweek_picks", {
    component: ManagerGameweekPicks,
});
