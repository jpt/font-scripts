
#MenuTitle: Build circled glyphs from components
# -*- coding: utf-8 -*-
__doc__="""
Builds circled numbers and letters (.blackCircled and .circled) from specificied glyphs that have already been shrunk to size. Supports letters and numbers. Centers vertically along the capheight. First you need to create small letters that end with .small e.g. A.small, B.small. You could use .sc instead, and use lowercase names if you wanted, etc - edit the letter_suffix variable. Supply numbers with a given suffix as well (variable number_suffix); dnom in used by default.
"""

from Foundation import NSClassFromString
font = Glyphs.font

# User settings

circle_diameter_default = 960
letter_suffix = "small"
number_suffix = "dnom"
letter_sources = []
number_sources = []
black_circle_name = "_blackCircle.circle"
stroke_circle_name = "_strokeCircle.circle"
letters = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z".split(" ")
numbers = "zero one two three four five six seven eight nine".split(" ")

build_from_letters = []
build_from_numbers = []
to_build_letters_black = []
to_build_numbers_black = []

to_build_letters_stroke = []
to_build_numbers_stroke = []


contrast = []
curve_tension = 58

for letter in letters:
	glyph_name = letter + "." + letter_suffix
	build_from_letters.append(glyph_name)
	stroke_circle_glyph = letter + ".circled"
	to_build_letters_stroke.append(stroke_circle_glyph)
	black_circle_glyph = letter		 + ".blackCircled"
	to_build_letters_black.append(black_circle_glyph)
	
for number in numbers:
	glyph_name = number + "." + number_suffix
	build_from_numbers.append(glyph_name)
	stroke_circle_glyph = number + ".circled"
	to_build_numbers_stroke.append(stroke_circle_glyph)
	black_circle_glyph = number + ".blackCircled"
	to_build_numbers_black.append(black_circle_glyph)
	
def makeCircle(circle_diameter):
	circle_diameter = round(circle_diameter)
	layer.width = circle_diameter
	
	layer.LSB = 0
	layer.RSB = 0
	
	pen = layer.getPen()
	
	mid_x = circle_diameter/2
	mid_y = mid_x
	
	pt1 = mid_x, 0
	pt2 = 0, mid_y
	pt3 = mid_x, circle_diameter 
	pt4 = circle_diameter, mid_y

	pen.moveTo(pt1)
	pen.curveTo((mid_y-handle_length,0),(0, mid_x - handle_length), pt2)
	pen.curveTo((0,circle_diameter-(mid_x-handle_length)),(mid_y-handle_length,circle_diameter), pt3)
	pen.curveTo((circle_diameter-(mid_x-handle_length),circle_diameter),(circle_diameter,mid_x+handle_length), pt4)
	pen.curveTo((circle_diameter,mid_x-handle_length),(circle_diameter-(mid_x-handle_length),0), pt1)
	
	pen.closePath()
	layer.removeOverlap()
	pen.endPath()
	
	
for layer in font.glyphs["%s.%s" % ("H",letter_suffix)].layers:
	if layer.isMasterLayer:
		measure_y = layer.bounds.size.height / 4
		measure_x = layer.width / 2
		start = 0
		stop = layer.width
		intersections = layer.intersectionsBetweenPoints((start, measure_y), (stop, measure_y))
		h = intersections[2].x - intersections[1].x
		start = 0
		stop = layer.master.capHeight
		intersections = layer.intersectionsBetweenPoints((measure_x, start), (measure_x, stop))
		v = intersections[-2].y - intersections[1].y				
		contrast.append((h,v))

if not font.glyphs[black_circle_name]:
	glyph = GSGlyph(black_circle_name)
	font.glyphs.append(glyph)
	
	for i, layer in enumerate(glyph.layers):
		layer.width = circle_diameter_default
		handle_length = round((circle_diameter_default/2) * (curve_tension / 100))

		makeCircle(circle_diameter_default)
		overshoot = layer.master.metrics[1].overshoot # frm capHeight)
		layer.applyTransform((
			1, # x scale factor
			0.0, # x skew factor
			0.0, # y skew factor
			1, # y scale factor
			0.0, # x position
			-overshoot  # y position
		))
		layer.applyTransform((
			1, # x scale factor
			0.0, # x skew factor
			0.0, # y skew factor
			1, # y scale factor
			0.0, # x position
			-overshoot  # y position
		))
		center_on_cap = ((circle_diameter_default - layer.master.capHeight) / 2) * -1
		layer.applyTransform((
			1, # x scale factor
			0.0, # x skew factor
			0.0, # y skew factor
			1, # y scale factor
			0.0, # x position
			center_on_cap,  # y position
		))
		if layer.paths[0].direction != 1:
			layer.paths[0].reverse()
	glyph.leftMetricsKey = "=50"
	glyph.rightMetricsKey = "=50"
	for layer in glyph.layers:
		layer.syncMetrics()
	for layer in glyph.layers:
		layer.syncMetrics()

