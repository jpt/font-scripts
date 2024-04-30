# MenuTitle: Center Anchor Between Points
# -*- coding: utf-8 -*-

__doc__ = """
Centers the horizontal position of an anchor between two selected points in all masters. Select exactly two points and one anchor in the active master.
"""


from GlyphsApp import Glyphs, GSNode, GSAnchor, NSPoint

def center_anchor_between_points(glyph):
    active_layer = Glyphs.font.selectedLayers[0]
    
    # Gather selected nodes and anchors from the active layer
    selected_points_info = [(path, node) for path in active_layer.paths for node in path.nodes if node.selected and node.type != OFFCURVE]
    selected_anchors = [anchor for anchor in active_layer.anchors if anchor.selected]

    # Check if the correct number of points and anchors are selected
    if len(selected_points_info) != 2 or len(selected_anchors) != 1:
        print("Error: Please select exactly two points and one anchor in the active master.")
        return
    
    # Calculate path and node indices for the selected nodes
    selected_points_indices = []
    for path, node in selected_points_info:
        path_index = None
        for idx, p in enumerate(active_layer.paths):
            if p == path:
                path_index = idx
                break
        node_index = None
        for idx, n in enumerate(path.nodes):
            if n == node:
                node_index = idx
                break
        if path_index is not None and node_index is not None:
            selected_points_indices.append((path_index, node_index))

    # Apply the changes to all layers
    for layer in glyph.layers:
        if not layer.isMasterLayer:
            continue

        try:
            # Find the corresponding nodes in this master layer using indices
            nodes_in_layer = [layer.paths[path_index].nodes[node_index] for path_index, node_index in selected_points_indices]
            x1, x2 = nodes_in_layer[0].x, nodes_in_layer[1].x
            midpoint_x = (x1 + x2) / 2
        except Exception as e:
            print(f"Error in master {layer.master.name}: {str(e)}")
            continue

        anchor_name = selected_anchors[0].name
        anchor = next((a for a in layer.anchors if a.name == anchor_name), None)

        if anchor:
            anchor.position = NSPoint(midpoint_x, anchor.position.y)
            print(f"Anchor '{anchor.name}' has been centered horizontally between the selected points on master {layer.master.name}.")
        else:
            print(f"Error in master {layer.master.name}: Anchor '{anchor_name}' not found.")

glyph = Glyphs.font.selectedLayers[0].parent
center_anchor_between_points(glyph)
