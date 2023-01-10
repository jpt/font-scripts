# MenuTitle: New tab with glyphs using selected as component
__doc__ = """
New tab with glyphs using the selected glyph as a component"""

def main():
	font = Glyphs.font
	tab_str = ""
	selected_glyph = [glyph for glyph in font.glyphs if glyph.selected]
	if len(selected_glyph) > 1:
		print("Select only one glyph")
		return
	selected_glyph = selected_glyph[0]
	glyphs_with_selected = [glyph.name for glyph in font.glyphs for layer in (layer for layer in glyph.layers if layer.isMasterLayer or layer.isSpecialLayer) for shape in layer.shapes if shape.shapeType == 4 and shape.name == selected_glyph.name]
	tab_str = '/' + '/'.join(glyphs_with_selected)
	font.newTab(tab_str) if tab_str != '/' else print(f"No glyphs containing {selected_glyph.name} found")	

main()
