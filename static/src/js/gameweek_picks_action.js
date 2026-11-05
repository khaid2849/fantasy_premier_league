/** @odoo-module */

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { FplPicksBoard } from "./gameweek_picks_board";

/** "Gameweek Picks" menu: the picks board with a manager selector. */
export class FplGameweekPicksAction extends Component {
    static template = "fantasy_premier_league.GameweekPicksAction";
    static components = { FplPicksBoard };
    static props = ["*"];
}

registry.category("actions").add("fantasy_premier_league.gameweek_picks_formation", FplGameweekPicksAction);
