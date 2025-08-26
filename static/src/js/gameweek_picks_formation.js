/** @odoo-module */

import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class GameweekPicksFormation extends Component {
    static template = "fantasy_premier_league.GameweekPicksFormation";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        this.state = useState({
            gameweek_id: "",
            manager_id: "",
            gameweeks: [],
            managers: [],
            formation: {
                lineup_gkp: [],
                lineup_def: [],
                lineup_mid: [],
                lineup_fwd: [],
                sub_elements: [],
            },
            teamStats: null,
            playersData: {},
        });

        this.loadInitialData();
    }

    async loadInitialData() {
        try {
            // Load gameweeks
            const gameweeks = await this.orm.searchRead(
                "fpl.events",
                [],
                ["id", "name", "is_current"],
                { order: "event_id asc" }
            );
            this.state.gameweeks = gameweeks;

            // Load managers
            const managers = await this.orm.searchRead(
                "fpl.manager.team",
                [],
                ["id", "name","manager_id"],
            );
            this.state.managers = managers;

        } catch (error) {
            console.error("Error loading initial data:", error);
            this.notification.add(_t("Failed to load initial data"), { type: "danger" });
        }
    }

    async syncGameweekPicks() {
        if (!this.state.gameweek_id || !this.state.manager_id) {
            this.notification.add(_t("Please select both gameweek and manager"), { type: "warning" });
            return;
        }

        try {
            // Find the gameweek and manager objects
            const gameweek = this.state.gameweeks.find(gw => gw.id == this.state.gameweek_id);
            const manager = this.state.managers.find(m => m.id == this.state.manager_id);

            if (!gameweek || !manager) {
                this.notification.add(_t("Invalid gameweek or manager selection"), { type: "danger" });
                return;
            }

            // Call the sync method
            await this.orm.call("fpl.gameweek.pick.lines", "sync_gameweek_picks", [manager, gameweek]);

            // Load the formation data after sync
            await this.loadFormationData();

            this.notification.add(_t("Gameweek picks synced successfully"), { type: "success" });

        } catch (error) {
            console.error("Error syncing gameweek picks:", error);
            this.notification.add(_t("Failed to sync gameweek picks"), { type: "danger" });
        }
    }

    async loadFormationData() {
        if (!this.state.gameweek_id || !this.state.manager_id) {
            return;
        }

        try {
            // Find existing gameweek pick
            const gameweekPicks = await this.orm.searchRead(
                "fpl.gameweek.picks",
                [
                    ["manager_id", "=", parseInt(this.state.manager_id)],
                    ["event_id", "=", parseInt(this.state.gameweek_id)]
                ],
                ["id", "points", "total_points", "rank", "bank", "value", "event_transfers"]
            );

            if (gameweekPicks.length === 0) {
                this.notification.add(_t("No picks found for selected gameweek and manager"), { type: "info" });
                return;
            }

            const gameweekPick = gameweekPicks[0];

            // Load pick lines
            const pickLines = await this.orm.searchRead(
                "fpl.gameweek.pick.lines",
                [["gameweek_pick_id", "=", gameweekPick.id]],
                [
                    "id", "position", "multiplier", "is_captain", "is_vice_captain",
                    "element_id", "element_type_id", "team_id", "web_name", 
                    "plural_name_short", "team_name"
                ]
            );

            // Get formation using the _get_pick_formations method
            const pickData = pickLines.map(line => ({
                id: line.id,
                position: line.position,
                element_type_id: {
                    plural_name_short: line.plural_name_short
                }
            }));
            
            const formationResult = await this.orm.call(
                "fpl.gameweek.pick.lines",
                "get_pick_formations",
                [pickData]
            );

            // Store players data for quick lookup
            this.state.playersData = {};
            pickLines.forEach(line => {
                this.state.playersData[line.id] = {
                    name: line.web_name,
                    team: line.team_name,
                    position: line.plural_name_short,
                    multiplier: line.multiplier,
                    is_captain: line.is_captain,
                    is_vice_captain: line.is_vice_captain,
                };
            });

            // Update formation state
            this.state.formation = formationResult;
            this.state.teamStats = {
                points: gameweekPick.points,
                total_points: gameweekPick.total_points,
                rank: gameweekPick.rank.toLocaleString(),
                bank: gameweekPick.bank,
                value: gameweekPick.value,
                event_transfers: gameweekPick.event_transfers,
            };

        } catch (error) {
            console.error("Error loading formation data:", error);
            this.notification.add(_t("Failed to load formation data"), { type: "danger" });
        }
    }

    // Helper methods for template
    getPlayerName(playerId) {
        return this.state.playersData[playerId]?.name || "Unknown";
    }

    getPlayerTeam(playerId) {
        return this.state.playersData[playerId]?.team || "";
    }

    getPlayerPosition(playerId) {
        return this.state.playersData[playerId]?.position || "";
    }

    getPlayerMultiplier(playerId) {
        return this.state.playersData[playerId]?.multiplier || 1;
    }

    isPlayerCaptain(playerId) {
        return this.state.playersData[playerId]?.is_captain || false;
    }

    isPlayerViceCaptain(playerId) {
        return this.state.playersData[playerId]?.is_vice_captain || false;
    }
}