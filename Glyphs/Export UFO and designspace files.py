# MenuTitle: Export UFO and designspace files
__doc__ = """
Exports UFO and designspace files. Supports substitutions defined in OT features, but not yet bracket layers. Brace layers supported, but not yet as "support layers" for Skateboard. Thanks to Rafał Buchner, Joancarles Casasín (https://robofont.com/documentation/how-tos/converting-from-glyphs-to-ufo/), and to the authors and maintainers of designspaceLib and fontParts.
"""

from GlyphsApp import GSInstance
import re
import os
import vanilla
import tempfile
import shutil
import glob
import subprocess
from collections import OrderedDict
from fontTools.designspaceLib import DesignSpaceDocument
from fontTools.designspaceLib import AxisDescriptor
from fontTools.designspaceLib import SourceDescriptor
from fontTools.designspaceLib import InstanceDescriptor
from fontTools.designspaceLib import RuleDescriptor
#from fontTools.designspaceLib import AxisLabelDescriptor disabled for now - want more clarity on how to define userspace values for names of axis location inside Glyphs
from fontTools.designspaceLib import LocationLabelDescriptor
from fontParts.world import NewFont
from fontParts.fontshell.contour import RContour
from fontParts.fontshell.component import RComponent
from fontParts.fontshell.anchor import RAnchor
from fontParts.fontshell.guideline import RGuideline
from fontParts.fontshell.lib import RLib

# Todo:
# - Font-level Guidelines
# - Hinting: public.postscript.hints, public.truetype.instructions, public.verticalOrigin, public.truetype.roundOffsetToGrid, public.truetype.useMyMetrics	
# - Metainfo.plist: creator, formatVersion, formatVersionMinor
# - One designspace for VF? Have to look into designspace 5 spec more closely
# - Finish the metadata in addFontInfoToUfo
# - Add support for font-level layers (instead of multiple UFOs for brace layers)
# - Add support for bracket layers (in addition to OT based subs, which are already supported)
# - Copy Glyph-level layers over (but this is potentially a non-goal)
# - Images in glyphs
# - Decompose smart stuff
# - More elaborate build script possibilities (add size table that we're outputting but not importing in masters, for example; other tables too)
# - public.openTypeMeta
# - public.openTypeCategories
# - public.unicodeVariationSequences
# - public.objectLibs
# com.schriftgestaltung.disablesAutomaticAlignment
# com.schriftgestaltung.font.customParameters = []
# com.schriftgestaltung.font.userData = dict()
# com.schriftgestaltung.fontMaster.customParameters = []
# com.schriftgestaltung.fontMasterID
# com.schriftgestaltung.glyphOrder
# com.schriftgestaltung.master.name
# com.schriftgestaltung.useNiceNames
# com.schriftgestaltung.weightValue
# com.schriftgestaltung.widthValue


