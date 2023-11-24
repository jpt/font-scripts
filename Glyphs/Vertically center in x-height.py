#MenuTitle: Vertically center in x-height
# -*- coding: utf-8 -*-

__doc__="""
Vertically centers selected paths, anchors, and components relative to the x-height.
"""

from Foundation import NSPoint
font = Glyphs.font

def get_combined_bounds(selected_paths, selected_components, selected_anchors):
    combined_min_y, combined_max_y = float('inf'), float('-inf')

    for item in selected_paths + selected_components:
        min_y = item.bounds.origin.y
        max_y = item.bounds.origin.y + item.bounds.size.height

        combined_min_y = min(combined_min_y, min_y)
        combined_max_y = max(combined_max_y, max_y)

    for anchor in selected_anchors:
        anchor_y = anchor.position.y

        combined_min_y = min(combined_min_y, anchor_y)
        combined_max_y = max(combined_max_y, anchor_y)

    return combined_min_y, combined_max_y

selected_paths = [path for path in font.selectedLayers[0].paths if path.selected]
selected_components = [comp for comp in font.selectedLayers[0].components if comp.selected]
selected_anchors = [anchor for anchor in font.selectedLayers[0].anchors if anchor.selected]

include_anchors_in_bounds = not selected_paths and not selected_components
combined_min_y, combined_max_y = get_combined_bounds(selected_paths, selected_components, selected_anchors if include_anchors_in_bounds else [])

if selected_paths or selected_components or selected_anchors:
    x_height = font.selectedLayers[0].master.xHeight
    move_y = x_height / 2 - (combined_max_y + combined_min_y) / 2

    for item in selected_paths + selected_components:
        item.applyTransform((1.0, 0.0, 0.0, 1.0, 0.0, move_y))

    for anchor in selected_anchors:
        anchor.position = NSPoint(anchor.position.x, anchor.position.y + move_y)

if not selected_paths and not selected_anchors:
    print("You haven't selected anything to center.")
