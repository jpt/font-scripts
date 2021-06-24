#MenuTitle: Delete kerning groups and values
# -*- coding: utf-8 -*-
__doc__="""
Delete all kerning groups and values across all masters
"""

Font = Glyphs.font
gc = 0

def deleteGroup(direction):
    gc += 1
    print("Deleting %s kerning group for glyph: %s" % (direction, glyph.name))
    glyph[direction + "KerningGroup"] = None

for glyph in Font.glyphs:
    for layer in glyph.layers:
        if glyph.rightKerningGroup:
            deleteGroup("right")
        if glyph.leftKerningGroup:
            deleteGroup("left")
        if glyph.topKerningGroup:
            deleteGroup("top")
        if glyph.bottomKerningGroup:
            deleteGroup("bottom")

Font.kerning = {}
Font.kerningRTL = {}
Font.kerningVertical = {}
print("\nDone! Deleted %s groups and all kerning in %s masters." % (gc, len(Font.masters)))