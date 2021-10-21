#MenuTitle: Set all horizontal TT stem hints to round with no stems
# -*- coding: utf-8 -*-

__doc__="""
Sets all horizontal TT stem hints to round with no stems
"""

for glyph in Glyphs.font.glyphs:
	for layer in glyph.layers:
		if layer.hints:
			for hint in layer.hints:
				if hint.isTrueType and hint.horizontal and hint.type == TTSTEM:
						hint.options = 0
						hint.stem = -1