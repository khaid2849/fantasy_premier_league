/** @odoo-module */

import { HierarchyModel } from "@web_hierarchy/hierarchy_model";
import { patch } from "@web/core/utils/patch";

export class FplCustomHierarchyModel extends HierarchyModel {
  /**
   * @override
   * Use the `move_to` method of the model instead of a simple `write` for
   * some extra processing and validations.
   */
    async load(params = {}) {
        await super.load(params);
        // Auto-collapse all nodes that have children
        if (this.root && this.root.rootNodes) {
            this._autoCollapseAllNodes(this.root.rootNodes);
        }
        
        this.notify();
    };
    // Override the reload method to auto-collapse all nodes after reloading  
    async reload() {
        await super.reload();
        
        // Auto-collapse all nodes that have children
        if (this.root && this.root.rootNodes) {
            this._autoCollapseAllNodes(this.root.rootNodes);
        }
        
        this.notify();
    };
    // Helper method to recursively collapse all nodes
    _autoCollapseAllNodes(nodes) {
        for (const node of nodes) {
            // If node has children and they are currently visible, collapse them
            if (node.nodes && node.nodes.length > 0) {
                node.collapseChildNodes();
            }
            // Recursively process any child nodes
            if (node.nodes) {
                this._autoCollapseAllNodes(node.nodes);
            }
        }
    };
    // Override fetchSubordinates to prevent expansion
    async fetchSubordinates(node) {
        // Do nothing to prevent expanding child nodes
        return;
    }
}