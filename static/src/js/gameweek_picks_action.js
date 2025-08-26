/** @odoo-module */

import { registry } from "@web/core/registry";
import { GameweekPicksFormation } from "./gameweek_picks_formation";

// Register the client action
registry.category("actions").add("fantasy_premier_league.gameweek_picks_formation", GameweekPicksFormation);