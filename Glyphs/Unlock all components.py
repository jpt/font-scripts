#MenuTitle: Unlock all components
# -*- coding: utf-8 -*-

__doc__="""
Unlocks all components in all layers for the active glyph or selected glyphs
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
	print("Unlocking components in %s" % glyph.name)
	for layer in glyph.layers:
		for component in layer.components:
			component.locked = False