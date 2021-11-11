# MenuTitle: Export UFO and designspace files
__doc__ = """
Exports UFO and designspace files. Supports substitutions defined in OT features, but not bracket layers. Brace layers supported, but not yet as support layers for Skateboard. With contributions from Rafał Buchner. Thanks to Frederik Berlaen and Joancarles Casasín for ideas that served as inspiration (https://robofont.com/documentation/how-tos/converting-from-glyphs-to-ufo/), and to the maintainers of designspaceLib.
"""

from GlyphsApp import GSInstance
import re
import os
import tempfile
import shutil
from AppKit import NSClassFromString, NSURL
from fontTools.designspaceLib import (
	DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor, RuleDescriptor)

is_vf = True  # To do: add vanilla interface for this
# Set to False if you want brace layers to be full masters
delete_unnecessary_glyphs = True


def getMutedGlyphs(font):
	__doc__ = "Provided a font object, returns an array of non-exporting glyphs to be added as muted glyphs in the designspace"
	return [glyph.name for glyph in font.glyphs if not glyph.export]


def getBoundsByTag(font, tag):
	__doc__ = """Provided a font object and an axis tag, returns an array in the form of [minimum, maximum] representing the bounds of an axis. 

Example use: 
min, max = getBoundsByTag(Glyphs.font,"wght")"""
	min = None
	max = None
	for i, axis in enumerate(font.axes):
		if axis.axisTag != tag:
			continue
		for master in font.masters:
			coord = master.axes[i]
			if min == None or coord < min:
				min = coord
			if max == None or coord > max:
				max = coord
	return [min, max]


def getOriginMaster(font):
	__doc__ = """Provided a font object, returns a string of the master ID referencing the master that is set to the variable font origin by custom paramter"""
	master_id = None
	for parameter in font.customParameters:
		if parameter.name == "Variable Font Origin":
			master_id = parameter.value
	if master_id is None:
		return font.masters[0].id
	return master_id


def getOriginCoords(font):
	__doc__ = """Provided a font object, returns an array of axis coordinates specified on the variable font origin master."""
	for parameter in font.customParameters:
		if parameter.name == "Variable Font Origin":
			master_id = parameter.value
	if master_id is None:
		master_id = font.masters[0].id
	for master in font.masters:
		if master.id == master_id:
			return list(master.axes)


def getAxisNameByTag(font, tag):
	__doc__ = """Provided a font object an axis tag, returns an axis name"""
	for axis in font.axes:
		if axis.axisTag == tag:
			return axis.name


def getVariableFontFamily(font):
	__doc__ = """Provided a font object, returns the name associated with a Variable Font Setting export"""
	for instance in font.instances:
		if not instance.familyName:
			return instance.name
	return None


def getFamilyName(font):
	__doc__ = """Provided a font object, returns a font family name"""
	if is_vf:
		family_name = "%s %s" % (font.familyName, getVariableFontFamily(font))
	else:
		family_name = font.familyName
	return family_name


def getFamilyNameWithMaster(font, master):
	__doc__ = """Provided a font object and a master, returns a font family name"""
	master_name = master.name
	if is_vf:
		font_name = "%s %s - %s" % (font.familyName,
									getVariableFontFamily(font), master_name)
	else:
		font_name = "%s - %s" % (font.familyName, master_name)
	return font_name


def getStyleNameWithAxis(font,axes):
	style_name = ""
	for i, axis in enumerate(axes):
		style_name = "%s %s %s" % (style_name, font.axes[i].name, axis)
	return style_name.strip()


def getNameWithAxis(font, axes):
	__doc__ = """Provided a font and a dict of axes for a brace layer, returns a font family name"""
	if is_vf:
		font_name = "%s %s -" % (font.familyName, getVariableFontFamily(font))
	else:
		font_name = font.familyName
	for i, axis in enumerate(axes):
		font_name = "%s %s %s" % (font_name, font.axes[i].name, axis)
	return font_name


def alignSpecialLayers(font):
	__doc__ = """Applies the same master ID referencing the variable font origin to all brace layers"""
	master_id = getOriginMaster(font)
	special_layers = getSpecialLayers(font)
	for layer in special_layers:
		layer.associatedMasterId = master_id


