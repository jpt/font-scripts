#MenuTitle: Delete all anchors in selected glyphs
# -*- coding: utf-8 -*-

__doc__="""
Deletes all anchors in the active glyph, or all selected glyphs if the editor isn't open.
"""

font = Glyphs.font

selected_glyphs = []

if font.selectedLayers[0]:
	selected_glyphs.append(font.selectedLayers[0].parent)
else:
	for glyph in font.glyphs:
	    if glyph.selected:
	        selected_glyphs.append(glyph)

for glyph in selected_glyphs:
	for layer in glyph.layers:
		for i,anchor in enumerate(layer.anchors):
			del(layer.anchors[i])