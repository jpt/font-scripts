#MenuTitle: Vertically center in capheight
# -*- coding: utf-8 -*-

__doc__="""
Vertically centers selected paths, anchors, and components relative to the capheight.
"""

from Foundation import NSPoint

font = Glyphs.font
selected_paths = []
selected_anchors = []

# Calculate combined bounding box for selected paths and components
combined_min_y = None
combined_max_y = None

for path in font.selectedLayers[0].paths:
    if path.selected:
        selected_paths.append(path)
        if combined_min_y is None or path.bounds.origin.y < combined_min_y:
            combined_min_y = path.bounds.origin.y
        if combined_max_y is None or (path.bounds.origin.y + path.bounds.size.height) > combined_max_y:
            combined_max_y = path.bounds.origin.y + path.bounds.size.height

for component in font.selectedLayers[0].components:
    if component.selected:
        selected_paths.append(component)
        if combined_min_y is None or component.bounds.origin.y < combined_min_y:
            combined_min_y = component.bounds.origin.y
        if combined_max_y is None or (component.bounds.origin.y + component.bounds.size.height) > combined_max_y:
            combined_max_y = component.bounds.origin.y + component.bounds.size.height

for anchor in font.selectedLayers[0].anchors:
    if anchor.selected:
        selected_anchors.append(anchor)

# Centering the combined bounding box within the cap height
if selected_paths:
    cap_height = font.selectedLayers[0].master.capHeight
    combined_height = combined_max_y - combined_min_y
    move_to = (cap_height/2) - (combined_height/2)
    move_by = combined_min_y - move_to
    move_by *= -1

    if move_by == 0:
        print("Selection is already centered")
    else:
        print("Centering selection, moving by %s" % move_by)
        for path in selected_paths:
            path.applyTransform((
                1.0,  # x scale factor
                0.0,  # x skew factor
                0.0,  # y skew factor
                1.0,  # y scale factor
                0.0,  # x position
                move_by  # y position
            ))

# Centering anchors
if selected_anchors:
    for anchor in selected_anchors:
        layer = font.selectedLayers[0]
        height = layer.master.capHeight
        y = height / 2 + move_by
        x = anchor.position.x
        print("Moving anchor %s to (%s,%s)" % (anchor.name, x, y))
        anchor.position = NSPoint(x, y)

if not selected_paths and not selected_anchors:
    print("You haven't selected anything to center.")