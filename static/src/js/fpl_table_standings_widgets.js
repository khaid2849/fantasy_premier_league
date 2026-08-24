/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";

const TEAM_LOGO_PATH = "/fantasy_premier_league/static/src/img/teams_logo";

function openFixtureWizard(actionService, fixtureId) {
    if (!fixtureId) {
        return;
    }
    actionService.doAction({
        type: "ir.actions.act_window",
        res_model: "fpl.gameweek.fixtures",
        res_id: fixtureId,
        name: "Fixture",
        view_mode: "form",
        view_type: "form",
        views: [[false, "form"]],
        target: "new",
    });
}

/**
 * Renders the crest + name of the team for a standings row (m2o field).
 */
export class FplTeamBadgeField extends Component {
    static template = "fantasy_premier_league.FplTeamBadgeField";
    static props = { ...standardFieldProps };

    get teamName() {
        return this.props.record.data[this.props.name]?.display_name || "";
    }

    get teamCode() {
        return this.props.record.data.team_code;
    }

    get logoSrc() {
        return this.teamCode ? `${TEAM_LOGO_PATH}/${this.teamCode}.svg` : "";
    }
}

registry.category("fields").add("fpl_team_badge", {
    component: FplTeamBadgeField,
    fieldDependencies: [{ name: "team_code", type: "char" }],
});

/**
 * Renders the last 5 results as clickable W/D/L chips (one2many field).
 * Clicking a chip opens that match's fixture form as a popup.
 */
export class FplStandingsFormField extends Component {
    static template = "fantasy_premier_league.FplStandingsFormField";
    static props = { ...standardFieldProps };

    setup() {
        this.action = useService("action");
    }

    get formResults() {
        const records = this.props.record.data[this.props.name]?.records || [];
        return records
            .map((r) => ({
                id: r.resId,
                result: r.data.result,
                fixtureId: r.data.fixture_id[0] || false,
            }))
            .sort((a, b) => a.id - b.id);
    }

    onChipClick(fixtureId) {
        openFixtureWizard(this.action, fixtureId);
    }
}

registry.category("fields").add("fpl_standings_form", {
    component: FplStandingsFormField,
});

/**
 * Renders the next opponent's crest (m2o field: next_fixture_id).
 * Clicking it opens the upcoming match's fixture form as a popup.
 */
export class FplNextOpponentField extends Component {
    static template = "fantasy_premier_league.FplNextOpponentField";
    static props = { ...standardFieldProps };

    setup() {
        this.action = useService("action");
    }

    get opponentName() {
        return this.props.record.data.next_opponent_id[1];
    }

    get opponentCode() {
        return this.props.record.data.next_opponent_code;
    }

    get logoSrc() {
        return this.opponentCode ? `${TEAM_LOGO_PATH}/${this.opponentCode}.svg` : "";
    }

    get fixtureId() {
        return this.props.record.data.next_fixture_id[0];
    }

    onLogoClick() {
        openFixtureWizard(this.action, this.fixtureId);
    }
}

registry.category("fields").add("fpl_next_opponent", {
    component: FplNextOpponentField,
    fieldDependencies: [
        { name: "next_opponent_id", type: "many2one" },
        { name: "next_opponent_code", type: "char" },
    ],
});
