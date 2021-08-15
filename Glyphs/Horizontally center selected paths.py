#MenuTitle: Horizontally center selected paths
# -*- coding: utf-8 -*-

__doc__="""
Horizontally centers selected paths and components. You might find this helpful for things like the dot on an exclamation point, the strokes on the yen symbol, etc.
"""

font = Glyphs.font
selected_paths = []

for path in font.selectedLayers[0].paths:
	if path.selected:
		selected_paths.append(path)
for component in font.selectedLayers[0].components:
	if component.selected:
		selected_paths.append(component)
if selected_paths:
	width = font.selectedLayers[0].width
	for path in selected_paths:
		left = path.bounds.origin.x
		path_width = path.bounds.origin.x + path.bounds.size.width
		right = width - path_width
		move_by = (left - right) / 2
		move_by *= -1
		if move_by == 0:
			print("Path is already centered")
		else:
			print("Centering path, moving by %s" % move_by)
			path.applyTransform((
				1.0, # x scale factor
				0.0, # x skew factor
				0.0, # y skew factor
				1.0, # y scale factor
				move_by, # x position			
				0.0  # y position
			))
else:
	print("You haven't selected any paths to center.")
