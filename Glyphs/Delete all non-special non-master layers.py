#MenuTitle: Delete all non-special non-master layers
# -*- coding: utf-8 -*-

__doc__="""
Deletes all non-special (brace, bracket), non-master layers in the current font.
"""

for glyph in Glyphs.font.glyphs:
	for i,layer in enumerate(glyph.layers):
		if not layer.isSpecialLayer and not layer.isMasterLayer:
			print("Deleting %s in %s" % (layer.name, layer.parent.name))