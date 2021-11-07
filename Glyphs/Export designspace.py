# MenuTitle: Export designspace
__doc__ = """
Export designspace files to your UFO export folder  
"""
import os, re
from fontTools.designspaceLib import (
	DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor, RuleDescriptor ) 

is_vf = True #todo dont do this

def getOriginMaster(font):
	master_id = None
	for cp in font.customParameters:
		if cp.name == "Variable Font Origin":
			master_id = cp.value
	if master_id is None:
		return font.masters[0].id
	return master_id
			
def getBoundsByTag(tag, font):
	min = None
	max = None
	for i,axis in enumerate(font.axes):
		if axis.axisTag != tag:
			continue
		for master in font.masters:
		   coord = master.axes[i]
		   if min == None or coord < min:
			   min = coord
		   if max == None or coord > max:
			   max = coord
	return [min,max]

def exportSingleUFObyMaster(master, ufoFilePath):
	exporter = NSClassFromString('GlyphsFileFormatUFO').alloc().init()
	exporter.setFontMaster_(master)
	exporter.writeUfo_toURL_error_(
		master, NSURL.fileURLWithPath_(ufoFilePath), None)

def exportUFOAndBuildDesignspace(doc, font, ufoFolder):
	for i, master in enumerate(font.masters):
		s = SourceDescriptor()
		
		filePath = font.parent.fileURL().path()
		fontName = font.fontName
		fileName = "%s - %s.glyphs" % (font.fontName, master.name)
		ufoFileName = fileName.replace('.glyphs', '.ufo')
		folderName = os.path.dirname(filePath)
		ufoFilePath = os.path.join(ufoFolder, ufoFileName)
		exportSingleUFObyMaster(master, ufoFilePath)

	return filePath, ufoFolder

def createUFOmastersForBraceLayers(font, doc, tempFolder, ufoFolder):
	# for now we will focus only on intermediate masters
	# we could do it in one go, but this seems more legible
	# gathering special layers
	
	special_layers = getSpecialLayers(font)
	
	# creating .glyphs file per special layer
	for layer in special_layers:
		
		layer_values_str = layer.name.strip("{}").split(",")
		layer_values = dict()
		layer_ufo_name = ""
		for i, txt in enumerate(layer_values_str):
			axis_name = font.axes[i].name
			value = float(txt)
			print(txt)
			if value % 1 == 0:
				value = int(value)
			layer_values[axis_name] = value
			layer_ufo_name += "%s %s " % (axis_name, value)
		
		layer_ufo_descrpition = layer_ufo_name.strip()
		layer_ufo_name = "( " + layer_ufo_descrpition + " )"

		fileName = "%s - %s.glyphs" % (font.fontName, layer_ufo_name)
		dst = os.path.join(tempFolder, fileName)
		src = font.parent.fileURL().path()
		shutil.copyfile(src, dst)
		print(dst)
		layerFont = Glyphs.open(dst, False)
		
		# delete glyphs that are not connected to the special layer
		glyphNamesToDelete = []
		for g in layerFont.glyphs:
			if g.name != layer.parent.name:
				glyphNamesToDelete.append(g.name)
				
		for name in glyphNamesToDelete:
			del(layerFont.glyphs[name])
		
		# delete unnescessary masters
		masterIndexesToDelete = [ 
				index for index,master in enumerate(layerFont.masters) if master.id != layer.associatedMasterId 
			]

		layerGlyph = layerFont.glyphs[layer.parent.name]
		layer.layerId = layerFont.masters[0].id
		layerFont.glyphs[layer.parent.name].layers[layerFont.masters[0].id] = layer
		for index in reversed(masterIndexesToDelete):
			del(layerFont.masters[index])
		ufoFile = fileName.replace(".glyphs", ".ufo")
		ufoFilePath = os.path.join(ufoFolder, ufoFile)
		exportSingleUFObyMaster(layerFont.masters[0], ufoFilePath)
		layerFont.close()
			
def getAxisNameByTag(font,tag):
	for axis in font.axes:
		if axis.axisTag == tag:
			return axis.name
			
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
		origin_master_id = getOriginMaster(font)
		if master.id == origin_master_id:
			s.copyLib = True
			s.copyFeatures = True
			s.copyGroups = True
			s.copyInfo = True
		sources.append(s)
	return sources

def addSources(doc,sources):
	for source in sources:
		doc.addSource(source)

def getSpecialLayers(font):
	special_layers = []
	for glyph in font.glyphs:
		for layer in glyph.layers:
			if layer.isSpecialLayer and layer.attributes['coordinates']:
				special_layers.append(layer)
	return special_layers

def getSpecialLayerAxes(font):
	special_layer_axes = []
	for layer in getSpecialLayers(font):
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

def getConditionsFromOT(font):
	feature_code = ""
	for feature_itr in font.features:
		for line in feature_itr.code.splitlines():
			if line.startswith("condition "):
				feature_code = feature_itr.code
	condition_index = 0
	condition_list = []
	replacement_list = [[]]
	
	for line in feature_code.splitlines():
		if line.startswith("condition"):
			conditions = []
			conditions_list = line.split(",")
			for condition in conditions_list:
				m = re.findall("< (\w{4})", condition)
				tag = m[0]
				axis_name = getAxisNameByTag(font,tag)
				m = re.findall("\d+(?:\.|)\d*", condition)
				cond_min = float(m[0])
				if len(m) > 1:
					cond_max = float(m[1])
					range_dict = dict(name=axis_name, minimum=cond_min, maximum=cond_max)	
				else:
					range_dict = dict(name=axis_name, minimum=cond_min)					
				conditions.append(range_dict)
			condition_list.append(conditions)
			condition_index = condition_index + 1
		elif line.startswith("sub"):	
			m = re.findall("sub (.*) by (.*);", line)[0]
			replace = (m[0],m[1])
			try:
				replacement_list[condition_index-1].append(replace)
			except:
				replacement_list.append(list())
				replacement_list[condition_index-1].append(replace)
	return [condition_list,replacement_list]

def applyConditionsToRules(doc,font,condition_list,replacement_list):
	rules = []
	for i,condition in enumerate(condition_list):
		r = RuleDescriptor()
		r.name = "Rule %s" % str(i+1)
		r.conditionSets.append(condition)
		for sub in replacement_list[i]:
			r.subs.append(sub)
		rules.append(r)
	doc.rules = rules

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
	[condition_list, replacement_list] = getConditionsFromOT(font)
	applyConditionsToRules(doc,font,condition_list,replacement_list)
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