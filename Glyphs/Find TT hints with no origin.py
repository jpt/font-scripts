#MenuTitle: Find TT hints with no origin
# -*- coding: utf-8 -*-
__doc__="""
Finds bad hints without origins, often caused by copying and pasting hinted outlines between layers. Requires a Get Hints From Master custom parameter
"""

font = Glyphs.font
if not font.customParameters["Get Hints From Master"]:
	print("The Get Hints From Master custom parameter is required for this script")
else:
	no_origin_hints = [glyph.name for glyph in font.glyphs if any(not hint.origin and hint.isTrueType for hint in glyph.layers[font.customParameters["Get Hints From Master"]].hints)]
	font.newTab('/' + "/".join(no_origin_hints))