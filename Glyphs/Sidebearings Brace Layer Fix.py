#MenuTitle: Sidebearings Brace Layer Fix
# -*- coding: utf-8 -*-

__doc__="""
Re-interpolate sidebearings of brace layers
"""

import GlyphsApp
import re
brace = re.compile("^{\d+,\s*\d+}$")

Font = Glyphs.font

for glyph in Font.glyphs:
  if glyph.layers > 1 and '.' not in glyph.name:
    for layer in glyph.layers:
      if brace.match(layer.name):
        print layer.name
        print layer.LSB