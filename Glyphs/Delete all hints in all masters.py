# MenuTitle: Delete all hints in all masters
__doc__ = """
Removes all hints (PS and TT) in all glyphs in all masters
"""

Font = Glyphs.font
for glyph in Font.glyphs:
	for layer in glyph.layers:
		if layer.hints:
			for i in range(len(layer.hints)-1, -1, -1):
				del layer.hints[i]