def getSources(font):
	__doc__ = """Provided a font object, creates and returns a designspaceLib SourceDescriptor"""
	sources = []
	for i, master in enumerate(font.masters):
		s = SourceDescriptor()
		font_name = getFamilyNameWithMaster(font, master)
		s.filename = "%s.ufo" % font_name
		s.familyName = getFamilyName(font)
		s.styleName = master.name
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
		s.mutedGlyphNames = getMutedGlyphs(font)
		sources.append(s)
	return sources


def addSources(doc, sources):
	__doc__ = """Provided a designspace document and array of source descriptors, adds those sources to the designspace doc."""
	for source in sources:
		doc.addSource(source)


def getSpecialLayers(font):
	__doc__ = """Provided a font object, returns a list of GSLayers that are brace layers (have intermediate master coordinates)."""

	return [l for g in font.glyphs for l in g.layers if l.isSpecialLayer and l.attributes['coordinates']]


def getSpecialLayerAxes(font):
	__doc__ = """Provided a font object, returns a list of dicts containing name and coordinate information for each axis"""
	special_layer_axes = []
	layers = getSpecialLayers(font)
	for layer in layers:
		layer_axes = dict()
		for i, coords in enumerate(layer.attributes['coordinates']):
			layer_axes[font.axes[i].name] = layer.attributes['coordinates'][coords]
		if layer_axes not in special_layer_axes:
			special_layer_axes.append(layer_axes)
	return special_layer_axes


def getNonSpecialGlyphs(font, axes):
	__doc__ = """Provided a font and a list of axis coordinates, returns all glyphs without those coordinates"""
	glyph_names_to_delete = []
	for glyph in font.glyphs:
		delete_glyph = True
		for layer in glyph.layers:
			if layer.isSpecialLayer and layer.attributes['coordinates']:
				coords = list(layer.attributes['coordinates'].values())
				if coords == axes:
					delete_glyph = False
		if delete_glyph:
			if glyph.name not in glyph_names_to_delete:
				glyph_names_to_delete.append(glyph.name)
	return glyph_names_to_delete


def getSpecialSources(font):
	__doc__ = """Returns an array of designspaceLib SourceDescriptors """

	sources = []
	special_layer_axes = getSpecialLayerAxes(font)
	for i, special_layer_axis in enumerate(special_layer_axes):
		axes = list(special_layer_axis.values())
		s = SourceDescriptor()
		s.location = special_layer_axis
		font_name = getNameWithAxis(font, axes)
		s.filename = "%s.ufo" % font_name
		sources.append(s)
	return sources


def addAxes(doc, font):
	__doc__ = """Provided a designspace doc and a font object, adds axes from that font to the designspace as AxisDescriptors"""
	for i, axis in enumerate(font.axes):
		try:
			axis_map = font.customParameters["Axis Mappings"][axis.axisTag]
		except:
			continue
		a = AxisDescriptor()
		axis_min, axis_max = getBoundsByTag(font, axis.axisTag)
		for k in sorted(axis_map.keys()):
			a.map.append((axis_map[k], k))
		a.maximum = axis_map[axis_max]
		a.minimum = axis_map[axis_min]
		origin_coord = getOriginCoords(font)[i]
		user_origin = axis_map[origin_coord]
		a.default = user_origin
		a.name = axis.name
		a.tag = axis.axisTag
		doc.addAxis(a)


def getConditionsFromOT(font):
	__doc__ = """Provided a font object, returns two arrays: one a list of OT substitution conditions, and one of the glyph replacements to make given those conditions. Each array has the same index.
	
Example use:
condition_list, replacement_list = getConditionsFromOT(font)
"""
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
				axis_name = getAxisNameByTag(font, tag)
				m = re.findall("\d+(?:\.|)\d*", condition)
				cond_min = float(m[0])
				if len(m) > 1:
					cond_max = float(m[1])
					range_dict = dict(
						name=axis_name, minimum=cond_min, maximum=cond_max)
				else:
					_, cond_max = getBoundsByTag(font, tag)
					range_dict = dict(
						name=axis_name, minimum=cond_min, maximum=cond_max)
				conditions.append(range_dict)
			condition_list.append(conditions)
			condition_index = condition_index + 1
		elif line.startswith("sub"):
			m = re.findall("sub (.*) by (.*);", line)[0]
			replace = (m[0], m[1])
			try:
				replacement_list[condition_index-1].append(replace)
			except:
				replacement_list.append(list())
				replacement_list[condition_index-1].append(replace)
	return [condition_list, replacement_list]


