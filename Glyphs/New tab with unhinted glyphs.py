# MenuTitle: New tab with unhinted glyphs
__doc__ = """
New tab with unhinted glyphs. Does not include glyphs composed only of components."""

font = Glyphs.font
tab_str = ""
for glyph in font.glyphs:
	hint_layer = glyph.layers[font.customParameters["Get Hints From Master"]]
	if not hint_layer:
		print("Error: Set the Get Hints From Master custom parameter and try again.")
		break
	if not hint_layer.hints:
		if len(hint_layer.components) != len(hint_layer.shapes):		
			tab_str = tab_str + "/" + glyph.name
if tab_str:
	font.newTab(tab_str)
