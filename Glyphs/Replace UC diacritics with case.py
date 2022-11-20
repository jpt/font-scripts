#MenuTitle: Replace UC diacritics with .case versions
# -*- coding: utf-8 -*-

__doc__="""
Replaces (across the entire font) all combining marks (glyphs that end with "comb"), with the corresponding ".case" glyph, if that glyph is uppercase. If a ".case" version does not exist, it will create one containing an auto-aligned component of the lowercase version.
"""

font = Glyphs.font

selected_glyphs = [glyph for glyph in font.glyphs if glyph.selected]
combining_marks = [glyph for glyph in font.glyphs if glyph.name.endswith("comb")]
case_mark_names = [glyph.name for glyph in font.glyphs if glyph.name.endswith("comb.case")]

# first, if we don't have a case variation, create one:
for mark in combining_marks:
	uc_name = mark.name + ".case"
	if(uc_name not in case_mark_names):
		font.glyphs.append(GSGlyph(uc_name))
		case_mark_names.append(uc_name)
		font.glyphs[uc_name].beginUndo()
		print("Adding %s" % uc_name)
		master_layers = [layer for layer in mark.layers if layer.isMasterLayer]
		for layer in master_layers:
			for new_layer in font.glyphs[uc_name].layers:
				new_layer.components.append(GSComponent(font.glyphs[mark.name]))
				# we can't set alignment until it's in the layer
				for component in new_layer.components:
					component.automaticAlignment = True
		font.glyphs[uc_name].endUndo()

# next, cycle through uppercase glyphs, see if they have lowercase combining marks, and replace if so

uc_glyphs = [glyph for glyph in font.glyphs if glyph.case == 1 and glyph.category == "Letter" and not glyph.name.endswith(".case")]

replaced = 0

for glyph in uc_glyphs:
	for layer in glyph.layers:
		for i, component in enumerate(layer.components):
			if(component.name + ".case" in case_mark_names):
				replaced += 1
				glyph.beginUndo()
				print("Replacing %s with %s in %s" % (component.name, component.name + ".case", glyph.name))
				layer.components[i].componentName = component.name + ".case"
				glyph.endUndo()

if(replaced == 0):
	print("No diacritics were found")
