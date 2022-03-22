#MenuTitle: Replace UC diacritics with .case versions
# -*- coding: utf-8 -*-

__doc__="""
Replaces (across the entire font) all occurences of components in glyphs with "comb" in their name, with the corresponding ".case" glyph, if that glyph is uppercase.
"""

Font = Glyphs.font.glyphs
for glyph in Font:
	if glyph.case == 1 and not "comb" in glyph.name:
		for layer in glyph.layers:
			for i, component in enumerate(layer.components):
				if(component.name + ".case" in Font):
					layer.components[i].componentName = component.name + ".case"
