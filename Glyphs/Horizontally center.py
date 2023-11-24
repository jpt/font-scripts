#MenuTitle: Horizontally center
# -*- coding: utf-8 -*-

__doc__="""
Horizontally centers selected paths, anchors, and components.
"""

from Foundation import NSPoint
font = Glyphs.font

def get_combined_bounds(selected_paths, selected_components, selected_anchors):
    combined_min_x, combined_max_x = float('inf'), float('-inf')

    for item in selected_paths + selected_components:
        min_x = item.bounds.origin.x
        max_x = item.bounds.origin.x + item.bounds.size.width

        combined_min_x = min(combined_min_x, min_x)
        combined_max_x = max(combined_max_x, max_x)

    for anchor in selected_anchors:
        anchor_x = anchor.position.x

        combined_min_x = min(combined_min_x, anchor_x)
        combined_max_x = max(combined_max_x, anchor_x)

    return combined_min_x, combined_max_x

selected_paths = [path for path in font.selectedLayers[0].paths if path.selected]
selected_components = [comp for comp in font.selectedLayers[0].components if comp.selected]
selected_anchors = [anchor for anchor in font.selectedLayers[0].anchors if anchor.selected]

include_anchors_in_bounds = not selected_paths and not selected_components
combined_min_x, combined_max_x = get_combined_bounds(selected_paths, selected_components, selected_anchors if include_anchors_in_bounds else [])

if selected_paths or selected_components or selected_anchors:
    glyph_width = font.selectedLayers[0].width
    move_x = glyph_width / 2 - (combined_max_x + combined_min_x) / 2

    for item in selected_paths + selected_components:
        item.applyTransform((1.0, 0.0, 0.0, 1.0, move_x, 0.0))

    for anchor in selected_anchors:
        anchor.position = NSPoint(anchor.position.x + move_x, anchor.position.y)

if not selected_paths and not selected_anchors:
    print("You haven't selected anything to center.")
