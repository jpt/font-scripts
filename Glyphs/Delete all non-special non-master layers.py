#MenuTitle: Delete all non-special non-master layers
# -*- coding: utf-8 -*-

__doc__ = """
Deletes all non-special (brace, bracket), non-master layers in the current font.
"""

for glyph in Glyphs.font.glyphs:
    layers_to_delete = []

    for layer in glyph.layers:
        if not layer.isSpecialLayer and not layer.isMasterLayer:
            layers_to_delete.append(layer.layerId)

    for layerId in layers_to_delete:
        print(f"Deleting layerId {layerId} ({layer.name}) in {glyph.name}")
        del glyph.layers[layerId]
