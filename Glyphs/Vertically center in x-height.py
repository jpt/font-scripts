#MenuTitle: Vertically center in x-height
# -*- coding: utf-8 -*-

__doc__="""
Vertically centers selected paths, anchors, and components relative to the x-height.
"""

from Foundation import NSPoint

font = Glyphs.font
selected_paths = []
selected_anchors = []

for path in font.selectedLayers[0].paths:
	if path.selected:
		selected_paths.append(path)
for component in font.selectedLayers[0].components:
	if component.selected:
		selected_paths.append(component)
for anchor in font.selectedLayers[0].anchors:
    if anchor.selected:
        selected_anchors.append(anchor)

if selected_paths:
	x_height = font.selectedLayers[0].master.xHeight
	for path in selected_paths:
		bottom = path.bounds.origin.y
		height =  path.bounds.size.height
		move_to = (x_height/2) - (height/2)
		move_by = bottom - move_to
		move_by *= -1
		print(move_by)
		
		if move_by == 0:
			print("Path is already centered")
		else:
			print("Centering path, moving by %s" % move_by)
			path.applyTransform((
				1.0, # x scale factor
				0.0, # x skew factor
				0.0, # y skew factor
				1.0, # y scale factor
				0.0, # x position			
				move_by  # y position
			))

if selected_anchors:
    for anchor in selected_anchors:
        layer = font.selectedLayers[0]
        height = layer.master.xHeight
        y = height / 2
        x = anchor.position.x
        print("Moving anchor %s to (%s,%s)" % (anchor.name,x,y))
        anchor.position = NSPoint(x,y)

if not selected_paths and not selected_anchors:
	print("You haven't selected anything to center.")
