#MenuTitle: Horizontally center
# -*- coding: utf-8 -*-

__doc__="""
Horizontally centers selected paths, anchors, and components. You might find this helpful for things like the dot on an exclamation point, the strokes on the yen symbol, etc.
"""

from Foundation import NSPoint

font = Glyphs.font
selected_paths = []
selected_anchors = []

# Calculate combined bounding box for selected paths and components
combined_min_x = None
combined_max_x = None

for path in font.selectedLayers[0].paths:
    if path.selected:
        selected_paths.append(path)
        if combined_min_x is None or path.bounds.origin.x < combined_min_x:
            combined_min_x = path.bounds.origin.x
        if combined_max_x is None or (path.bounds.origin.x + path.bounds.size.width) > combined_max_x:
            combined_max_x = path.bounds.origin.x + path.bounds.size.width

for component in font.selectedLayers[0].components:
    if component.selected:
        selected_paths.append(component)
        if combined_min_x is None or component.bounds.origin.x < combined_min_x:
            combined_min_x = component.bounds.origin.x
        if combined_max_x is None or (component.bounds.origin.x + component.bounds.size.width) > combined_max_x:
            combined_max_x = component.bounds.origin.x + component.bounds.size.width

for anchor in font.selectedLayers[0].anchors:
    if anchor.selected:
        selected_anchors.append(anchor)

# Centering the combined bounding box within the glyph width
if selected_paths:
    glyph_width = font.selectedLayers[0].width
    combined_width = combined_max_x - combined_min_x
    move_to = (glyph_width/2) - (combined_width/2)
    move_by = combined_min_x - move_to
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
                move_by,  # x position
                0.0    # y position
            ))

# Centering anchors
if selected_anchors:
    for anchor in selected_anchors:
        layer = font.selectedLayers[0]
        width = layer.width
        x = width / 2 + move_by
        y = anchor.position.y
        print("Moving anchor %s to (%s,%s)" % (anchor.name, x, y))
        anchor.position = NSPoint(x, y)

if not selected_paths and not selected_anchors:
    print("You haven't selected anything to center.")
