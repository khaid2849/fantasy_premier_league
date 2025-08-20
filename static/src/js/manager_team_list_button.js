/** @odoo-module */
import { ListController } from "@web/views/list/list_controller";
import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';

export class ManagerTeamListController extends ListController {
   setup() {
       super.setup();
   }
   OnVerifyTeamDataClick() {
       this.actionService.doAction({
          type: 'ir.actions.act_window',
          res_model: 'fpl.manager.team.wizard',
          name:'Verify Team Manager Data',
          view_mode: 'form',
          view_type: 'form',
          views: [[false, 'form']],
          target: 'new',
          res_id: false,
      });
   }
}
ManagerTeamListController.template = "module.fantasy_premier_league.ListView.Buttons";
export const customManagerTeamListController = {
    ...listView,
    Controller: ManagerTeamListController,
};
registry.category("views").add("verify_manager_team_data_js", customManagerTeamListController);

