#MenuTitle: Sidebearings Brace Layer Fix
# -*- coding: utf-8 -*-

__doc__="""
Re-interpolate sidebearings of brace layers
"""

import GlyphsApp
import re
brace = re.compile("^{\d+,\s*\d+}$")

Font = Glyphs.font


print Font.glyphs['a'].layers


for glyph in Font.glyphs:
  if glyph.layers > 1 and '.' not in glyph.name:
    for layer in glyph.layers:
      if brace.match(layer.name):

        name = layer.name

        newLayer = layer.copy()
        layer.name = "tmp"
        newLayer.name = name

        glyph.layers.append(newLayer)

        newLayer.reinterpolate()

        layer.LSB = newLayer.LSB
        layer.RSB = newLayer.RSB
        layer.name = name

        del(glyph.layers[newLayer.layerId])