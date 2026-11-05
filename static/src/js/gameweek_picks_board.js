/** @odoo-module */

import { Component, onMounted, onWillStart, onWillUnmount, onWillUpdateProps, useState } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";
import { deserializeDateTime } from "@web/core/l10n/dates";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";

const { DateTime } = luxon;

// The server re-syncs a live gameweek at most once a minute
const LIVE_REFRESH_DELAY = 60000;

/**
 * Squad of a manager for a gameweek, on a pitch: summary of the gameweek,
 * starting XI, bench and the details of the selected player.
 *
 * Used by the "Gameweek Picks" menu (with a manager selector) and by the tab
 * of the manager form (fixed manager). All the data comes from a single RPC
 * (fpl.gameweek.picks/get_gameweek_picks_data), which also decides whether
 * the FPL API needs to be called.
 */
export class FplPicksBoard extends Component {
    static template = "fantasy_premier_league.PicksBoard";
    static props = {
        managerId: { type: [Number, Boolean], optional: true },
        selectManager: { type: Boolean, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        this.state = useState({
            managers: [],
            managerId: this.props.managerId || false,
            gameweeks: [],
            gameweekId: false,
            data: null,
            selectedId: false,
            loading: false,
            loaded: false,
        });
        this.loadToken = 0;
        this.refreshTimer = null;

        onWillStart(() => this.loadInitialData());
        onMounted(() => this.loadGameweek());
        onWillUpdateProps((nextProps) => {
            // The pager of the manager form moved to another manager: same gameweek
            if (nextProps.managerId !== this.props.managerId) {
                this.state.managerId = nextProps.managerId || false;
                this.state.selectedId = false;
                this.loadGameweek();
            }
        });
        onWillUnmount(() => this.clearRefresh());
    }

    // ------------------------------------------------------------------
    // Data loading
    // ------------------------------------------------------------------

    async loadInitialData() {
        try {
            const [gameweeks, managers] = await Promise.all([
                // Only the gameweeks that have already started can have picks
                this.orm.searchRead(
                    "fpl.events",
                    [
                        ["is_current_season", "=", true],
                        "|", "|", ["finished", "=", true], ["is_current", "=", true], ["is_previous", "=", true],
                    ],
                    ["id", "name", "event_id", "is_current"],
                    { order: "event_id asc" }
                ),
                this.props.selectManager
                    ? this.orm.searchRead("fpl.manager.team", [], ["id", "name"], { order: "name" })
                    : Promise.resolve([]),
            ]);
            this.state.gameweeks = gameweeks;
            this.state.managers = managers;
            const current = gameweeks.find((gw) => gw.is_current) || gameweeks.at(-1);
            this.state.gameweekId = current ? current.id : false;
            if (!this.state.managerId && managers.length) {
                this.state.managerId = managers[0].id;
            }
        } catch (error) {
            this.notifyError(error, _t("Failed to load the gameweeks"));
        }
    }

    /**
     * Show the picks of the selected manager and gameweek.
     *
     * @param {Object} [options]
     * @param {boolean} [options.forceSync] call the FPL API even if the data is recent
     * @param {boolean} [options.silent] background refresh: keep the current view while loading
     */
    async loadGameweek({ forceSync = false, silent = false } = {}) {
        this.clearRefresh();
        const { managerId, gameweekId } = this.state;
        if (!managerId || !gameweekId) {
            this.state.data = null;
            this.state.loaded = true;
            return;
        }
        const token = ++this.loadToken;
        if (!silent) {
            this.state.loading = true;
        }
        try {
            const data = await this.orm.call(
                "fpl.gameweek.picks",
                "get_gameweek_picks_data",
                [managerId, gameweekId],
                { force_sync: forceSync }
            );
            if (token !== this.loadToken) {
                return;
            }
            this.state.data = data.found ? data : null;
            this.keepSelection();
        } catch (error) {
            if (token === this.loadToken) {
                if (!silent) {
                    this.state.data = null;
                }
                this.notifyError(error, _t("Could not get the gameweek picks"));
            }
        } finally {
            if (token === this.loadToken) {
                this.state.loading = false;
                this.state.loaded = true;
                this.scheduleRefresh();
            }
        }
    }

    /** Keep the selected player when he is still in the squad, else select the captain. */
    keepSelection() {
        const players = this.players;
        if (!players.some((p) => p.id === this.state.selectedId)) {
            const captain = players.find((p) => p.is_captain) || players[0];
            this.state.selectedId = captain ? captain.id : false;
        }
    }

    /** Matches in progress: refresh the points every minute. */
    scheduleRefresh() {
        const data = this.state.data;
        if (data && data.has_live && data.event.is_current) {
            this.refreshTimer = browser.setTimeout(() => this.loadGameweek({ silent: true }), LIVE_REFRESH_DELAY);
        }
    }

    clearRefresh() {
        if (this.refreshTimer) {
            browser.clearTimeout(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    notifyError(error, title) {
        this.notification.add(error.data?.message || error.message || title, { title, type: "danger" });
    }

    // ------------------------------------------------------------------
    // Handlers
    // ------------------------------------------------------------------

    onManagerChange(ev) {
        this.state.managerId = parseInt(ev.target.value) || false;
        this.state.selectedId = false;
        this.loadGameweek();
    }

    onGameweekChange(ev) {
        this.setGameweek(parseInt(ev.target.value));
    }

    setGameweek(gameweekId) {
        if (gameweekId && gameweekId !== this.state.gameweekId) {
            this.state.gameweekId = gameweekId;
            this.loadGameweek();
        }
    }

    previousGameweek() {
        this.setGameweek(this.state.gameweeks[this.gameweekIndex - 1]?.id);
    }

    nextGameweek() {
        this.setGameweek(this.state.gameweeks[this.gameweekIndex + 1]?.id);
    }

    refresh() {
        this.loadGameweek({ forceSync: true });
    }

    selectPlayer(playerId) {
        this.state.selectedId = playerId;
    }

    async openPlayerStats(playerId) {
        const action = await this.orm.call("fpl.gameweek.pick.lines", "action_open_player_stats", [playerId]);
        if (action) {
            this.action.doAction(action);
        }
    }

    // ------------------------------------------------------------------
    // Template helpers
    // ------------------------------------------------------------------

    get gameweekIndex() {
        return this.state.gameweeks.findIndex((gw) => gw.id === this.state.gameweekId);
    }

    get hasPrevious() {
        return this.gameweekIndex > 0;
    }

    get hasNext() {
        const index = this.gameweekIndex;
        return index >= 0 && index < this.state.gameweeks.length - 1;
    }

    get players() {
        const data = this.state.data;
        return data ? [...data.rows.flat(), ...data.bench] : [];
    }

    get selectedPlayer() {
        return this.players.find((p) => p.id === this.state.selectedId) || null;
    }

    get syncedAgo() {
        const syncedAt = this.state.data?.synced_at;
        return syncedAt ? deserializeDateTime(syncedAt).toRelative() : "";
    }

    get isTripleCaptain() {
        return this.state.data?.summary.active_chip === "3xc";
    }

    get isBenchBoost() {
        return this.state.data?.summary.active_chip === "bboost";
    }

    get summaryItems() {
        const s = this.state.data.summary;
        const change = s.overall_rank_change;
        return [
            {
                label: _t("GW rank"),
                value: this.formatRank(s.rank),
                note: s.percentile_rank ? _t("Top %s%", s.percentile_rank) : "",
            },
            {
                label: _t("Overall rank"),
                value: this.formatRank(s.overall_rank),
                note: change ? `${change > 0 ? "▲" : "▼"} ${Math.abs(change).toLocaleString()}` : "",
                noteClass: change > 0 ? "text-success" : change < 0 ? "text-danger" : "",
            },
            { label: _t("Total points"), value: (s.total_points || 0).toLocaleString() },
            {
                label: _t("Transfers"),
                value: s.event_transfers || 0,
                note: s.event_transfers_cost ? _t("-%s pts", s.event_transfers_cost) : _t("No hit"),
                noteClass: s.event_transfers_cost ? "text-danger" : "",
            },
            { label: _t("Bank"), value: this.formatMoney(s.bank) },
            { label: _t("Team value"), value: this.formatMoney(s.value) },
            {
                label: _t("Bench points"),
                value: s.points_on_bench || 0,
                note: this.isBenchBoost ? _t("Counted") : "",
            },
            { label: _t("Chip"), value: s.active_chip_name || _t("None") },
        ];
    }

    formatRank(rank) {
        return rank ? rank.toLocaleString() : "–";
    }

    formatMoney(value) {
        return `£${(value || 0).toFixed(1)}m`;
    }

    /** C / TC / V badge of a player, "" for the others. */
    roleBadge(player) {
        if (player.is_captain) {
            return this.isTripleCaptain ? "TC" : "C";
        }
        return player.is_vice_captain ? "V" : "";
    }

    roleLabel(player) {
        return { TC: _t("Triple captain"), C: _t("Captain"), V: _t("Vice-captain") }[this.roleBadge(player)] || "";
    }

    get benchPoints() {
        return (this.state.data?.bench || []).reduce((total, p) => total + (p.raw_points || 0), 0);
    }

    get emptyMessage() {
        if (!this.state.gameweeks.length) {
            return _t("No gameweek has started yet this season.");
        }
        if (!this.state.managerId) {
            return this.props.selectManager
                ? _t("Add a manager team first (Your FPL Team > Manager Team).")
                : _t("Save the manager team to see its picks.");
        }
        return _t("No picks for this gameweek: the manager may have joined the game later.");
    }

    autoSubTitle(player) {
        return player.auto_sub === "in"
            ? _t("Automatic substitution: came in from the bench")
            : _t("Automatic substitution: did not play, replaced from the bench");
    }

    cardAriaLabel(player) {
        const parts = [
            player.name,
            player.team_name,
            this.hasStarted(player) ? _t("%s points", player.points) : this.cardBottom(player),
        ];
        const role = this.roleLabel(player);
        if (role) {
            parts.push(role);
        }
        if (player.status !== "a") {
            parts.push(this.statusHeadline(player));
        }
        return parts.join(", ");
    }

    isLive(player) {
        return player.fixtures.some((f) => f.live);
    }

    hasStarted(player) {
        return player.fixtures.some((f) => f.started);
    }

    /** Points once a fixture of the player has kicked off, else his opponent(s). */
    cardBottom(player) {
        if (this.hasStarted(player)) {
            return String(player.points);
        }
        if (!player.fixtures.length) {
            return "–";
        }
        return player.fixtures.map((f) => `${f.opponent} (${f.is_home ? "H" : "A"})`).join(", ");
    }

    isBenchCounted(player) {
        return player.bench_order === 0 || this.isBenchBoost;
    }

    benchLabel(player) {
        return player.position === "GKP" ? "GKP" : `${player.bench_order - 1}. ${player.position}`;
    }

    /**
     * Availability flag of a player, null when available.
     *
     * @returns {{ cls: string, icon: string, title: string } | null}
     */
    statusFlag(player) {
        const status = player.status;
        if (!status || status === "a") {
            return null;
        }
        let cls = "o_fpl_status_out";
        let icon = "!";
        if (status === "d") {
            const chance = player.chance ?? 50;
            cls = chance >= 75 ? "o_fpl_status_75" : chance >= 50 ? "o_fpl_status_50" : "o_fpl_status_25";
        } else if (status === "i") {
            cls = "o_fpl_status_injured";
            icon = "+";
        } else if (status === "s") {
            cls = "o_fpl_status_suspended";
            icon = "";
        }
        return { cls, icon, title: this.statusText(player) };
    }

    /** "Injured", "Doubtful · 75% chance of playing", ... */
    statusHeadline(player) {
        if (player.status === "d" && player.chance !== null) {
            return _t("%(status)s · %(chance)s% chance of playing", {
                status: player.status_label,
                chance: player.chance,
            });
        }
        return player.status_label;
    }

    statusText(player) {
        const headline = this.statusHeadline(player);
        return player.news ? `${headline} – ${player.news}` : headline;
    }

    newsDate(player) {
        if (!player.news_added) {
            return "";
        }
        const date = DateTime.fromISO(player.news_added);
        return date.isValid ? date.toLocaleString(DateTime.DATE_MED) : "";
    }

    fixtureCenter(fixture) {
        return fixture.started ? `${fixture.home_score ?? 0} – ${fixture.away_score ?? 0}` : _t("vs");
    }

    fixtureStatus(fixture) {
        if (fixture.live) {
            return _t("Live · %s'", fixture.minutes || 0);
        }
        if (fixture.finished) {
            return _t("Full time");
        }
        if (fixture.started) {
            return _t("In progress");
        }
        return fixture.kickoff_time
            ? deserializeDateTime(fixture.kickoff_time).toFormat("ccc d LLL · HH:mm")
            : _t("Kick-off to be confirmed");
    }

    fixtureEmptyText(player, fixture) {
        if (!fixture.started) {
            return _t("The match has not started yet.");
        }
        return player.raw_points ? "" : _t("Did not play.");
    }

    totalLabel(player) {
        if (player.bench_order) {
            return this.isBenchBoost ? _t("Total (Bench Boost)") : _t("Total (bench, not counted)");
        }
        if (player.multiplier > 1) {
            return _t("Total (%(points)s × %(multiplier)s)", {
                points: player.raw_points,
                multiplier: player.multiplier,
            });
        }
        return _t("Total");
    }
}
