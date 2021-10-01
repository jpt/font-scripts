#MenuTitle: Set Latin vertical metrics
# -*- coding: utf-8 -*-
__doc__="""
Sets vertical metrics for a whole Latin font according to Google's recommendations (https://github.com/googlefonts/gf-docs/blob/main/VerticalMetrics/README.md)"""

Font = Glyphs.font

a_z = "a b c d e f g h i j k l m n o p q r s t u v w x y z".split(" ")
upm_multiplier = 1.2
upm = Font.upm
tallest = 0
tallest_glyph = ""
shortest = 0
shortest_glyph = ""
Agrave_height = 0
H_height = 0
a_z_min = 0
shortest_a_z = ""

print("Measuring %s glyphs across %s masters..." % (len(Font.glyphs), len(Font.masters)))
for glyph in Font.glyphs:
	if glyph.export == True:
		for layer in glyph.layers:
			if layer.isMasterLayer or layer.isSpecialLayer:
					measure_layer = layer.copyDecomposedLayer()
					if measure_layer.shapes:
						for path in measure_layer.shapes:
							for node in path.nodes:
								if(node.type != "offcurve"):
									if node.y > tallest:
										tallest = node.y
										tallest_glyph = glyph.name 
									if node.y < shortest:
										shortest = node.y
										shortest_glyph = glyph.name
									if glyph.name == "Agrave":
										if node.y > Agrave_height:
											Agrave_height = node.y
									if glyph.name == "H":
										if node.y > H_height:
											H_height = node.y
									if glyph.name in a_z:
										if node.y < a_z_min:
											a_z_min = node.y
											shortest_a_z = glyph.name

win_ascent = tallest + abs(shortest)
win_descent = abs(shortest) 

typo_ascender = (upm * upm_multiplier - H_height) / 2 + H_height
typo_descender = -((upm * upm_multiplier - H_height) / 2)

if typo_ascender < Agrave_height:
	typo_ascender = Agrave_height

hhea_ascender = typo_ascender
hhea_descender = typo_descender

typo_line_gap = 0
hhea_line_gap = typo_line_gap

print("""
Tallest glyph: %s (%s)
Shortest glyph: %s (%s)
H height: %s
Shortest of a-z: %s (%s)

Setting new vertical metrics and Use Typo Metrics to true:
typoAscender, hheaAscender: %s
typoDescender, hheaDescender: %s
winAscent: %s
winDescent: %s
typoLineGap: 0
hheaLineGap 0
""" % (tallest_glyph, tallest ,shortest_glyph, shortest, H_height, shortest_a_z, a_z_min, typo_ascender, typo_descender, win_ascent, win_descent))

Font.customParameters["Use Typo Metrics"] = True	

for master in Font.masters:
	master.customParameters["typoAscender"] = typo_ascender
	master.customParameters["typoDescender"] = typo_descender
	master.customParameters["hheaAscender"] = hhea_ascender
	master.customParameters["hheaDescender"] = hhea_descender
	master.customParameters["typoLineGap"] = typo_line_gap
	master.customParameters["hheaLineGap"] = hhea_line_gap
	master.customParameters["winAscent"] = win_ascent
	master.customParameters["winDescent"] = win_descent

print("...done!")