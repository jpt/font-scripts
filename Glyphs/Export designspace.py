# MenuTitle: Export designspace
__doc__ = """
Export designspace files to your UFO export folder  
"""

import os
from fontTools.designspaceLib import (
	DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor ) ## TODO import RuleDescriptor for rules

is_vf = True #todo dont do this

def getVariableFontFamily(font):
	for instance in font.instances:
		if not instance.familyName:
			return instance.name
	return None
		
def getSources(font,doc):
	sources = []
	for i, master in enumerate(font.masters):
		s = SourceDescriptor()
		if is_vf:
			font_name = "%s %s" % (font.familyName, getVariableFontFamily(font))
		else:
			font_name = "%s %s" % (font.familyName, master.name) 
		s.filename = "%s.ufo" % font_name
		locations = dict()
		for x, axis in enumerate(master.axes):
			locations[font.axes[x].name] = axis
		s.location = locations
		if i == 0: # Todo look for variable font origin and copy from there, or ask for user input
			s.copyLib = True
			s.copyFeatures = True
			s.copyGroups = True
			s.copyInfo = True
		sources.append(s)
	return sources

def addSources(doc,sources):
	for source in sources:
		doc.addSource(source)

def getSpecialLayerAxes(font):
	special_layer_axes = []
	for glyph in font.glyphs:
		for layer in glyph.layers:
			if layer.isSpecialLayer and layer.attributes['coordinates']:
				#if layer.axes not in special_layer_axes:
				layer_axes = dict()
				for i,coords in enumerate(layer.attributes['coordinates']):				
					layer_axes[font.axes[i].name] = layer.attributes['coordinates'][coords]
				if layer_axes not in special_layer_axes:
					special_layer_axes.append(layer_axes)			
	return special_layer_axes

def getSpecialSources(font,doc):
	sources = []
	special_layer_axes = getSpecialLayerAxes(font)
	for i,special_layer_axis in enumerate(special_layer_axes):
		axes = list(special_layer_axis.values())
		s = SourceDescriptor()
		s.location = special_layer_axis
		if is_vf:
			font_name = "%s %s" % (font.familyName, getVariableFontFamily(font))
		else:
			font_name = font.familyName
		for i,axis in enumerate(axes):
			font_name = "%s %s %s" % (font_name, axes[i], font.axes[i].axisTag)
		s.filename = "%s.ufo" % font_name
		sources.append(s)
	return sources

def addAxes(doc,font):
	axes_to_return = []
	for i, axis in enumerate(font.axes):
		try:
			axis_map = font.customParameters["Axis Mappings"][axis.axisTag]
		except:
			continue
		a = AxisDescriptor()
		axis_min = None
		axis_max = None
		for k in sorted(axis_map.keys()):
			a.map.append((axis_map[k], k))
			if axis_min is None or axis_map[k] < axis_min:
				axis_min = axis_map[k]
			if axis_max is None or axis_map[k] > axis_max:
				axis_max = axis_map[k]
		a.maximum = axis_max
		a.minimum = axis_min
		a.default = axis_min
		a.name = axis.name
		a.tag = axis.axisTag
		doc.addAxis(a)

def getInstances(font):
	instances_to_return = []
	for instance in font.instances:
		if not instance.active:
			continue
		if not instance.familyName: # skip VF export settings-as-instances
			continue
		ins = InstanceDescriptor()
		postScriptName = instance.fontName
		if instance.isBold:
			style_map_style = "bold"
		elif instance.isItalic:
			style_map_style = "italic"
		else:
			style_map_style = "regular"
		if is_vf:
			family_name = "%s %s" % (font.familyName, getVariableFontFamily(font))
		else:
			family_name = instance.preferredFamily
		ins.familyName = family_name
		if is_vf:
			style_name = instance.variableStyleName
		else:
			style_name = instance.name
		ins.styleName = style_name
		ins.filename = "%s.ufo" % postScriptName
		ins.postScriptFontName = postScriptName
		ins.styleMapFamilyName = "%s %s" % (instance.preferredFamily, instance.name)
		ins.styleMapStyleName = style_map_style
		axis_name = {}
		for i, axis_value in enumerate(instance.axes):
			axis_name[font.axes[i].name] = axis_value
		ins.location = axis_name
		instances_to_return.append(ins)
	return instances_to_return

def addInstances(doc,instances):
	for instance in instances:
		doc.addInstance(instance)

def updateFeatures(font):
	# Update auto features 
	for feature in font.features:
		if feature.automatic:
			feature.update()

def getDesignSpaceDocument(font):
	doc = DesignSpaceDocument()
	addAxes(doc,font)
	sources = getSources(font,doc)
	addSources(doc,sources)
	special_sources = getSpecialSources(font,doc)
	addSources(doc,special_sources)
	instances = getInstances(font)
	addInstances(doc,instances)
	return doc

def main():
	font = Glyphs.font
	updateFeatures(font)
	doc = getDesignSpaceDocument(font)
	try:
		file_path = font.parent.fileURL().path()
		font_name = font.fontName
		folder_name = os.path.dirname(file_path)
		ufo_folder = os.path.join(folder_name)
		designspaceFilePath = "%s/%s.designspace" % (ufo_folder, font_name)
		doc.write(designspaceFilePath)
		os.system("open %s" % ufo_folder.replace(" ", "\ "))
	except:
		print("You need to save the file you're in.")
main()