def removeSubsFromOT(font):
	__doc__ = """Provided a font object, removes any variable conditional subsitutions"""
	feature_index = None
	for i, feature_itr in enumerate(font.features):
		for line in feature_itr.code.splitlines():
			if line.startswith("condition "):
				feature_index = i
				break
	if(feature_index):
		font.features[feature_index].code = re.sub(
			r'#ifdef VARIABLE.*?#endif', '', font.features[feature_index].code, flags=re.DOTALL)


def applyConditionsToRules(doc, condition_list, replacement_list):
	__doc__ = """Provided a designspace document, condition list, and replacement list (as provided by getConditionsFromOT), adds matching designspace RuleDescriptors to the doc"""
	rules = []
	for i, condition in enumerate(condition_list):
		r = RuleDescriptor()
		r.name = "Rule %s" % str(i+1)
		r.conditionSets.append(condition)
		for sub in replacement_list[i]:
			r.subs.append(sub)
		rules.append(r)
	doc.rules = rules


def getInstances(font):
	__doc__ = """Provided a font object, provides a list of designspaceLib InstanceDescriptors"""
	instances_to_return = []
	for instance in font.instances:
		if not instance.active:
			continue
		if not instance.familyName:  # skip Variable Font Setting, which is an instance
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
			family_name = "%s %s" % (
				font.familyName, getVariableFontFamily(font))
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
		ins.styleMapFamilyName = "%s %s" % (
			instance.preferredFamily, instance.name)
		ins.styleMapStyleName = style_map_style
		axis_name = {}
		for i, axis_value in enumerate(instance.axes):
			axis_name[font.axes[i].name] = axis_value
		ins.location = axis_name
		instances_to_return.append(ins)
	return instances_to_return


def addInstances(doc, instances):
	__doc__ = """Provided a doc and list of designspace InstanceDescriptors, adds them to the doc"""
	for instance in instances:
		doc.addInstance(instance)


def updateFeatures(font):
	__doc__ = """Provided a font object, updates its automatically generated OpenType features"""
	for feature in font.features:
		if feature.automatic:
			feature.update()


def getDesignSpaceDocument(font):
	__doc__ = """Returns a designspaceLib DesignSpaceDocument populated with informated from the provided font object"""
	doc = DesignSpaceDocument()
	addAxes(doc, font)
	sources = getSources(font)
	addSources(doc, sources)
	special_sources = getSpecialSources(font)
	addSources(doc, special_sources)
	instances = getInstances(font)
	addInstances(doc, instances)
	condition_list, replacement_list = getConditionsFromOT(font)
	applyConditionsToRules(doc, condition_list, replacement_list)
	return doc


def generateMastersAtBraces(font, temp_ufo_folder):
	__doc__ = """Provided a font object and export destination, exports all brace layers as individual UFO masters"""
	global delete_unnecessary_glyphs
	special_layer_axes = getSpecialLayerAxes(font)
	for i, special_layer_axis in enumerate(special_layer_axes):
		axes = list(special_layer_axis.values())
		font.instances.append(GSInstance())
		ins = font.instances[-1]
		ins.name = getNameWithAxis(font, axes)
		ufo_file_name = "%s.ufo" % ins.name
		style_name = getStyleNameWithAxis(font,axes)
		ins.styleName = style_name
		ins.axes = axes
		brace_font = ins.interpolatedFont
		brace_font.masters[0].name = style_name
		if delete_unnecessary_glyphs:
			glyph_names_to_delete = getNonSpecialGlyphs(font, axes)
			for glyph in glyph_names_to_delete:
				del(brace_font.glyphs[glyph])
			feature_keys = [feature.name for feature in brace_font.features]
			for key in feature_keys:
				del(brace_font.features[key])
			class_keys = [font_class.name for font_class in brace_font.classes]
			for key in class_keys:
				del(brace_font.classes[key])
			for glyph in brace_font.glyphs:
				if glyph.rightKerningGroup:
					glyph.rightKerningGroup = None
				if glyph.leftKerningGroup:
					glyph.leftKerningGroup = None
				if glyph.topKerningGroup:
					glyph.topKerningGroup = None
				if glyph.bottomKerningGroup:
					glyph.bottomKerningGroup = None
			brace_font.kerning = {}
			brace_font.kerningRTL = {}
			brace_font.kerningVertical = {}
		ufo_file_path = os.path.join(temp_ufo_folder, ufo_file_name)
		exportSingleUFObyMaster(
			brace_font.masters[0], ufo_file_path, brace_font.masters[0].name)

