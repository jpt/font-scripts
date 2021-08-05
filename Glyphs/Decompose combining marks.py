#MenuTitle: Decompose combining marks in all masters
# -*- coding: utf-8 -*-

__doc__="""
Decomposes all combining marks in all masters 
"""

font = Glyphs.font

for glyph in font.glyphs:
	if glyph.name.endswith("comb") and len(glyph.glyphInfo.anchors) > 0:
		print("Decomposing %s" % glyph.name)
		for layer in glyph.layers:
			layer.decomposeComponents()
			layer.syncMetrics()