class ExportUFOAndDesignspace(object):
	def __init__(self):
		margin_x = 20
		margin_y = 16
		spacer = 6
		ui_height = 24
		window_width  = 220 + margin_x * 2
		window_height = (ui_height * 10) + (spacer * 9) + (margin_y * 1.5)

		#todo window_height = (ui_height * 15) + (spacer * 9) + (margin_y * 1.5)

		self.w = vanilla.FloatingWindow(
			( window_width, window_height ), # default window size
			"Export UFO and designspace" # window title
		)
		
		xPos = margin_x		
		yPos = spacer * 2
	
		self.w.buttonLabel = vanilla.TextBox((margin_x, yPos, -margin_x, ui_height), "Designspace:", sizeStyle="small")

		yPos = yPos + spacer + ui_height / 2.33
		
		self.w.buttonSelectBuild = vanilla.SegmentedButton((margin_x, yPos, -margin_x, ui_height), [dict(title="Variable"), dict(title="Static"), dict(title="Both")],sizeStyle='small', callback=self.buttonSelectBuildCallback)
		self.w.buttonSelectBuild.set(2)
		
		yPos = yPos + spacer * 1.5 + ui_height

		## Production names option todo

		#

		# #Skateboard layers todo 
		
		# self.w.buttonLabel2 = vanilla.TextBox((margin_x, yPos, -margin_x, ui_height), "Brace layers:", sizeStyle="small")

		# yPos = yPos + spacer + ui_height / 2.33
		
		# self.w.buttonSelect2 = vanilla.SegmentedButton((margin_x, yPos, -margin_x, ui_height), [dict(title="Skateboard layers"), dict(title="Multiple UFOs")],sizeStyle='small', callback=self.layerButtonCallback)
		# self.w.buttonSelect2.set(1)
		
		# yPos = yPos + spacer * 1 + ui_height

		self.w.checkBox = vanilla.CheckBox((margin_x, yPos, -margin_x, ui_height), "Generate fontmake build scripts", callback=self.checkBoxCallback, value=True, sizeStyle="small")

		# todo
		# 
		# yPos = yPos +  ui_height

		# self.w.keepLibCheckbox = vanilla.CheckBox((margin_x, yPos, -margin_x, ui_height), "Keep Glyphs info in designspace lib", callback=self.checkBoxCallback, value=False, sizeStyle="small")

		
		# yPos = yPos +  ui_height

		# self.w.decomposeCheckbox = vanilla.CheckBox((margin_x, yPos, -margin_x, ui_height), "Decompose smart stuff", callback=self.checkBoxCallback, value=False, sizeStyle="small")

		# yPos = yPos +  ui_height

		# self.w.productionCheckbox = vanilla.CheckBox((margin_x, yPos, -margin_x, ui_height), "Convert to production names", callback=self.checkBoxCallback, value=False, sizeStyle="small")

		yPos = yPos + spacer * 1 + ui_height
																										
		self.w.decomposeLabel = vanilla.TextBox((margin_x, yPos, -margin_x, 14), "Decompose glyphs", sizeStyle="small")
		yPos = yPos + spacer + ui_height / 2.33
		self.w.decomposeField = vanilla.EditText((xPos, yPos, -margin_x, ui_height))
		yPos = yPos + spacer * 1.5 + ui_height

		self.w.overlapLabel = vanilla.TextBox((margin_x, yPos, -margin_x, 14), "Remove overlaps", sizeStyle="small")
		yPos = yPos + spacer + ui_height / 2.33
		self.w.overlapField = vanilla.EditText((xPos, yPos, -margin_x, ui_height))
		yPos = yPos + spacer * 1.5 + ui_height
		
		self.w.statusLabel = vanilla.TextBox((margin_x, yPos, -margin_x, ui_height), "Log:", sizeStyle="small")
		yPos = yPos + spacer + ui_height / 2.33
		self.w.status = vanilla.TextEditor((margin_x, yPos, -margin_x, ui_height * 3), "Ready...",checksSpelling=False)
		yPos = yPos + spacer + ui_height * 3
	
		self.w.FindButton = vanilla.Button((xPos, yPos, -margin_x, ui_height), "Export files", sizeStyle='regular', callback=self.exportButton)
		
		self.to_build = {
			"variable": True,
			"static": True,
		}

		self.to_add_build_script = True  # adds a minimal build script to the output dir
		self.brace_layers_as_layers = False

		# todo, keep track of these in a preference
		self.to_decompose = []  # if you want, make an array of glyphnames (not unicodes)
		self.to_remove_overlap = []  # same

		self.keep_glyphs_lib = False
		self.production_names = False
		self.decompose_smart  = False
        
		self.w.open()

	def exportButton(self, sender):
		self.to_decompose = self.w.decomposeField.get().split(" ")
		self.to_remove_overlap = self.w.overlapField.get().split(" ")
		self.main()
	
	def buttonSelectBuildCallback(self, sender):
		if sender.get() == 0:
			self.to_build = { "variable": True, "static": False }
		elif sender.get() == 1:
			self.to_build = { "variable": False, "static": True }
		elif sender.get() == 2:
			self.to_build = { "variable": True, "static": True }

	def layerButtonCallback(self, sender):
		if sender.get() == 0:
			self.brace_layers_as_layers = True
		elif sender.get() == 1:
			self.brace_layers_as_layers = False
			
	def checkBoxCallback(self, sender):
		if sender.get() == 1:
			self.to_add_build_script = True
		else:
			self.to_add_build_script = False

	def keepLibCheckBoxCallback(self, sender):
		if sender.get() == 1:
			self.keep_glyphs_lib = True
		else:
			self.keep_glyphs_lib = False
	
	def decomposeCheckBoxCallback(self, sender):
		if sender.get() == 1:
			self.decompose_smart = True
		else:
			self.decompose_smart = False

	def productionCheckBoxCallback(self, sender):
		if sender.get() == 1:
			self.production_names = True
		else:
			self.production_names = False

	def addBuildScript(self, font, dest):
		__doc__ = """Provided a font, destination and font name, creates a build script for the project"""
		if not self.to_add_build_script:
			return
		static_font_name = self.getFamilyName(font, "static").replace(" ", "")
		vf_font_name = self.getFamilyName(font, "variable").replace(" ", "")
		nl = "\n"
		vf_script = f"""python3 -m fontmake -m {vf_font_name}.designspace -o variable --output-dir build/vf"""
		static_script = f"""python3 -m fontmake -i --expand-features-to-instances -m {static_font_name}.designspace -o ttf --output-dir build/ttf{nl}python3 -m fontmake -i --expand-features-to-instances -m {static_font_name}.designspace -o otf --output-dir build/otf"""
		if self.to_build["static"] and self.to_build["variable"]:
			build_script = "#!/bin/bash" + "\n" + vf_script + "\n" + static_script + "\n"
		elif self.to_build["static"]:
			build_script = "#!/bin/bash" + "\n" + static_script + "\n"
		else:
			build_script = "#!/bin/bash" + "\n" + vf_script + "\n"
		script_name = os.path.join(dest, "build.sh")
		f = open(script_name, "w")
		f.write(build_script)
		f.close()
		subprocess.run(["chmod", "+x", script_name])


	def decomposeGlyphs(self, font):
		__doc__ = """Provided a font object, decomposes glyphs defined in to_decompose"""
		for glyph in self.to_decompose:
			if font.glyphs[glyph]:
				for layer in font.glyphs[glyph].layers:
					if len(layer.components) > 0:
						if layer.isMasterLayer or layer.isSpecialLayer:
							layer.decomposeComponents()


	def removeOverlaps(self, font):
		__doc__ = """Provided a font object, removes overlaps in glyphs defined in to_remove_overlap"""
		for glyph in self.to_remove_overlap:
			if font.glyphs[glyph]:
				for layer in font.glyphs[glyph].layers:
					if layer.isMasterLayer or layer.isSpecialLayer:
						layer.removeOverlap()


	def getMutedGlyphs(self, font):
		__doc__ = "Provided a font object, returns an array of non-exporting glyphs to be added as muted glyphs in the designspace"
		return [glyph.name for glyph in font.glyphs if not glyph.export]


	def getBoundsByTag(self, font, tag):
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


	def getOriginMaster(self, font):
		__doc__ = """Provided a font object, returns a string of the master ID referencing the master that is set to the variable font origin by custom paramter"""
		master_id = None
		for parameter in font.customParameters:
			if parameter.name == "Variable Font Origin":
				master_id = parameter.value
		if master_id is None:
			return font.masters[0].id
		return master_id


	def getOriginCoords(self, font):
		__doc__ = """Provided a font object, returns an array of axis coordinates specified on the variable font origin master."""
		for parameter in font.customParameters:
			if parameter.name == "Variable Font Origin":
				master_id = parameter.value
		if master_id is None:
			master_id = font.masters[0].id
		for master in font.masters:
			if master.id == master_id:
				return list(master.axes)


	def getAxisNameByTag(self, font, tag):
		__doc__ = """Provided a font object an axis tag, returns an axis name"""
		for axis in font.axes:
			if axis.axisTag == tag:
				return axis.name


	def hasVariableFamilyName(self, font):
		__doc__ = """Provided a font object, returns a boolean as to whether or not the font has a different VF name"""
		for instance in font.instances:
			if instance.type == 1:
				return True


	def getVariableFontFamily(self, font):
		__doc__ = """Provided a font object, returns the name associated with a Variable Font Setting export"""
		for instance in font.instances:
			if instance.type == 1:
				return font.familyName + " " + instance.name
		return font.familyName


	def getFamilyName(self, font, format):
		__doc__ = """Provided a font object, returns a font family name"""
		if format == "variable":
			family_name = self.getVariableFontFamily(font)
		else:
			family_name = font.familyName
		return family_name


	def getFamilyNameWithMaster(self, font, master, format):
		__doc__ = """Provided a font object and a master, returns a font family name"""
		master_name = master.name
		if self.hasVariableFamilyName(font):
			if format == "static":
				font_name = "%s - %s" % (font.familyName, master_name)
			else:
				font_name = "%s - %s" % (self.getVariableFontFamily(font), master_name)
		else:
			font_name = "%s - %s" % (font.familyName, master_name)

		return font_name


	def getStyleNameWithAxis(self, font, axes):
		__doc__ = """Returns a style name based on GSAxes"""
		style_name = ""
		for i, axis in enumerate(axes):
			style_name = "%s %s %s" % (style_name, font.axes[i].name, axis)
		return style_name.strip()


	def getNameWithAxis(self, font, axes, format):
		__doc__ = """Provided a font and a dict of axes for a brace layer, returns a font family name"""
		if not self.to_build["static"]:
			font_name = "%s -" % self.getVariableFontFamily(font)
		else:
			font_name = "%s -" % (font.familyName)
		for i, axis in enumerate(axes):
			font_name = "%s %s %s" % (font_name, font.axes[i].name, axis)
		return font_name


	def alignSpecialLayers(self, font):
		__doc__ = """Applies the same master ID referencing the variable font origin to all brace layers"""
		master_id = self.getOriginMaster(font)
		special_layers = self.getSpecialLayers(font)
		for layer in special_layers:
			layer.associatedMasterId = master_id


	def getSources(self, font, format):
		__doc__ = """Provided a font object, creates and returns a list of designspaceLib SourceDescriptors"""
		sources = []
		for i, master in enumerate(font.masters):
			s = SourceDescriptor()
			if self.hasVariableFamilyName(font) and not self.to_build["static"]:
				font_name = self.getFamilyNameWithMaster(font, master, "variable")
			else:
				font_name = self.getFamilyNameWithMaster(font, master, "static")
			s.filename = "masters/%s.ufo" % font_name
			s.familyName = self.getFamilyName(font, format)
			s.styleName = master.name
			locations = dict()
			for x, axis in enumerate(master.axes):
				locations[font.axes[x].name] = axis
			s.designLocation = locations
			s.mutedGlyphNames = self.getMutedGlyphs(font)
			sources.append(s)
		return sources


	def addSources(self, doc, sources):
		__doc__ = """Provided a designspace document and array of source descriptors, adds those sources to the designspace doc."""
		for source in sources:
			doc.addSource(source)


	def getSpecialLayers(self, font):
		__doc__ = """Provided a font object, returns a list of GSLayers that are brace layers (have intermediate master coordinates)."""
		return [l for g in font.glyphs for l in g.layers if l.isSpecialLayer and l.attributes['coordinates']]


	def getSpecialLayerAxes(self, font):
		__doc__ = """Provided a font object, returns a list of dicts containing name and coordinate information for each axis"""
		special_layer_axes = []
		layers = self.getSpecialLayers(font)
		for layer in layers:
			layer_axes = dict()
			for i, coords in enumerate(layer.attributes['coordinates']):
				layer_axes[font.axes[i].name] = int(
					layer.attributes['coordinates'][coords])
			if layer_axes not in special_layer_axes:
				special_layer_axes.append(layer_axes)
		return special_layer_axes


	def getSpecialGlyphs(self, font, axes):
		__doc__ = """Provided a font and a list of axis coordinates, returns all glyphs inside those coordinates"""
		glyph_names = []
		for glyph in font.glyphs:
			for layer in glyph.layers:
				if layer.isSpecialLayer and layer.attributes['coordinates']:
					coords = list(
						map(int, layer.attributes['coordinates'].values()))
					if coords == axes:
						glyph_names.append(glyph.name)
						continue
		return glyph_names


	def getSpecialSources(self, font, format):
		__doc__ = """Provided a font object, returns an array of designspaceLib SourceDescriptors """
		if self.brace_layers_as_layers == False:
			sources = []
			special_layer_axes = self.getSpecialLayerAxes(font)
			for i, special_layer_axis in enumerate(special_layer_axes):
				axes = list(special_layer_axis.values())
				s = SourceDescriptor()
				s.location = special_layer_axis
				font_name = self.getNameWithAxis(font, axes, format)
				s.filename = "masters/%s.ufo" % font_name
				sources.append(s)
			return sources
		else:
			sources = []
			special_layer_axes = self.getSpecialLayerAxes(font)
			for i, special_layer_axis in enumerate(special_layer_axes):
				s = SourceDescriptor()
				layer_axis_name= "{" + ", ".join(str(x) for x in list(special_layer_axis.values())) + "}"
				axes = list(special_layer_axis.values())
				s = SourceDescriptor()
				s.location = special_layer_axis
				font_name = self.getNameWithAxis(font, axes, format)
				s.filename = "masters/%s.ufo" % font_name
				s.familyName = font_name
				s.layerName = layer_axis_name
				sources.append(s)
			return sources


	def getAxisMap(self, font):
		__doc__ = """Provided a font object, iterate over the GSInstances and return a dict compatible with the Axis Mappings custom parameter, based on the Axis Location custom parameter of those GSInstances"""
		axis_map = dict()
		for instance in font.instances:
			if instance.customParameters["Axis Location"]:
				if instance.type == 0:
					for i, internal in enumerate(instance.axes):
						external = instance.customParameters["Axis Location"][i]['Location']
						axis_tag = font.axes[i].axisTag
						try:
							axis_map[axis_tag][internal] = external
						except:
							axis_map[axis_tag] = dict()
							axis_map[axis_tag][internal] = external
		if len(axis_map):
			return axis_map
		else:
			return None


	def getLabels(self,font,format):
		__doc__ = """Provided a GSfont object and a font format string, return a list of LocationLabelDescriptors"""
		labels = []
		
		instances = [instance for instance in font.instances if instance.active == True and instance.type == 0]
		for instance in instances:
			if format == "variable" and instance.variableStyleName:
				style_name = instance.variableStyleName
			else:
				style_name = instance.name

			elidable = False
			for i,axis in enumerate(instance.axes):
				axis_tag = font.axes[i].axisTag
				if instance.customParameters["Elidable STAT Axis Value Name"] and instance.customParameters["Elidable STAT Axis Value Name"] == axis_tag:
					elidable = True
			
			if font.customParameters["Axis Mappings"]:
				axis_map = font.customParameters["Axis Mappings"]
			else:
				axis_map = self.getAxisMap(font)
			
			user_location = dict()
			for i,axis in enumerate(instance.axes):
				user_name = font.axes[i].name
				user_coord = axis_map[font.axes[i].axisTag][axis]
				user_location[user_name] = user_coord

			label = LocationLabelDescriptor(name=style_name,userLocation=user_location,elidable=elidable)
			if label not in labels:
				labels.append(label)
		labels = list(dict.fromkeys(labels))
		return labels


	def addLabels(self,doc,labels):
		__doc__ = """Provided a DesignSpaceDocument and a list of LocationLabelDescriptors, adds those labels to the doc"""
		doc.locationLabels = labels
		return doc


	def getAxisLabelList(self,font,axis_index,format):
		__doc__ = "Provided a GSfont object, the index of a GSAxis, and the output format, returns a list of labels"
		axis_tag = font.axes[axis_index].axisTag
		if font.customParameters["Axis Mappings"]:
			axis_map = font.customParameters["Axis Mappings"][axis_tag]
		else:
			axis_map = self.getAxisMap(font)
		
		axis_range = axis_map[axis_tag]
		axis_list = list(axis_range.items())

		labels = []
		label_user = []
		
		instances = [instance for instance in font.instances if instance.active == True and instance.type == 0]
		for instance in instances:
			#
			# tricky if there's an opsz... 
			#
			# if format == "variable" and instance.variableStyleName:
			#	style_name = instance.variableStyleName
			# else:
			#	style_name = instance.name

			if axis_tag == "opsz" and instance.customParameters["Optical Size"]:
				style_name = instance.customParameters["Optical Size"].split(";")[-1]
			else:
				style_name = instance.name

			if instance.customParameters["Style Name as STAT entry"] and instance.customParameters["Style Name as STAT entry"] == axis_tag:
				if instance.customParameters["Elidable STAT Axis Value Name"]:
					elidable = True
				else:
					elidable = False
				user_min = axis_list[0][1]
				user_max = axis_list[-1][1]
				user_val = axis_range[instance.axes[axis_index]]
				label = AxisLabelDescriptor(name=style_name,userValue=user_val, userMinimum=user_min, userMaximum=user_max,elidable=elidable)
				if user_val not in label_user:
					label_user.append(user_val)
					labels.append(label)
		return labels

		
	def addAxes(self, doc, font, format):
		__doc__ = """Provided a designspace doc and a font object, adds axes from that font to the designspace as AxisDescriptors"""
		for i, axis in enumerate(font.axes):
			if font.customParameters["Axis Mappings"]:
				axis_map = font.customParameters["Axis Mappings"][axis.axisTag]
			else:
				axis_map = self.getAxisMap(font)
				if axis_map is not None:
					axis_map = axis_map[axis.axisTag]
			if axis_map:
				a = AxisDescriptor()
				
				axis_min, axis_max = self.getBoundsByTag(font, axis.axisTag)

				for k in sorted(axis_map.keys()):
					a.map.append((axis_map[k], k))
				try:
					a.maximum = axis_map[axis_max]
					a.minimum = axis_map[axis_min]
				except:
					self.w.status.set("\n\nError: the font's axis mappings don't match its real min/max coords\n\n" + self.w.status.get())
					print(" ")
				origin_coord = self.getOriginCoords(font)[i]
				user_origin = axis_map[origin_coord]
				a.axisOrdering = i
				a.default = user_origin
				a.name = axis.name
				a.tag = axis.axisTag

				#
				# For Format 2 STAT, but see note at top, diabled for now
				#
				# label_list = self.getAxisLabelList(font,i,format)
				# for label in label_list:
				# 	a.axisLabels.append(label)
				
				doc.addAxis(a)


	def getConditionsFromOT(self, font):
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
					axis_name = self.getAxisNameByTag(font, tag)
					m = re.findall("\d+(?:\.|)\d*", condition)
					cond_min = float(m[0])
					if len(m) > 1:
						cond_max = float(m[1])
						range_dict = dict(
							name=axis_name, minimum=cond_min, maximum=cond_max)
					else:
						_, cond_max = self.getBoundsByTag(font, tag)
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


	def removeSubsFromOT(self, font):
		__doc__ = """Provided a font object, removes subsitutions in feature code"""
		feature_index = None
		for i, feature_itr in enumerate(font.features):
			for line in feature_itr.code.splitlines():
				if line.startswith("condition "):
					feature_index = i
					break
		if(feature_index):
			font.features[feature_index].code = re.sub(
				r'#ifdef VARIABLE.*?#endif', '', font.features[feature_index].code, flags=re.DOTALL)


	def applyConditionsToRules(self, doc, condition_list, replacement_list):
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


	def getInstances(self, font, format):
		__doc__ = """Provided a font object, returns a list of designspaceLib InstanceDescriptors"""
		instances_to_return = []
		for instance in font.instances:
			if not instance.active:
				continue
			if instance.type == 1:  # skip Variable Font Setting
				continue
			ins = InstanceDescriptor()
			postScriptName = instance.fontName
			if instance.isBold:
				style_map_style = "bold"
			elif instance.isItalic:
				style_map_style = "italic"
			else:
				style_map_style = "regular"
			if format == "variable":
				family_name = self.getVariableFontFamily(font)
			else:
				if instance.preferredFamily:
					family_name = instance.preferredFamily
				else:
					family_name = font.familyName
			ins.familyName = family_name
			if format == "variable":
				style_name = instance.variableStyleName
			else:
				style_name = instance.name
			ins.styleName = style_name
			ins.filename = "instances/%s.ufo" % postScriptName
			ins.postScriptFontName = postScriptName
			ins.styleMapFamilyName = instance.preferredFamily
			ins.styleMapStyleName = style_map_style
			design_location = {}
			for i, axis_value in enumerate(instance.axes):
				design_location[font.axes[i].name] = axis_value
			ins.designLocation = design_location
			
			axis_map = self.getAxisMap(font)
			user_location = {}
			for i, axis_value in enumerate(instance.axes):
				user_location[font.axes[i].name] = axis_map[font.axes[i].axisTag][axis_value]
			ins.userLocation = user_location

			instances_to_return.append(ins)
		return instances_to_return


	def addInstances(self, doc, instances):
		__doc__ = """Provided a doc and list of designspace InstanceDescriptors, adds them to the doc"""
		for instance in instances:
			doc.addInstance(instance)


	def updateFeatures(self, font):
		__doc__ = """Provided a font object, updates its automatically generated OpenType features"""
		for feature in font.features:
			if feature.automatic:
				feature.update()


	def getDesignSpaceDocument(self, font, format):
		__doc__ = """Returns a designspaceLib DesignSpaceDocument populated with informated from the provided font object"""
		doc = DesignSpaceDocument()
		self.addAxes(doc, font, format)
		sources = self.getSources(font, format)
		self.addSources(doc, sources)
		special_sources = self.getSpecialSources(font, format)
		self.addSources(doc, special_sources)
		instances = self.getInstances(font, format)
		self.addInstances(doc, instances)
		labels = self.getLabels(font,format)
		self.addLabels(doc,labels)
		condition_list, replacement_list = self.getConditionsFromOT(font)
		self.applyConditionsToRules(doc, condition_list, replacement_list)
		doc.rulesProcessingLast = True
		return doc


	def generateMastersAtBraces(self, font, temp_project_folder, format):
		__doc__ = """Provided a font object and export destination, exports all brace layers as individual UFO masters"""
		special_layer_axes = self.getSpecialLayerAxes(font)

		if self.brace_layers_as_layers == False:
			for i, special_layer_axis in enumerate(special_layer_axes):
				axes = list(special_layer_axis.values())
				font.instances.append(GSInstance())
				ins = font.instances[-1]
				ins.name = self.getNameWithAxis(font, axes, format)
				ufo_file_name = "%s.ufo" % ins.name
				style_name = self.getStyleNameWithAxis(font, axes)
				ins.styleName = style_name
				ins.axes = axes
				brace_font = ins.interpolatedFont
				brace_font.masters[0].name = style_name
				brace_glyphs = self.getSpecialGlyphs(font, axes)
				for glyph in font.glyphs:
					if glyph.name not in brace_glyphs:
						del(brace_font.glyphs[glyph.name])
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
				ufo_file_path = os.path.join(temp_project_folder, ufo_file_name)
				ufo = self.buildUfoFromMaster(brace_font.masters[0], brace_font.glyphs)
				ufo.save(ufo_file_path)


	def getIndexByMaster(self, master):
		__doc__ = "Provided a GSFontMaster, returns its index within its parent GSFont"
		font = master.font
		for i, m in enumerate(font.masters):
			if master.id == m.id:
				return i


	def addGroups(self, font, ufo):
		__doc__ = "Provided a GSFont and fontParts UFO, writes kerning groups from GSFont to UFO. Currently only supports LTR."
		groups = {"left": {}, "right": {}}
		for glyph in font.glyphs:
			if glyph.leftKerningGroup:
				if glyph.leftKerningGroup not in groups["left"]:
					groups["left"][glyph.leftKerningGroup] = []
					groups["left"][glyph.leftKerningGroup].append(glyph.name)
				else:
					groups["left"][glyph.leftKerningGroup].append(glyph.name)
			if glyph.rightKerningGroup:
				if glyph.rightKerningGroup not in groups["right"]:
					groups["right"][glyph.rightKerningGroup] = []
					groups["right"][glyph.rightKerningGroup].append(glyph.name)
				else:
					groups["right"][glyph.rightKerningGroup].append(glyph.name)

		for group in groups["left"]:
			group_name = "public.kern1." + group
			group_glyphs = groups["left"][group]
			ufo.groups[group_name] = group_glyphs

		for group in groups["right"]:
			group_name = "public.kern2." + group
			group_glyphs = groups["right"][group]
			ufo.groups[group_name] = group_glyphs
		return ufo

	def formatValue(self,value,type):
		if not value:
			return None
		if type == "int":
			return int(value)
		elif type == "float":
			return float(value)
		elif type == "bool":
			return bool(value)

	def addFontInfoToUfo(self,master,ufo):
		__doc__ = """Provided a GSFontMaster and a UFO, returns a UFO with OpenType metadata from that master (and its parent GSFont)"""
		font = master.font
		ufo.info.versionMajor = font.versionMajor
		ufo.info.versionMinor = font.versionMinor

		# Generic legal 
		ufo.info.copyright = font.copyright
		ufo.info.trademark = font.trademark

		# Generic dimension
		ufo.info.unitsPerEm = font.upm
		ufo.info.ascender = master.ascender
		ufo.info.descender = master.descender
		ufo.info.xHeight = master.xHeight
		ufo.info.capHeight = master.capHeight
		ufo.info.ascender = master.ascender
		ufo.info.italicAngle = master.italicAngle

		# Misc
		ufo.info.note = font.note

		# Gasp todo
		#ufo.info.openTypeGaspRangeRecords = []
		#ufo.info.rangeMaxPPEM = dict()
		#ufo.info.rangeGaspBehavior = []

		# Head table
		ufo.info.openTypeHeadCreated = font.date.strftime("%Y/%m/%d %H:%M:%S")
		# ufo.info.openTypeHeadLowestRecPPEM = ?
		# ufo.info.openTypeHeadFlags = ?
		# ufo.info.created reated can be calculated by subtracting the 12:00 midnight, January 1, 1904 (as specified in the head table documentation) from the date stored at openTypeHeadCreated. —

		# name table - some of these may be instance specific?
		ufo.info.openTypeNameDesigner = font.designer
		ufo.info.openTypeNameDesignerURL = font.designerURL
		ufo.info.openTypeNameManufacturer = font.manufacturer
		ufo.info.openTypeNameManufacturerURL = font.manufacturerURL
		ufo.info.openTypeNameLicense = font.license
		for info in font.properties:
			if info.key == "licenseURL":
				ufo.info.openTypeNameLicenseURL = info.value
		#ufo.info.openTypeNameVersion = 
		#ufo.info.openTypeNameUniqueID = 
		ufo.info.openTypeNameDescription = font.description
		#ufo.info.openTypeNamePreferredFamilyName = 
		#ufo.info.openTypeNamePreferredSubfamilyName = 
		ufo.info.openTypeNameCompatibleFullName = font.compatibleFullName
		ufo.info.openTypeNameSampleText = font.sampleText
		# These are for instances only, no? Ghmmmmmmm
		ufo.info.openTypeNameWWSFamilyName = font.customParameters["WWS Family Name"]
		#ufo.info.openTypeNameWWSSubfamilyName =

		# hhea table

		ufo.info.openTypeHheaAscender = self.formatValue(master.customParameters["hheaAscender"],"int")
		ufo.info.openTypeHheaDescender =self.formatValue(master.customParameters["hheaDescender"],"int")
		ufo.info.openTypeHheaLineGap = self.formatValue(master.customParameters["hheaLineGap"],"int")
		# todo
		# ufo.info.openTypeHheaCaretSlopeRise
		# ufo.info.openTypeHheaCaretSlopeRun
		# ufo.info.openTypeHheaCaretOffset
		
		# OS/2 table
		#ufo.info.openTypeOS2WidthClass = ?
		#ufo.info.openTypeOS2WeightClass =  ? 
		#ufo.info.openTypeOS2Selection = fsSelection... not sure

		for info in font.properties:
			if info.key == "vendorID":
				ufo.info.openTypeOS2VendorID = info.value if info.value else None

		ufo.info.openTypeOS2Panose = [int(p) for p in font.customParameters["panose"]]
		#ufo.info.openTypeOS2FamilyClass =  ? 
		#ufo.info.openTypeOS2UnicodeRanges =
		#ufo.info.openTypeOS2CodePageRanges = 

		ufo.info.openTypeOS2TypoAscender = self.formatValue(master.customParameters["typoAscender"],"int")
		ufo.info.openTypeOS2TypoDescender = self.formatValue(master.customParameters["typoDescender"],"int")
		ufo.info.openTypeOS2TypoLineGap = self.formatValue(master.customParameters["typoLineGap"],"int")

		ufo.info.openTypeOS2WinAscent = self.formatValue(master.customParameters["winAscent"],"int")
		ufo.info.openTypeOS2WinDescent = self.formatValue(master.customParameters["winDescent"],"int")

		ufo.info.openTypeOS2Type = [int(font.customParameters["fsType"]["value"])] if font.customParameters["fsType"] and font.customParameters["fsType"]["value"] else [0]
		ufo.info.openTypeOS2SubscriptXSize = self.formatValue(master.customParameters["subscriptXSize"],"int")
		ufo.info.openTypeOS2SubscriptYSize = self.formatValue(master.customParameters["subscriptYSize"],"int")
		ufo.info.openTypeOS2SubscriptXOffset = self.formatValue(master.customParameters["subscriptXOffset"],"int")
		ufo.info.openTypeOS2SubscriptYOffset = self.formatValue(master.customParameters["subscriptYOffset"],"int")
		ufo.info.openTypeOS2SuperscriptXSize = self.formatValue(master.customParameters["subscriptYOffset"],"int")

		ufo.info.openTypeOS2SuperscriptYSize = self.formatValue(master.customParameters["superscriptYSize"],"int")
		ufo.info.openTypeOS2SuperscriptXOffset = self.formatValue(master.customParameters["superscriptXOffset"],"int")
		ufo.info.openTypeOS2SuperscriptYOffset = self.formatValue(master.customParameters["superscriptYOffset"],"int")
		ufo.info.openTypeOS2StrikeoutSize = self.formatValue(master.customParameters["strikeoutSize"],"int")
		ufo.info.openTypeOS2StrikeoutPosition = self.formatValue(master.customParameters["strikeoutPosition"],"int")

		# vhea table

	    # tcheck font.customParams["Use Typo Metrics"] / convert upm

		#ufo.info.openTypeVheaVertTypoAscender = 
		#ufo.info.openTypeVheaVertTypoDescender = 
		#ufo.info.openTypeVheaVertTypoLineGap = 
		#ufo.info.openTypeVheaCaretSlopeRise = 
		#ufo.info.openTypeVheaCaretSlopeRun = 
		#ufo.info.openTypeVheaCaretOffset = 

		# postScript 
		# ufo.info.postscriptFontName =  font.fontName hmm wait no thats on instances...
		# ufo.info.postscriptFullName = font.fullName
		#ufo.info.postscriptSlantAngle = whats a good default? no way to set in glyphs?
		ufo.info.postscriptUniqueID = font.customParameters["uniqueID"]
		ufo.info.postscriptUnderlineThickness = self.formatValue(master.customParameters["underlineThickness"],"int")
		ufo.info.postscriptUnderlinePosition = self.formatValue(master.customParameters["underlinePosition"],"int")
		ufo.info.postscriptIsFixedPitch =  self.formatValue(font.customParameters["isFixedPitch"],"bool")

		ufo.info.postscriptBlueValues = [int(b) for b in master.blueValues]
		ufo.info.postscriptOtherBlues = [int(b) for b in master.otherBlues]
		#ufo.info.postscriptFamilyBlues = to calc
		#ufo.info.postscriptFamilyOtherBlues = 
		ufo.info.postscriptStemSnapH = [float(stem) for i,stem in enumerate(master.stems) if font.stems[i].horizontal]
		ufo.info.postscriptStemSnapV = [float(stem) for i,stem in enumerate(master.stems) if not font.stems[i].horizontal]

		ufo.info.postscriptBlueFuzz = self.formatValue(font.customParameters["blueFuzz"],"float")
		ufo.info.postscriptBlueShift = self.formatValue(font.customParameters["blueShift"],"float")
		ufo.info.postscriptBlueScale = self.formatValue(font.customParameters["blueScale"],"float")

		#ufo.info.postscriptForceBold = 
		#ufo.info.postscriptDefaultWidthX = 
		#ufo.info.postscriptNominalWidthX = 
		#ufo.info.postscriptWeightName = 
		#ufo.info.postscriptDefaultCharacter = 
		#ufo.info.postscriptWindowsCharacterSet

		# FOND
		#ufo.info.macintoshFONDFamilyID = 
		#ufo.info.macintoshFONDName = 

		# todo font level custom params:
		# Extension kerning - GPOS
		# TTFZones / TTFBlueFuzz ??


		return ufo

	def buildUfoFromMaster(self, master, glyphs):
		__doc__ = """Provided a GSMFontMaster and a list of glyph names to be used in that master, return a fontParts UFO"""
		font = master.font
		master_index = self.getIndexByMaster(master)

		self.w.status.set(("Building master: %s - %s" % (master.font.familyName, master.name)) + "\n" + self.w.status.get())
		print(" ")

		if not glyphs:
			glyphs = font.glyphs

		# Create UFO
		ufo = NewFont(familyName=font.familyName, styleName=master.name)

		# Add fontinfo.plist
		ufo = self.addFontInfoToUfo(master,ufo)
		
		# add empty glyphs
		for glyph in glyphs:
			ufo.newGlyph(glyph.name)
			if glyph.unicodes is not None:
				ufo[glyph.name].unicodes = glyph.unicodes
			ufo[glyph.name].export = glyph.export

		# add glyph contents
		for glyph in glyphs:
			for layer in glyph.layers:
				if layer.isMasterLayer and layer.master.id == font.masters[master_index].id:
					ufo[glyph.name].width = layer.width
					ufo[glyph.name].leftMargin = layer.LSB
					ufo[glyph.name].rightMargin = layer.RSB
					if layer.anchors:
						for anchor in layer.anchors:
							ufo_anchor = RAnchor()
							ufo_anchor.name = anchor.name
							ufo_anchor.x = anchor.x
							ufo_anchor.y = anchor.y
							ufo[glyph.name].appendAnchor(anchor=ufo_anchor)
					if layer.shapes:
						for shape in layer.shapes:
							if shape.shapeType == 2:
								contour = RContour()
								contour.clockwise = False if shape.direction == -1 else True
								nodes = shape.nodes
								for i, node in enumerate(nodes):
									if shape.closed == False and i == 0:
										contour.appendPoint(
											(node.x, node.y), "move")
									else:
										if node.type == "line" or node.type == "curve" or node.type == "offcurve":
											contour.appendPoint(
												(node.x, node.y), node.type, node.smooth)
								ufo[glyph.name].appendContour(contour)
							elif shape.shapeType == 4:
								component = RComponent()
								component.baseGlyph = shape.name
								component.scale = (shape.scale.x, shape.scale.y)
								component.transform = shape.transform
								component.rotateBy(shape.rotation)
								component.offset = (shape.x, shape.y)
								ufo[glyph.name].appendComponent(
									component=component)
					if layer.guides:
						for guide in layer.guides:
							guideline = RGuideline()
							guideline.x = guide.position.x
							guideline.y = guide.position.y
							guideline.angle = guide.angle
							guideline.name = guide.name
							ufo[glyph.name].appendGuideline(guideline=guideline)

		return ufo


	def addKerning(self, font, ufo):
		__doc__ = """Provided a GSFont object and a fontParts UFO, build kerning into the font. Currently only tested for LTR."""
		glyph_ids = dict()
		for glyph in font.glyphs:
			glyph_ids[glyph.id] = glyph.name
		for master_id, value in font.kerning.items():
			for left_group, value in font.kerning[master_id].items():
				if left_group[0:4] == "@MMK":
					left_group = "public.kern1." + left_group[7:]
				else:
					left_group = glyph_ids[left_group]
				for right_group, value in value.items():
					if right_group[0:4] == "@MMK":
						right_group = "public.kern2." + right_group[7:]
					else:
						right_group = glyph_ids[right_group]
					ufo.kerning[(left_group, right_group)] = int(value)
					continue
		return ufo


	def addFeatureInclude(self, ufo, font):
		__doc__ = """Provided a fontParts UFO master, add feature includes for classes and individual features."""
		features = self.getFeatureDict(font)
		feature_str = """include(../features/prefixes.fea);
include(../features/classes.fea);
"""
		nl = "\n"
		for feature in features.keys():
			if not feature.startswith("size_"):
				feature_str = feature_str + f"""include(../features/{feature}.fea);{nl}"""
			ufo.features.text = feature_str
		return ufo

	# todo
	# def addLayerMastersToUFO(self, font, ufo):
	# 	special_layers = self.getSpecialLayers(font)
	# 	for layer in special_layers:
	# 		print(layer)
	# 	return ufo

	def addSkipExport(self,font,ufo):
		__doc__ =  """Provided a GSfont and a UFO, adds an item to lib.plist for skipping glyphs that are non-exporting and returns that UFO"""
		lib = RLib()
		lib["public.skipExportGlyphs"] = [g.name for g in font.glyphs if g.export == False]
		ufo.lib.update(lib)
		return ufo


	def exportUFOMasters(self, font, dest, format):
		__doc__ = """Provided a font object and a destination, exports a UFO for each master in the UFO, not including special layers (for that use generateMastersAtBraces)"""
		for master in font.masters:
			font_name = self.getFamilyNameWithMaster(font, master, format)
			ufo_file_name = "%s.ufo" % font_name
			ufo_file_path = os.path.join(dest, ufo_file_name)
			ufo = self.buildUfoFromMaster(master, font.glyphs)
			ufo = self.addGroups(font, ufo)
			ufo = self.addKerning(font, ufo)
			ufo = self.addFeatureInclude(ufo, font)
			ufo = self.addPostscriptNames(font, ufo)
			ufo = self.addSkipExport(font, ufo)
			# todo
			# if master.id == self.getOriginMaster(font) and self.brace_layers_as_layers == True:
			# 	ufo = self.addLayerMastersToUFO(font,ufo)
			# 	ufo.save(ufo_file_path)
			# else:
			# 	ufo.save(ufo_file_path)
			ufo.save(ufo_file_path)


	def getFeatureDict(self, font):
		__doc__ = """Provided a GSFont object, build an ordered dictionary of feature names and feature code based on those GSFeatures."""
		nl = "\n"
		features = OrderedDict()
		for feature in font.features:
			feature_code = ""
			for line in feature.code.splitlines():
				feature_code = feature_code + "  " + line + "\n"
			if feature.name[0:2] == "ss":
				feature_str = f"""feature {feature.name} {{ {nl}{feature_code}}} {feature.name};{nl}{nl}"""
				try:
					features["ss"] = features["ss"] + feature_str
				except:
					features["ss"] = feature_str
			elif feature.name[0:2] == "cv":
				feature_str = f"""feature {feature.name} {{ {nl}{feature_code}}} {feature.name};{nl}{nl}"""
				try:
					features["cv"] = features["cv"] + feature_str
				except:
					features["cv"] = feature_str
			else:
				features[feature.name] = f"""feature {feature.name} {{ {nl}{feature_code}}} {feature.name};{nl}"""
		try:
			features["ss"] = features["ss"].strip()
		except:
			None
		try:
			features["cv"] = features["cv"].strip()
		except:
			None

		# stat supercedes this, but keep around in case people need for static builds?
		if self.to_build["static"] is not False:
			size_arr = list(dict.fromkeys([instance.customParameters["Optical Size"] for instance in font.instances if instance.customParameters["Optical Size"]]))
			nl = "\n"
			for s,size in enumerate(size_arr):
				size_str = "feature size {\n"
				size_params = size.split(";")
				for i in range(0,len(size_params)-1):
					if i == 0:
						size_str = size_str + f"""    parameters {size_params[i]}"""
					else:
						size_str = size_str + " " + size_params[i]
				size_str = size_str + ";\n"
				size_str = size_str + f"""    sizemenuname "{size_params[-1]}";{nl}"""
				size_str = size_str + f"""    sizemenuname 1 "{size_params[-1]}";{nl}"""
				size_str = size_str + f"""    sizemenuname 1 21 0 "{size_params[-1]}";{nl}"""
				size_str = size_str + "} size;"
				key = "size_" + str(s)
				features[key] = size_str
			
		return features


	def writeFeatureFiles(self, font, dest):
		__doc__ = """Provided a GSFont object, writes the feature files from the getFeatureDict() dictionary that are referenced inside of the fontParts UFO masters."""

		# features 
		feature_dir = "features"
		os.mkdir(os.path.join(dest, feature_dir))
		features = self.getFeatureDict(font)
		for f_name, f_code in features.items():
			f_dest = os.path.join(dest, feature_dir, f"""{f_name}.fea""")
			f = open(f_dest, "w")
			f.write(f_code)
			f.close()

		# prefixes
		prefixes = ""
		for prefix in font.featurePrefixes:
			prefixes = prefixes + prefix.code + "\n"
		prefixes.strip()
		p_dest = os.path.join(dest, feature_dir, "prefixes.fea")
		f = open(p_dest, "w")
		f.write(prefixes)
		f.close()

		# classes
		font_classes = ""
		nl = "\n"
		for font_class in font.classes:
			font_classes = font_classes + \
				f"""@{font_class.name} = [{font_class.code.strip()}];{nl}{nl}"""
		font_classes.strip()
		c_dest = os.path.join(dest, feature_dir, "classes.fea")
		f = open(c_dest, "w")
		f.write(font_classes)
		f.close()

	def addPostscriptNames(self,font,ufo):
		__doc__ = """Provided a GSfont and a UFO, adds a lib.plist item for PostScript names that should be swapped out for production names on build"""
		lib = RLib()
		lib["public.postscriptNames"] = dict()
		glyphs = [g for g in font.glyphs if g.export == True]
		for glyph in glyphs:
			if glyph.productionName is not None and glyph.productionName != glyph.name:
				lib["public.postscriptNames"][glyph.name] = glyph.productionName
		ufo.lib.update(lib)
		return ufo


	def main(self):
		# use a copy to prevent modifying the open Glyphs file
		font = Glyphs.font.copy()
		# put all special layers on the same masterID
		self.alignSpecialLayers(font)
		# update any automatically generated features that need it
		self.updateFeatures(font)
		# remove overlaps and decompose glyphs if set at top
		self.removeOverlaps(font)
		self.decomposeGlyphs(font)

		# as a destination path (and empty it first if it exists)
		file_path = Glyphs.font.parent.fileURL().path()
		file_dir = os.path.dirname(file_path)
		dest = os.path.join(file_dir, 'ufo')
		if os.path.exists(dest):
			shutil.rmtree(dest)

		# when creating files below, export them to tmp_dir before we copy it over.
		# tempfile will automatically delete the temp files we generated
		with tempfile.TemporaryDirectory() as tmp_dir:
			temp_project_folder = os.path.join(tmp_dir, "ufo")
			os.mkdir(temp_project_folder)
			master_dir = os.path.join(temp_project_folder, "masters")
			os.mkdir(master_dir)

			# remove the OpenType substituties as they are now in the designspace as conditionsets
			self.removeSubsFromOT(font)

			# generate a designspace file based on metadata in the copy of the open font
			if self.to_build["static"] or (self.to_build["variable"] and not self.hasVariableFamilyName(font)):
				self.w.status.set(("Building designspace from font metadata...") + "\n" + self.w.status.get())
				print(" ")
				static_designspace_doc = self.getDesignSpaceDocument(font, "static")
				static_designspace_path = "%s/%s.designspace" % (
					temp_project_folder, self.getFamilyName(font, "static"))
				static_designspace_doc.write(static_designspace_path)
			if self.to_build["variable"] and self.hasVariableFamilyName(font):
				self.w.status.set(("Building variable designspace from font metadata...") + "\n" + self.w.status.get())
				print(" ")
				variable_designspace_doc = self.getDesignSpaceDocument(font, "variable")
				variable_designspace_path = "%s/%s.designspace" % (
					temp_project_folder, self.getFamilyName(font, "variable").replace(" ", ""))
				variable_designspace_doc.write(variable_designspace_path)
			self.w.status.set(("Building UFOs for masters...") + "\n" + self.w.status.get())
			print(" ")
			# We only need one set of masters
			if self.to_build["variable"] and not self.to_build["static"]:
				self.exportUFOMasters(font, temp_project_folder, "variable")
				if self.brace_layers_as_layers == False:
					self.w.status.set(("Building UFOs for brace layers if present...") + "\n" + self.w.status.get())
					print(" ")
					self.generateMastersAtBraces(font, temp_project_folder, "variable")
			else:
				self.exportUFOMasters(font, temp_project_folder, "static")
				if self.brace_layers_as_layers == False:
					self.w.status.set(("Building UFOs for brace layers if present...") + "\n" + self.w.status.get())
					print(" ")
					self.generateMastersAtBraces(font, temp_project_folder, "static")

			for file in glob.glob(os.path.join(temp_project_folder, "*.ufo")):
				shutil.move(file, master_dir)
			if self.to_add_build_script:
				self.addBuildScript(font, temp_project_folder)

			# write feature files that are imported by the masters
			self.writeFeatureFiles(font, temp_project_folder)

			# copy from temp dir to the destination. after this, tempfile will automatically delete the temp files
			shutil.copytree(temp_project_folder, dest)

		# open the output dir
		os.system("open %s" % dest.replace(" ", "\ "))
		self.w.status.set(("Done!") + "\n" + self.w.status.get())
		print(" ")

ExportUFOAndDesignspace()