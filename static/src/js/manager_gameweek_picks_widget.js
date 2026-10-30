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
    Object.assign(this.state, { loading: false, loaded: false });
    this.loadToken = 0;

    onWillUpdateProps((nextProps) => {
      // The pager moved to another manager: show its team on the same gameweek
      if (nextProps.record.resId !== this.props.record.resId) {
        this.setManager(nextProps.record);
        this.loadGameweek();
      }
    });
  }

  setManager(record) {
    this.state.manager_id = record.resId;
    this.state.managers = [{ id: record.resId, manager_id: record.data.manager_id }];
  }

  async loadInitialData() {
    this.setManager(this.props.record);
    try {
      // Only gameweeks that have already started can have picks
      this.state.gameweeks = await this.orm.searchRead(
        "fpl.events",
        ["|", "|", ["finished", "=", true], ["is_current", "=", true], ["is_previous", "=", true]],
        ["id", "name", "is_current", "finished", "is_previous", "is_next", "event_id"],
        { order: "event_id desc" }
      );
    } catch {
      this.notification.add(_t("Failed to load gameweeks"), { type: "danger" });
      return;
    }
    const current =
      this.state.gameweeks.find((gw) => gw.is_current) || this.state.gameweeks[0];
    if (current) {
      this.state.gameweek_id = current.id;
      await this.loadGameweek();
    }
  }

  get selectedGameweek() {
    return this.state.gameweeks.find((gw) => gw.id == this.state.gameweek_id);
  }

  onGameweekChange(ev) {
    this.state.gameweek_id = parseInt(ev.target.value);
    this.loadGameweek();
  }

  /**
   * Show the picks of the selected gameweek. A finished gameweek no longer changes, so it is
   * fetched from the FPL API only once; the current one is refreshed every time (live points).
   */
  async loadGameweek({ forceSync = false } = {}) {
    const gameweek = this.selectedGameweek;
    if (!gameweek || !this.state.manager_id) {
      return;
    }
    const token = ++this.loadToken;
    this.state.loading = true;
    this.resetFormation();
    try {
      let hasPicks = false;
      if (!forceSync && gameweek.finished && !gameweek.is_current) {
        hasPicks = await this.orm.searchCount("fpl.gameweek.picks", [
          ["manager_id", "=", this.state.manager_id],
          ["event_id", "=", gameweek.id],
        ]);
      }
      if (!hasPicks) {
        await this.orm.call("fpl.gameweek.pick.lines", "sync_gameweek_picks", [
          this.state.managers[0],
          gameweek,
        ]);
      }
      if (token === this.loadToken) {
        await this.loadFormationData();
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

  resetFormation() {
    this.state.teamStats = null;
    this.state.playersData = {};
    this.state.formation = {
      lineup_gkp: [],
      lineup_def: [],
      lineup_mid: [],
      lineup_fwd: [],
      sub_elements: [],
    };
  }

  get hasPicks() {
    return Object.keys(this.state.playersData).length > 0;
  }
}

registry.category("view_widgets").add("fpl_manager_gameweek_picks", {
  component: ManagerGameweekPicks,
});
