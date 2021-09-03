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
math_width = []
hyphen_weight = []
hyphen_factor = 2
contrast_factor = 0.985
multiply_factor = 1.01
divide_factor = 1.66
n_distance = []

for layer in font.glyphs['n'].layers:
	n_distance.append(layer.LSB + layer.RSB)

for layer in font.glyphs['zero.tf'].layers:
	if layer.isMasterLayer:
		zero_width.append(layer.width)

for layer in font.glyphs['hyphen'].layers:
	if layer.isMasterLayer:
		hyphen_layer = layer.copyDecomposedLayer()
		hyphen_lsb.append(layer.LSB)
		measure_x = hyphen_layer.width / 2
		start = layer.master.capHeight
		stop = layer.master.descender
		intersections = hyphen_layer.intersectionsBetweenPoints((measure_x, start), (measure_x, stop))
		stem_height = intersections[-2].y - intersections[-3].y
		master_contrast.append((stem_height,round(stem_height*contrast_factor)))

for i in range(0,len(font.masters)):
	math_width.append(zero_width[i] - hyphen_lsb[i])

if not font.glyphs['minus']:	
	font.glyphs.append(GSGlyph('minus'))
	for i,layer in enumerate(font.glyphs['minus'].layers):
		h,v = master_contrast[i]
		layer.width = zero_width[i]
		line_width = layer.width - (hyphen_lsb[i] * hyphen_factor)
		y_start = layer.master.capHeight / 2
		y_end = y_start
		x_start = hyphen_lsb[i] * hyphen_factor
		x_end = line_width
		pen = layer.getPen()
		pen.moveTo( (x_start, y_start))
		pen.lineTo( (x_end, y_start))
		pen.endPath()
		pen.closePath()
		pen.endPath()
		offsetFilter = NSClassFromString("GlyphsFilterOffsetCurve")
		offsetFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_metrics_error_shadow_capStyleStart_capStyleEnd_keepCompatibleOutlines_(
			layer,
			h/2 ,v /2, # horizontal and vertical offset
			True,     # if True, creates a stroke
			False,     # if True, distorts resulting shape to vertical metrics
			0.5,       # stroke distribution to the left and right, 0.5 = middle
			None, None, None, 0, 0, False )
		layer.correctPathDirection()
		
if not font.glyphs['plus']:
	font.glyphs.append(GSGlyph('plus'))
	for i,layer in enumerate(font.glyphs['plus'].layers):
		h,v = master_contrast[i]
		layer.width = zero_width[i]
		line_width = layer.width - (hyphen_lsb[i] * hyphen_factor)
		y_start = layer.master.capHeight / 2
		y_end = y_start
		x_start = hyphen_lsb[i] * hyphen_factor
		x_end = line_width
		pen = layer.getPen()
		pen.moveTo( (x_start, y_start))
		pen.lineTo( (x_end, y_start))
		pen.endPath()
		pen.closePath()
		pen.endPath()
		
		x_start = layer.width / 2
		x_end = x_start
		y_start = ((layer.master.capHeight + hyphen_lsb[i] * hyphen_factor) - line_width) / 2
		y_end = layer.master.capHeight - y_start

		pen = layer.getPen()
		pen.moveTo( (x_start, y_start))
		pen.lineTo( (x_end, y_end))
		pen.endPath()
		pen.closePath()
		pen.endPath()
		
		v, h = h, v
		offsetFilter = NSClassFromString("GlyphsFilterOffsetCurve")
		offsetFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_metrics_error_shadow_capStyleStart_capStyleEnd_keepCompatibleOutlines_(
			layer,
			v/2, h/2, # horizontal and vertical offset
			True,     # if True, creates a stroke
			False,     # if True, distorts resulting shape to vertical metrics
			0.5,       # stroke distribution to the left and right, 0.5 = middle
			None, None, None, 0, 0, True )
		layer.correctPathDirection()

