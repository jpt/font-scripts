#MenuTitle: Reinterpolate special layer sidebearings
# -*- coding: utf-8 -*-

__doc__="""
Re-interpolate special layer sidebearings (intermediate and alternate layers, a.k.a. brace and bracket layers)
"""

font = Glyphs.font

for glyph in font.glyphs:
	for layer in glyph.layers:
		if layer.isSpecialLayer:
			layer.reinterpolateMetrics()