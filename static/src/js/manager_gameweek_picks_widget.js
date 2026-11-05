/** @odoo-module */

import { onWillUpdateProps } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";
import { GameweekPicksFormation } from "./gameweek_picks_formation";

/**
 * "Gameweek Picks" tab of the manager team form: the formation of the record's manager,
 * on the current gameweek by default, with a selector to look back at past gameweeks.
 */
export class ManagerGameweekPicks extends GameweekPicksFormation {
    static template = "fantasy_premier_league.ManagerGameweekPicks";
    static props = { ...standardWidgetProps };

    setup() {
        super.setup();
        Object.assign(this.state, { loaded: false });
        this.loadToken = 0;

        onWillUpdateProps((nextProps) => {
            // The pager moved to another manager: show its team on the same gameweek
            if (nextProps.record.resId !== this.props.record.resId) {
                this.state.manager_id = nextProps.record.resId;
                this.loadGameweek();
            }
        });
    }

    async loadInitialData() {
        this.state.manager_id = this.props.record.resId;
        try {
            // Only the gameweeks of the season that have already started can have picks
            this.state.gameweeks = await this.orm.searchRead(
                "fpl.events",
                [
                    ["is_current_season", "=", true],
                    "|", "|", ["finished", "=", true], ["is_current", "=", true], ["is_previous", "=", true],
                ],
                ["id", "name", "is_current", "finished", "event_id"],
                { order: "event_id desc" }
            );
        } catch {
            this.notification.add(_t("Failed to load gameweeks"), { type: "danger" });
            return;
        }
        const current = this.state.gameweeks.find((gw) => gw.is_current) || this.state.gameweeks[0];
        if (current) {
            this.state.gameweek_id = current.id;
            await this.loadGameweek();
        } else {
            this.state.loaded = true;
        }
    }

    onGameweekChange(ev) {
        this.state.gameweek_id = parseInt(ev.target.value);
        this.loadGameweek();
    }

    /**
     * Show the picks of the selected gameweek. The server only calls the FPL API when the
     * gameweek data can still change (or on an explicit refresh).
     */
    async loadGameweek({ forceSync = false } = {}) {
        if (!this.state.gameweek_id || !this.state.manager_id) {
            return;
        }
        const token = ++this.loadToken;
        this.state.loading = true;
        this.resetFormation();
        try {
            const data = await this.fetchPitchData(this.state.manager_id, this.state.gameweek_id, forceSync);
            if (token === this.loadToken) {
                this.applyPitchData(data);
            }
        } catch (error) {
            if (token === this.loadToken) {
                this.notification.add(error.data?.message || error.message, {
                    title: _t("Could not get gameweek picks"),
                    type: "danger",
                });
            }
        } finally {
            if (token === this.loadToken) {
                this.state.loading = false;
                this.state.loaded = true;
            }
        }
    }

    get hasPicks() {
        return Object.keys(this.state.playersData).length > 0;
    }
}

registry.category("view_widgets").add("fpl_manager_gameweek_picks", {
    component: ManagerGameweekPicks,
});
