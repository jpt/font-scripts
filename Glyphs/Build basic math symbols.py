#MenuTitle: Build basic math symbols
# -*- coding: utf-8 -*-

__doc__="""
Builds the following math symbols: plus, minus, equal, divide. Relies on measurements from n, hyphen, zero.tf, and dotaccentcomb.
"""

from Foundation import NSClassFromString, NSAffineTransform
import copy

font = Glyphs.font

master_contrast = []
zero_width = []
hyphen_lsb = []
n_distance = []
hyphen_factor = 1.1
hyphen_thick_factor = 0.9
contrast_factor = 0.95
multiply_factor = 1.01
equal_factor = 1.3

for layer in font.glyphs['zero.tf'].layers:
	if layer.isMasterLayer:
		zero_width.append(layer.width)

for layer in font.glyphs['n'].layers:
	if layer.isMasterLayer:
		measure_y = layer.master.xHeight/3
		start = 0
		stop = layer.width
		intersections = layer.intersectionsBetweenPoints((start, measure_y), (stop, measure_y))
		n_distance.append(intersections[1].x + (stop-intersections[-2].x))

for layer in font.glyphs['hyphen'].layers:
	if layer.isMasterLayer:
		hyphen_layer = layer.copyDecomposedLayer()
		hyphen_lsb.append(layer.LSB * hyphen_factor)
		measure_x = hyphen_layer.width / 2
		start = layer.master.capHeight
		stop = layer.master.descender
		intersections = hyphen_layer.intersectionsBetweenPoints((measure_x, start), (measure_x, stop))
		stem_height = (intersections[-2].y - intersections[-3].y) * hyphen_thick_factor
		master_contrast.append((stem_height, round(stem_height * contrast_factor)))

offsetFilter = NSClassFromString("GlyphsFilterOffsetCurve")

if not font.glyphs['minus']:
	glyph = GSGlyph('minus')
	font.glyphs.append(glyph)
	for i, layer in enumerate(glyph.layers):
		h, v = master_contrast[i]
		layer.width = zero_width[i]
		line_width = layer.width - hyphen_lsb[i]
		y_start = layer.master.capHeight / 2
		y_end = y_start
		x_start = hyphen_lsb[i]
		x_end = line_width
		pen = layer.getPen()
		pen.moveTo((x_start, y_start))
		pen.lineTo((x_end, y_start))
		pen.endPath()
		offsetFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_metrics_error_shadow_capStyleStart_capStyleEnd_keepCompatibleOutlines_(
			layer,
			h / 2, v / 2, # horizontal and vertical offset
			True,     # if True, creates a stroke
			False,     # if True, distorts resulting shape to vertical metrics
			0.5,       # stroke distribution to the left and right, 0.5 = middle
			None, None, None, 0, 0, False)
		layer.correctPathDirection()

if not font.glyphs['plus']:
	glyph = GSGlyph('plus')
	font.glyphs.append(glyph)
	for i, layer in enumerate(glyph.layers):
		h,v = master_contrast[i]
		layer.width = zero_width[i]
		line_width = layer.width - hyphen_lsb[i]
		y_start = layer.master.capHeight / 2
		y_end = y_start
		x_start = hyphen_lsb[i]
		x_end = line_width
		pen = layer.getPen()
		pen.moveTo((x_start, y_start))
		pen.lineTo((x_end, y_start))
		
		x_start = layer.width / 2
		x_end = x_start
		y_start = (layer.master.capHeight + hyphen_lsb[i] - line_width) / 2
		y_end = layer.master.capHeight - y_start

		pen.moveTo((x_start, y_start))
		pen.lineTo((x_end, y_end))
		pen.endPath()

		offsetFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_metrics_error_shadow_capStyleStart_capStyleEnd_keepCompatibleOutlines_(
			layer,
			h / 2, v / 2, # horizontal and vertical offset
			True,     # if True, creates a stroke
			False,     # if True, distorts resulting shape to vertical metrics
			0.5,       # stroke distribution to the left and right, 0.5 = middle
			None, None, None, 0, 0, True)
		layer.correctPathDirection()

if not font.glyphs['equal']:
	glyph = GSGlyph('equal')
	font.glyphs.append(glyph)
	for i,layer in enumerate(glyph.layers):
		minusLayerBounds = font.glyphs['minus'].layers[i].bounds
		equal_height = minusLayerBounds.size.height
		layer.width = zero_width[i]
		y_offset = (equal_height/2) + (n_distance[i]/2)

		top_equal = GSComponent('minus', (0, y_offset))
		layer.components.append(top_equal)

		bottom_equal = GSComponent('minus', (0, -y_offset))
		layer.components.append(bottom_equal)

if not font.glyphs['multiply']:
	glyph = GSGlyph('multiply')
	font.glyphs.append(glyph)
	for i, layer in enumerate(glyph.layers):
		h,v = master_contrast[i]
		layer.width = zero_width[i]
		line_width = round((layer.width - hyphen_lsb[i]) * multiply_factor)
		y_start = layer.master.capHeight / 2
		y_end = y_start
		x_start = (layer.width - line_width) / 2
		
		x_end = x_start + line_width
		pen = layer.getPen()
		pen.moveTo((x_start, y_start))
		pen.lineTo((x_end, y_start))
		
		x_start = layer.width / 2
		x_end = x_start
		y_start = (layer.master.capHeight - line_width) / 2
		y_end = y_start + line_width

		pen.moveTo((x_start, y_start))
		pen.lineTo((x_end, y_end))
		pen.endPath()

		offsetFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_metrics_error_shadow_capStyleStart_capStyleEnd_keepCompatibleOutlines_(
			layer,
			h / 2, v / 2, # horizontal and vertical offset
			True,     # if True, creates a stroke
			False,     # if True, distorts resulting shape to vertical metrics
			0.5,       # stroke distribution to the left and right, 0.5 = middle
			None, None, None, 0, 0, True)
		layer.correctPathDirection()
		rotate_transform = NSAffineTransform()
		rotate_transform.rotate(45, ((layer.width / 2), (layer.master.capHeight / 2)))
		layer.transform(rotate_transform)
		
if not font.glyphs['divide']:
	glyph = GSGlyph('divide')
	font.glyphs.append(glyph)
	for i, layer in enumerate(glyph.layers):
		minusLayerBounds = font.glyphs['minus'].layers[i].bounds
		layer.width = zero_width[i]
		divide_height = minusLayerBounds.size.height
		divide_bottom = minusLayerBounds.origin.y
		dotaccentBounds = font.glyphs['dotaccentcomb'].layers[i].bounds
		dot_accent_x = dotaccentBounds.origin.x
		dot_accent_width = dotaccentBounds.size.width
		dot_accent_height = dotaccentBounds.size.height
		dot_accent_y = dotaccentBounds.origin.y
		dot_accent_distance = dotaccentBounds.origin.y - font.masters[i].xHeight
		
		minus = GSComponent('minus')
		
		x = (layer.width / 2) - (dot_accent_width / 2) - dot_accent_x
		y = (layer.master.capHeight / 2) - dot_accent_y + (divide_height / 2) + dot_accent_distance
		dot_top = GSComponent('dotaccentcomb', (x, y))
		
		x = (layer.width / 2) - (dot_accent_width / 2) - dot_accent_x
		y = divide_bottom - dot_accent_y - dot_accent_height - dot_accent_distance
		dot_bottom = GSComponent('dotaccentcomb', (x, y))
		dot_top.automaticAlignment = False
		dot_bottom.automaticAlignment = False

		layer.components.append(minus)
		layer.components.append(dot_top)
		layer.components.append(dot_bottom)
