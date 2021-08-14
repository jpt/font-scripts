#MenuTitle: Build Cyrillic composite glyphs
# -*- coding: utf-8 -*-

__doc__="""
Adds entry and exit anchors to En-cy, El-cy, en-cy, el-cy, Softsign-cy, and softsign-cy to generate Lje-cy, Nje-cy, lje-cy, and nje-cy
"""

font = Glyphs.font

exit_glyphs = ["En-cy", "El-cy", "en-cy", "el-cy"]
entry_glyphs = ["Softsign-cy", "softsign-cy"]
all_glyphs = exit_glyphs + entry_glyphs
to_generate = ["Lje-cy", "Nje-cy", "lje-cy", "nje-cy"]

measure_at = 0.85 # this will differ by font, YMMV — this is a percentage of the cap height or x-height's x coordinate at which to measure stem width

for glyph_name in all_glyphs:
	glyph = font.glyphs[glyph_name]
	for layer in glyph.layers:
		if glyph_name[0].isupper():
			y = layer.master.capHeight / 2
			measure_point = layer.master.capHeight * measure_at
		else:
			y = layer.master.xHeight / 2
			measure_point = layer.master.xHeight * measure_at
		start = -1
		stop = layer.width
		measuring_layer = layer.copyDecomposedLayer()
		intersections = measuring_layer.intersectionsBetweenPoints((start, measure_point), (stop, measure_point))
		stem_width = intersections[-2].x - intersections[-3].x
		leftmost = intersections[1].x
		rightmost = intersections[-2].x
		if glyph_name in exit_glyphs:
			print("Adding exit anchor to %s %s" % (glyph_name, layer.name)) 
			x = rightmost										
			layer.anchors['#exit'] = GSAnchor()
			layer.anchors['#exit'].position = NSPoint(x, y)
		elif glyph_name in entry_glyphs:
			print("Adding entry anchor to %s %s" % (glyph_name, layer.name)) 
			x = leftmost + stem_width
			layer.anchors['#entry'] = GSAnchor()
			layer.anchors['#entry'].position = NSPoint(x, y)
for glyph_name in to_generate:
	try:
		font.glyphs.append(GSGlyph(glyph_name))
		for layer in font.glyphs[glyph_name].layers:
			if glyph_name == "Lje-cy":
				components = [GSComponent(font.glyphs["El-cy"]),GSComponent(font.glyphs["Softsign-cy"])]
			elif glyph_name == "Nje-cy":
				components = [GSComponent(font.glyphs["En-cy"]),GSComponent(font.glyphs["Softsign-cy"])]
			elif glyph_name == "lje-cy":
				components = [GSComponent(font.glyphs["el-cy"]),GSComponent(font.glyphs["softsign-cy"])]
			elif glyph_name == "nje-cy":
				components = [GSComponent(font.glyphs["en-cy"]),GSComponent(font.glyphs["softsign-cy"])]
			for component in components:
				layer.components.append(component)
		print("Created %s!" % glyph_name)
	except NameError:
		print("%s already exists. Please make a copy to back it up, delete it, and re-run this script." % glyph_name)