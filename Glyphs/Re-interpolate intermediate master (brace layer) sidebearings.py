#MenuTitle: Reinterpolate itermediate master (brace layer) sidebearings 
# -*- coding: utf-8 -*-

__doc__="""
Re-interpolate sidebearings of intermediate master layers (formerly known as brace layers)
"""

font = Glyphs.font

for glyph in font.glyphs:
	for layer in glyph.layers:
		if layer.isSpecialLayer and layer.name.startswith("{"):
			layer.reinterpolateMetrics()