if not font.glyphs['equal']:	
	font.glyphs.append(GSGlyph('equal'))
	for i,layer in enumerate(font.glyphs['equal'].layers):
		equal_height = font.glyphs['minus'].layers[i].bounds.size.height
		layer.width = font.glyphs['minus'].layers[i].width
		top_equal = GSComponent(font.glyphs['minus'])
		top_equal.y = top_equal.y + (equal_height/2) + (n_distance[i]/2)	
		bottom_equal = GSComponent(font.glyphs['minus'])
		bottom_equal.y = bottom_equal.y - (equal_height/2) - (n_distance[i]/2)	
		components = [top_equal, bottom_equal]
		for component in components:
			layer.components.append(component)

if not font.glyphs['multiply']:
	font.glyphs.append(GSGlyph('multiply'))
	for i,layer in enumerate(font.glyphs['multiply'].layers):
		h,v = master_contrast[i]
		layer.width = zero_width[i]
		line_width = round((layer.width - (hyphen_lsb[i] * hyphen_factor)) * multiply_factor)
		y_start = layer.master.capHeight / 2
		y_end = y_start
		x_start = (layer.width - line_width) / 2
		
		x_end = x_start + line_width
		pen = layer.getPen()
		pen.moveTo( (x_start, y_start))
		pen.lineTo( (x_end, y_start))
		pen.endPath()
		pen.closePath()
		pen.endPath()
		
		x_start = layer.width / 2
		x_end = x_start
		y_start = (layer.master.capHeight - line_width) / 2
		y_end = y_start + line_width

		pen = layer.getPen()
		pen.moveTo( (x_start, y_start))
		pen.lineTo( (x_end, y_end))
		pen.endPath()
		pen.closePath()
		pen.endPath()
		
		v, h = h, v
		offsetFilter = NSClassFromString("GlyphsFilterOffsetCurve")
		offsetFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_metrics_error_shadow_capStyleStart_capStyleEnd_keepCompatibleOutlines_(
			layer,
			v/2, h/2, # horizontal and vertical offset
			True,     # if True, creates a stroke
			False,     # if True, distorts resulting shape to vertical metrics
			0.5,       # stroke distribution to the left and right, 0.5 = middle
			None, None, None, 0, 0, True )
		layer.correctPathDirection()
		rotate_transform = NSAffineTransform()
		rotate_transform.rotate(45, ((layer.width/2),(layer.master.capHeight/2)))
		layer.transform(rotate_transform)
		
if not font.glyphs['divide']:	
	font.glyphs.append(GSGlyph('divide'))
	for i,layer in enumerate(font.glyphs['divide'].layers):
		layer.width = font.glyphs['minus'].layers[i].width
		divide_height = font.glyphs['minus'].layers[i].bounds.size.height
		divide_bottom = font.glyphs['minus'].layers[i].bounds.origin.y
		dot_accent_lsb = font.glyphs['dotaccentcomb'].layers[i].LSB
		dot_accent_width = font.glyphs['dotaccentcomb'].layers[i].bounds.size.width
		dot_accent_height = font.glyphs['dotaccentcomb'].layers[i].bounds.size.height
		dot_accent_y = font.glyphs['dotaccentcomb'].layers[i].bounds.origin.y
		dot_accent_distance = font.glyphs['dotaccentcomb'].layers[i].bounds.origin.y - font.glyphs['dotaccentcomb'].layers[i].master.xHeight
		minus = GSComponent(font.glyphs['minus'])
		minus.x = 0
		minus.y = 0
		dot_top =  GSComponent(font.glyphs['dotaccentcomb'])
		dot_bottom =  GSComponent(font.glyphs['dotaccentcomb'])
		dot_top.automaticAlignment = False
		dot_bottom.automaticAlignment = False
		
		dot_top.x = (layer.width / 2) - (dot_accent_width/2) - dot_accent_lsb
		dot_bottom.x = (layer.width / 2) - (dot_accent_width/2) - dot_accent_lsb
		
		dot_top.y = (layer.master.capHeight / 2) - dot_accent_y + (divide_height / 2) + dot_accent_distance
		dot_bottom.y = divide_bottom - dot_accent_y - dot_accent_height - dot_accent_distance

		components = [minus,dot_top,dot_bottom]
		for component in components:
			layer.components.append(component)