if not font.glyphs[stroke_circle_name]:
	glyph = GSGlyph(stroke_circle_name)
	font.glyphs.append(glyph)
	for i, layer in enumerate(glyph.layers):
		circle_diameter_stroke = circle_diameter_default - contrast[i][1]
		layer.width = circle_diameter_stroke
		layer.LSB=0
		layer.RSB=0
		h = contrast[i][0]
		v = contrast[i][1]
		#v = contrast[i][1] *0.666
		#h = round(v * 1.13)
		handle_length = round((circle_diameter_stroke/2) * (curve_tension / 100))		
		makeCircle(circle_diameter_stroke)
		overshoot = layer.master.metrics[1].overshoot # frm capHeight		
		layer.correctPathDirection()				
		offsetFilter = NSClassFromString("GlyphsFilterOffsetCurve")
		
		offsetFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_metrics_error_shadow_capStyleStart_capStyleEnd_keepCompatibleOutlines_(
			layer,
			h / 2, v / 2, # horizontal and vertical offset
			True,     # if True, creates a stroke
			False,     # if True, distorts resulting shape to vertical metrics
			0.5,       # stroke distribution to the left and right, 0.5 = middle
			None, None, None, 0, 0, False)
		layer.correctPathDirection()
		overshoot = layer.master.metrics[1].overshoot # frm capHeight
		layer.applyTransform((
			1, # x scale factor
			0.0, # x skew factor
			0.0, # y skew factor
			1, # y scale factor
			0.0, # x position
			(v/2)-overshoot
		))
		center_on_cap = ((circle_diameter_default - layer.master.capHeight) / 2) * -1
		layer.applyTransform((
			1, # x scale factor
			0.0, # x skew factor
			0.0, # y skew factor
			1, # y scale factor
			0.0, # x position
			center_on_cap,  # y position
		))
	glyph.leftMetricsKey = "=50"
	glyph.rightMetricsKey = "=50"
	for layer in glyph.layers:
		layer.syncMetrics()
	for layer in glyph.layers:
		layer.syncMetrics()

def buildCircledGlyphs(to_build,build_from,circle_type):
	for i,build_glyph in enumerate(to_build):
		if not font.glyphs[build_glyph]:
			new_glyph = GSGlyph(build_glyph)
			font.glyphs.append(new_glyph)		
			new_glyph.leftMetricsKey = "=50"
			new_glyph.rightMetricsKey = "=50"


			for layer in new_glyph.layers:
				circle_component = GSComponent(circle_type)
				build_component = GSComponent(build_from[i])
				circle_component.automaticAlignment = True	
				circle_component.locked = True		
				build_component.automaticAlignment = False
				layer.components.append(circle_component)
				layer.components.append(build_component)
				layer.syncMetrics()
				
				
				LSB = layer.components[1].componentLayer.LSB
				RSB = layer.components[1].componentLayer.RSB
				spacing_diff = 0
				if LSB > RSB:
					spacing_diff = (LSB-RSB)
				
				overshoot = layer.master.metrics[1].overshoot

				component_x = (layer.width / 2) - build_component.bounds.size.width / 2 - build_component.bounds.origin.x			
				component_y = (circle_diameter_default - overshoot) / 2 - build_component.bounds.size.height / 2 - overshoot
				
				build_component.applyTransform((
					1, # x scale factor
					0.0, # x skew factor
					0.0, # y skew factor
					1, # y scale factor
					component_x, # x position
					0.0,  # y position
				))
				build_component.applyTransform((
					1, # x scale factor
					0.0, # x skew factor
					0.0, # y skew factor
					1, # y scale factor
					0.0, # x position
					component_y,  # y position
				))
				build_component.applyTransform((
					1, # x scale factor
					0.0, # x skew factor
					0.0, # y skew factor
					1, # y scale factor
					spacing_diff, # x position
					0,  # y position
				))
				center_on_cap = ((circle_diameter_default - layer.master.capHeight) / 2) * -1
				build_component.applyTransform((
					1, # x scale factor
					0.0, # x skew factor
					0.0, # y skew factor
					1, # y scale factor
					0.0, # x position
					center_on_cap,  # y position
				))
			for layer in new_glyph.layers:
				layer.syncMetrics()
			for layer in new_glyph.layers:
				layer.syncMetrics()

buildCircledGlyphs(to_build_letters_black, build_from_letters, black_circle_name)
buildCircledGlyphs(to_build_numbers_black, build_from_numbers, black_circle_name)

buildCircledGlyphs(to_build_letters_stroke, build_from_letters, stroke_circle_name)
buildCircledGlyphs(to_build_numbers_stroke, build_from_numbers, stroke_circle_name)