def fixStyleName(name,path):
	new_path = os.path.join(path, "fontinfo.plist")
	f = open(new_path,'r', encoding="utf-8")
	file_data = f.read()
	f.close()
	new_data = re.sub(r'(<key>styleName</key>\n*\r*\s+<string>)(.*)?</string>',rf'\1{name}</string>', file_data)
	f = open(new_path,'w', encoding="utf-8")
	f.write(new_data)
	f.close()

def exportSingleUFObyMaster(master, dest, name):
	__doc__ = """Provided a master, destination, and name, exports a UFO file of that master"""
	exporter = NSClassFromString('GlyphsFileFormatUFO').alloc().init()
	exporter.setFontMaster_(master)
	print("Exporting master: %s - %s" % (master.font.familyName, master.name))
	exporter.writeUfo_toURL_error_(master, NSURL.fileURLWithPath_(dest), None)
	fixStyleName(master.name,dest)


def exportUFOMasters(font, dest):
	__doc__ = """Provided a font object and a destination, exports a UFO for each master in the UFO, not including special layers (for that use generateMastersAtBraces)"""
	for master in font.masters:
		font_name = getFamilyNameWithMaster(font, master)
		file_name = "%s.glyphs" % font_name
		ufo_file_name = file_name.replace('.glyphs', '.ufo')
		ufo_file_path = os.path.join(dest, ufo_file_name)
		exportSingleUFObyMaster(master, ufo_file_path, font_name)


def main():
	# use a copy to prevent modifying the open Glyphs file
	font = Glyphs.font.copy()
	# put all special layers on the same masterID
	alignSpecialLayers(font)
	# update any automatically generated features that need it
	updateFeatures(font)

	# as a destination path (and empty it first if it exists)
	file_path = Glyphs.font.parent.fileURL().path()
	font_name = getFamilyName(font)
	file_dir = os.path.dirname(file_path)
	dest = os.path.join(file_dir, 'ufo')
	if os.path.exists(dest):
		shutil.rmtree(dest)

	# when creating files below, export them to tmp_dir before we copy it over.
	# tempfile will automatically delete the temp files we generated
	with tempfile.TemporaryDirectory() as tmp_dir:
		temp_ufo_folder = os.path.join(tmp_dir, "ufo")
		os.mkdir(temp_ufo_folder)
		# generate a designspace file based on metadata in the copy of the open font
		print("Building designspace from font metadata...")
		designspace_doc = getDesignSpaceDocument(font)
		# remove the OpenType substituties as they are now in the designspace as conditionsets
		removeSubsFromOT(font)
		# export designspace, UFOs for masters, and UFOs for brace layers
		designspace_path = "%s/%s.designspace" % (temp_ufo_folder, font_name)
		designspace_doc.write(designspace_path)
		print("Building UFOs for masters...")
		exportUFOMasters(font, temp_ufo_folder)
		print("Building UFOs for brace layers if present...")
		generateMastersAtBraces(font, temp_ufo_folder)
		# copy from temp dir to the destination. after this, tempfile will automatically delete the temp files
		shutil.copytree(temp_ufo_folder, dest)
	# open the output dir

	
	os.system("open %s" % dest.replace(" ", "\ "))
	print("Done!")


main()
