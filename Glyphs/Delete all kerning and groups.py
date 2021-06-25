#MenuTitle: Delete all kerning and groups
# -*- coding: utf-8 -*-
__doc__="""
Delete all kerning and groups across all masters
"""

Font = Glyphs.font
gc = 0

def deleteLog(direction):
    global gc
    gc += 1
    print("Deleting %s kerning group for glyph: %s" % (direction, glyph.name))

for glyph in Font.glyphs:
    for layer in glyph.layers:
        if glyph.rightKerningGroup:
            glyph.rightKerningGroup = None
            deleteLog("right")
        if glyph.leftKerningGroup:
            glyph.leftKerningGroup = None
            deleteLog("left")
        if glyph.topKerningGroup:
            glyph.topKerningGroup = None
            deleteLog("top")
        if glyph.bottomKerningGroup:
            glyph.bottomKerningGroup = None
            deleteLog("bottom")
           
Font.kerning = {}
Font.kerningRTL = {}
Font.kerningVertical = {}
print("\nDone! Deleted %s groups and all kerning in %s masters." % (gc, len(Font.masters)))