#MenuTitle: New tab with open path layers
# -*- coding: utf-8 -*-

__doc__="""
Finds active layers with open paths and creates a new tab with them
"""

Font = Glyphs.font
open_layers = [layer for glyph in Font.glyphs for layer in glyph.layers if (layer.isMasterLayer or layer.isSpecialLayer) and any(not path.closed for path in layer.paths)]
print(f"Found {len(open_layers)} layers with open paths: {open_layers}")
Font.newTab(open_layers)