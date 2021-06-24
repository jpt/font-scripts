#MenuTitle: Delete all kerning groups
# -*- coding: utf-8 -*-
__doc__="""
Delete all kerning groups across all masters
"""
c = 0
for glyph in Font.glyphs:
    for layer in glyph.layers:
        if glyph.rightKerningGroup:
            c += 1
            print("Deleting right kerning group for glyph: %s" % glyph.name)
            glyph.rightKerningGroup = None
        if glyph.leftKerningGroup:
            c += 1
            print("Deleting left kerning group for glyph: %s" % glyph.name)
            glyph.leftKerningGroup = None
print("\nDone! Deleted %s groups in %s masters." % (c, len(Font.masters)))