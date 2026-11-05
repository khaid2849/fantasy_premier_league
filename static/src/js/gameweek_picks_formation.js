/** @odoo-module */

import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export function emptyFormation() {
    return {
        lineup_gkp: [],
        lineup_def: [],
        lineup_mid: [],
        lineup_fwd: [],
        sub_elements: [],
    };
}

/**
 * "Gameweek Picks" client action: pick a manager and a gameweek, and show the
 * squad on a pitch. All the data comes from a single RPC
 * (fpl.gameweek.picks/get_gameweek_picks_data), which also decides whether
 * the FPL API needs to be called.
 */
export class GameweekPicksFormation extends Component {
    static template = "fantasy_premier_league.GameweekPicksFormation";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        this.state = useState({
            gameweek_id: "",
            manager_id: "",
            gameweeks: [],
            managers: [],
            loading: false,
            formation: emptyFormation(),
            teamStats: null,
            playersData: {},
        });

        this.loadInitialData();
    }

    async loadInitialData() {
        try {
            const [gameweeks, managers] = await Promise.all([
                this.orm.searchRead(
                    "fpl.events",
                    [["is_current_season", "=", true]],
                    ["id", "name", "is_current", "finished", "event_id"],
                    { order: "event_id asc" }
                ),
                this.orm.searchRead("fpl.manager.team", [], ["id", "name", "manager_id"]),
            ]);
            this.state.gameweeks = gameweeks;
            this.state.managers = managers;
            const current = gameweeks.find((gw) => gw.is_current);
            if (current) {
                this.state.gameweek_id = String(current.id);
            }
            if (managers.length === 1) {
                this.state.manager_id = String(managers[0].id);
            }
        } catch {
            this.notification.add(_t("Failed to load initial data"), { type: "danger" });
        }
    }

    /**
     * Fetch the pitch data of a manager/gameweek and display it.
     *
     * @returns {Promise<boolean>} whether picks were found
     */
    async fetchPitchData(managerId, gameweekId, forceSync = false) {
        return this.orm.call(
            "fpl.gameweek.picks",
            "get_gameweek_picks_data",
            [parseInt(managerId), parseInt(gameweekId)],
            { force_sync: forceSync }
        );
    }

    applyPitchData(data) {
        if (!data || !data.found) {
            this.resetFormation();
            return false;
        }
        this.state.formation = data.formation;
        this.state.playersData = data.players;
        this.state.teamStats = {
            ...data.stats,
            rank: (data.stats.rank || 0).toLocaleString(),
        };
        return true;
    }

    resetFormation() {
        this.state.teamStats = null;
        this.state.playersData = {};
        this.state.formation = emptyFormation();
    }

    async syncGameweekPicks() {
        if (!this.state.gameweek_id || !this.state.manager_id) {
            this.notification.add(_t("Please select both gameweek and manager"), { type: "warning" });
            return;
        }
        this.state.loading = true;
        try {
            const data = await this.fetchPitchData(this.state.manager_id, this.state.gameweek_id, true);
            if (this.applyPitchData(data)) {
                this.notification.add(_t("Gameweek picks synced successfully"), { type: "success" });
            } else {
                this.notification.add(_t("No picks found for selected gameweek and manager"), { type: "info" });
            }
        } catch (error) {
            this.notification.add(error.data?.message || error.message || _t("Failed to sync gameweek picks"), {
                title: _t("Could not get gameweek picks"),
                type: "danger",
            });
        } finally {
            this.state.loading = false;
        }
    }

    async openPlayerStats(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        const pickLineId = parseInt(ev.currentTarget.dataset.playerId);
        const action = await this.orm.call("fpl.gameweek.pick.lines", "action_open_player_stats", [pickLineId]);
        if (action) {
            this.action.doAction(action);
        }
    }

    getPlayer(playerId) {
        return this.state.playersData[playerId] || {};
    }

    getTotalPoints(playerId) {
        return this.getPlayer(playerId).total_points || 0;
    }

    getTeamcode(playerId) {
        return this.getPlayer(playerId).team_code || "";
    }

    getTeamId(playerId) {
        return this.getPlayer(playerId).team_id || 0;
    }

    getPlayerName(playerId) {
        return this.getPlayer(playerId).name || _t("Unknown");
    }

    getPlayerTeam(playerId) {
        return this.getPlayer(playerId).team || "";
    }

    getPlayerPosition(playerId) {
        return this.getPlayer(playerId).position || "";
    }

    getPlayerMultiplier(playerId) {
        return this.getPlayer(playerId).multiplier ?? 1;
    }

    isPlayerCaptain(playerId) {
        return Boolean(this.getPlayer(playerId).is_captain);
    }

    isPlayerViceCaptain(playerId) {
        return Boolean(this.getPlayer(playerId).is_vice_captain);
    }
}
