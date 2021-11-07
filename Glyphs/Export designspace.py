# MenuTitle: Export designspace
__doc__ = """
Export designspace files to your UFO export folder  
"""

import os
from re import findall, match
from fontTools.designspaceLib import (
	DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor, RuleDescriptor)

isVF = True #todo dont do this

def getSources(font,doc):
	sources = []
	for i, master in enumerate(font.masters):
		s = SourceDescriptor()
		fontName = "%s %s" % (font.fontName, master.name) 
		s.filename = "%s.ufo" % fontName
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
		font_name = font.fontName
		for i,axis in enumerate(axes):
			font_name = "%s %s %s" % (font_name, axes[i], font.axes[i].axisTag)
		s.filename = "%s.ufo" % font_name
		sources.append(s)
	return sources

def addAxes(doc,font):
	axes_to_return = []
	for i, axis in enumerate(font.axes):
		try:
			axisMap = font.customParameters["Axis Mappings"][axis.axisTag]
		except:
			continue
		a = AxisDescriptor()
		axisMin = None
		axisMax = None
		for k in sorted(axisMap.keys()):
			a.map.append((axisMap[k], k))
			if axisMin is None or axisMap[k] < axisMin:
				axisMin = axisMap[k]
			if axisMax is None or axisMap[k] > axisMax:
				axisMax = axisMap[k]
		a.maximum = axisMax
		a.minimum = axisMin
		a.default = axisMin
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
			styleMapStyle = "bold"
		elif instance.isItalic:
			styleMapStyle = "italic"
		else:
			styleMapStyle = "regular"
		if isVF:
			family_name = font.familyName
		else:
			family_name = instance.preferredFamily
		ins.familyName = family_name
		if isVF:
			style_name = instance.variableStyleName
		else:
			style_name = instance.name
		ins.styleName = style_name
		ins.filename = "%s.ufo" % postScriptName
		ins.postScriptFontName = postScriptName
		ins.styleMapFamilyName = "%s %s" % (instance.preferredFamily, instance.name)
		ins.styleMapStyleName = styleMapStyle
		axisName = {}
		for i, axisValue in enumerate(instance.axes):
			axisName[font.axes[i].name] = axisValue
		ins.location = axisName
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
	filePath = font.parent.fileURL().path()
	fontName = font.fontName
	folderName = os.path.dirname(filePath)
	ufoFolder = os.path.join(folderName)
	designspaceFilePath = "%s/%s.designspace" % (ufoFolder, fontName)
	doc.write(designspaceFilePath)
	os.system("open %s" % ufoFolder.replace(" ", "\ "))
main()