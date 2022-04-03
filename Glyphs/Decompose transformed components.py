# MenuTitle: Decompose transformed components
__doc__ = """
Removes overlaps and writes binaries. Edit this script to change formats and paths.
"""
			
transformed_components = []
for glyph in Glyphs.font.glyphs:
	for layer in glyph.layers:
		if layer.isMasterLayer or layer.isSpecialLayer:
			if layer.shapes:
				for shape in layer.shapes:
					if shape.shapeType == 4:
						if shape.transform[0:4] != (1.0,0.0,0.0,1.0):
							transformed_components.append((shape,glyph.name))
for shape,glyph_name in transformed_components:
	print("Decomposing %s in %s" % (shape.name,glyph_name))
	shape.decompose()