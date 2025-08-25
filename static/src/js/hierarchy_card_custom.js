/** @odoo-module */
import { HierarchyCard } from "@web_hierarchy/hierarchy_card";

export class FplCustomHierarchyCard extends HierarchyCard {
  /**
   * @override
   * Add a context variable to be able to show/hide the section if a node
   * is a root (in the hierarchy view).
   */
  // Override the onClickArrowDown to prevent fold/unfold actions
    onClickArrowDown(ev) {
        // Disable the fold/unfold functionality by not calling the parent method
        ev.preventDefault();
        ev.stopPropagation();
    };
    
    // Override to hide the fold/unfold button by modifying the class names
    get classNames() {
        const classNames = [this.props.classNames];
        // Always show as folded (no o_hierarchy_node_unfolded class)
        return classNames.join(" ");
    }
}