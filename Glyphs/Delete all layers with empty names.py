#MenuTitle: Delete all layers with empty names
# -*- coding: utf-8 -*-
__doc__="""
Deletes all layers with empty names.
"""

font = Glyphs.font
for glyph in font.glyphs:
	for i,layer in enumerate(glyph.layers):
		if layer.name is None:
			print("Deleting an empty layer on %s" % glyph.name)
			del(glyph.layers[i])