# MenuTitle: Export UFO and designspace files
__doc__ = """Exports UFO and designspace files. Supports substitutions defined in OT features, but not yet bracket layers. Brace layers supported, both as separate UFO masters or as Skateboard-style "support layers." Thanks to Rafał Buchner, Joancarles Casasín (https://robofont.com/documentation/how-tos/converting-from-glyphs-to-ufo/), and to the authors and maintainers of designspaceLib and fontParts."""

from GlyphsApp import GSInstance, GSFont, GSFontMaster, GSLayer
import re
import os
import vanilla
import tempfile
import shutil
import glob
import subprocess
from typing import Union
from collections import OrderedDict
from fontTools.designspaceLib import DesignSpaceDocument
from fontTools.designspaceLib import AxisDescriptor
from fontTools.designspaceLib import SourceDescriptor
from fontTools.designspaceLib import InstanceDescriptor
from fontTools.designspaceLib import RuleDescriptor
#from fontTools.designspaceLib import AxisLabelDescriptor disabled for now - https://forum.glyphsapp.com/t/question-about-stat-axis-value-tables/22400
from fontTools.designspaceLib import LocationLabelDescriptor
from fontParts.world import NewFont
from fontParts.fontshell.lib import RLib
from fontParts.fontshell.glyph import RGlyph
from fontParts.fontshell.layer import RLayer
from fontParts.fontshell.contour import RContour
from fontParts.fontshell.component import RComponent
from fontParts.fontshell.anchor import RAnchor
from fontParts.fontshell.guideline import RGuideline
from fontParts.fontshell.font import RFont

# Known problems:
#
# - Image not implemented in fontParts
# - Glyphs doesn't support explicit STAT axis label names
# - In the build scripts, fontmake will regenerate a bunch of instances for static fonts, which makes the process take forever, todo, fix whatever is causing that
# - If segments were added instead of points, building the RFonts would be faster, but complexity is "Georg warned me not to do it"-level. Todo, look into it.
#
# Todo:

# questionable function:
#
# def zeroNonSpacingMarks(self,font,ufo): — wait why does Glyphs do this? fewer bytes in production? probably will want to do this in script AFTER export if so
# 	non_spacing_marks = [glyph for glyph in font.glyphs if glyph.category == "Mark" and glyph.subCategory == "Nonspacing"]
# 	glyphs_to_zero = set([layer.parent.name for glyph in non_spacing_marks for layer in glyph.layers if layer.isSpecialLayer or layer.isMasterLayer])
# 	for glyph_name in glyphs_to_zero:
# 		# etc
#
# General todo:
# - split out a library
# - Add something like def addFontGuideline(self,ufo: RFont) -> RFont: for font-level guidelines
# - Add color to glyphs, maybe other things?
# - Speaking of color, this probably doesn't support color fonts at all? Lol
# - Does current kerning implementation handle all kinds? Probably only left and right? 
# - Use ufo2ft to generate kerning + GDEF + mark + mkmk? it doesnt seem necessary since fontmake will do it
# - add woff2_compress to build script
# - Hinting: public.verticalOrigin? public.truetype.roundOffsetToGrid? public.truetype.useMyMetrics? I forget which can be set in custom params. 
# - One designspace for VF? Have to look into designspace 5 spec more closely.
# - Finish the metadata in addFontInfoToUfo — mostly there.
# - Add support for bracket layers (in addition to OT based subs, which are already supported)
# - More elaborate build script possibilities (add size table that we're outputting but not importing in masters, for example; other tables too; add remove overlaps etc to build scripts)
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
		
		#vanilla UI

		margin_x = 20
		margin_y = 16
		spacer = 6
		ui_height = 24
		window_width  = 220 + margin_x * 2
		window_height = (ui_height * 12) + (spacer * 9) + (margin_y * 1.5)

		self.w = vanilla.FloatingWindow(
			( window_width, window_height ),
			"Export UFO and designspace"
		)
		
		xPos = margin_x		
		yPos = spacer * 2
	
		self.w.buttonLabel = vanilla.TextBox((margin_x, yPos, -margin_x, ui_height), "Designspace:", sizeStyle="small")

		yPos = yPos + spacer + ui_height / 2.33
		
		self.w.buttonSelectBuild = vanilla.SegmentedButton((margin_x, yPos, -margin_x, ui_height), [dict(title="Variable"), dict(title="Static"), dict(title="Both")],sizeStyle='small', callback=self.buttonSelectBuildCallback)
		self.w.buttonSelectBuild.set(2)
		
		yPos = yPos + spacer * 1.5 + ui_height

		self.w.buttonLabel2 = vanilla.TextBox((margin_x, yPos, -margin_x, ui_height), "Intermediate masters (brace layers) as:", sizeStyle="small")

		yPos = yPos + spacer + ui_height / 2.33
		
		self.w.buttonSelect2 = vanilla.SegmentedButton((margin_x, yPos, -margin_x, ui_height), [dict(title="Layers"), dict(title="Separate UFOs")],sizeStyle='small', callback=self.layerButtonCallback)
		self.w.buttonSelect2.set(0)
		
		yPos = yPos + spacer * 1 + ui_height

		self.w.checkBox = vanilla.CheckBox((margin_x, yPos, -margin_x, ui_height), "Generate fontmake build scripts", callback=self.checkBoxCallback, value=True, sizeStyle="small")

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
		self.brace_layers_as_layers = True # these are not in sync with default button values above, make sure to change both

		# todo, keep track of these in a preference
		self.to_decompose = []  # if you want, make an array of glyphnames (not unicodes)
		self.to_remove_overlap = []  # same

		self.keep_glyphs_lib = False
		self.production_names = False
		self.decompose_smart  = False

		self.w.open()

	# callback functions for vanilla

	def exportButton(self, sender):

		# get the glyphs to decompose etc
		self.to_decompose = self.w.decomposeField.get().split(" ")
		self.to_remove_overlap = self.w.overlapField.get().split(" ")
		
		# pre-load all the functions we call once on GSFont
		self.font = Glyphs.font.copy()
		self.origin_master = self.getOriginMaster()
		self.kerning = self.getKerning()
		self.variable_font_family = self.getVariableFontFamily()
		self.has_variable_font_name =  self.hasVariableFamilyName()
		self.special_layers = self.getSpecialLayers()
		self.muted_glyphs = self.getMutedGlyphs()
		self.special_layer_axes = self.getSpecialLayerAxes()
		self.axis_map_to_build = self.getAxisMapToBuild()
		self.origin_coords = self.getOriginCoords()

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

	# begin glyphs->UFO/designspace lib
	def addBuildScript(self, dest: str):
		"""
		Provided a font, destination and font name, creates a build script for the project
		"""
		if not self.to_add_build_script:
			return
		static_font_name = self.getFamilyName("static").replace(" ", "")
		vf_font_name = self.getFamilyName("variable").replace(" ", "")
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


	def decomposeGlyphs(self):
		"""
		Provided a font object, decomposes glyphs defined in to_decompose
		"""
		for glyph in self.to_decompose:
			if self.font.glyphs[glyph]:
				for layer in self.font.glyphs[glyph].layers:
					if len(layer.components) > 0:
						if layer.isMasterLayer or layer.isSpecialLayer:
							layer.decomposeComponents()


	def removeOverlaps(self):
		"""
		Provided a font object, removes overlaps in glyphs defined in to_remove_overlap
		"""
		for glyph in self.to_remove_overlap:
			if self.font.glyphs[glyph]:
				for layer in self.font.glyphs[glyph].layers:
					if layer.isMasterLayer or layer.isSpecialLayer:
						layer.removeOverlap()


	def getMutedGlyphs(self) -> list:
		"""
		Provided a font object, returns an array of non-exporting glyphs to be added as muted glyphs in the designspace
		"""
		return [glyph.name for glyph in self.font.glyphs if not glyph.export]


	def getBoundsByTag(self, tag: str) -> list:
		"""
		Provided a font object and an axis tag, returns an array in the form of [minimum, maximum] representing the bounds of an axis.

		Example use:
		min, max = getBoundsByTag(Glyphs.font,"wght")
		"""
		min = None
		max = None
		for i, axis in enumerate(self.font.axes):
			if axis.axisTag != tag:
				continue
			for master in self.font.masters:
				coord = master.axes[i]
				if min == None or coord < min:
					min = coord
				if max == None or coord > max:
					max = coord
		return [min, max]


	def getOriginMaster(self):
		"""
		Provided a font object, returns a string of the master ID referencing the master that is set to the variable font origin by custom paramter
		"""
		master_id = None
		for parameter in self.font.customParameters:
			if parameter.name == "Variable Font Origin":
				master_id = parameter.value
		if master_id is None:
			return self.font.masters[0].id
		return master_id


	def getOriginCoords(self) -> list[tuple]:
		"""
		Returns an array of axis coordinates specified on the variable font origin master.
		"""
		master_id = None
		for parameter in self.font.customParameters:
			if parameter.name == "Variable Font Origin":
				master_id = parameter.value
		if master_id is None:
			master_id = self.font.masters[0].id
		for master in self.font.masters:
			if master.id == master_id:
				return list(master.axes)


	def getAxisNameByTag(self, tag: str) -> str:
		"""
		Provided an axis tag, returns an axis name
		"""
		for axis in self.font.axes:
			if axis.axisTag == tag:
				return axis.name


	def hasVariableFamilyName(self) -> bool:
		"""
		Returns a boolean as to whether or not the font has a different VF name
		"""
		for instance in self.font.instances:
			if instance.variableStyleName:
				return True


	def getVariableFontFamily(self) -> str:
		"""
		Returns the name associated with a Variable Font Setting export
		"""
		for instance in self.font.instances:
			if instance.type == 1:
				return self.font.familyName + " " + instance.name
		return self.font.familyName


	def getFamilyName(self, format: str) -> str:
		"""
		Returns a font family name
		"""
		if format == "variable":
			family_name = self.variable_font_family
		else:
			family_name = self.font.familyName
		return family_name


	def getFamilyNameWithMaster(self, master: GSFontMaster, format: str) -> str:
		"""
		Provided a master, returns a font family name
		"""
		master_name = master.name
		if self.has_variable_font_name:
			if format == "static":
				font_name = "%s - %s" % (self.font.familyName, master_name)
			else:
				font_name = "%s - %s" % (self.variable_font_family, master_name)
		else:
			font_name = "%s - %s" % (self.font.familyName, master_name)

		return font_name


	def getStyleNameWithAxis(self, axes: list) -> str:
		"""
		Returns a style name based on special_layer_axes
		"""
		style_name = ""
		for i, axis in enumerate(axes):
			style_name = "%s %s %s" % (style_name, self.font.axes[i].name, axis)
		return style_name.strip()


	def getNameWithAxis(self, axes: list) -> str:
		"""
		Provided a dict of axes for a brace layer, returns a font family name
		"""
		if not self.to_build["static"]:
			font_name = "%s -" % self.variable_font_family
		else:
			font_name = "%s -" % (self.font.familyName)
		for i, axis in enumerate(axes):
			font_name = "%s %s %s" % (font_name, self.font.axes[i].name, axis)
		return font_name


	def alignSpecialLayers(self):
		"""
		Applies the same master ID referencing the variable font origin to all brace layers
		"""
		master_id = self.origin_master
		special_layers = self.special_layers
		# make them the same
		for layer in special_layers:
			layer.associatedMasterId = master_id


	def getSources(self, format: str) -> list[SourceDescriptor]:
		"""
		Creates and returns a list of designspaceLib SourceDescriptors
		"""
		sources = []
		for i, master in enumerate(self.font.masters):
			s = SourceDescriptor()
			if self.has_variable_font_name and not self.to_build["static"]:
				font_name = self.getFamilyNameWithMaster(master, "variable")
			else:
				font_name = self.getFamilyNameWithMaster(master, "static")
			s.filename = "masters/%s.ufo" % font_name
			s.familyName = self.getFamilyName(format)
			s.styleName = master.name
			locations = dict()
			for x, axis in enumerate(master.axes):
				locations[self.font.axes[x].name] = axis
			s.designLocation = locations
			s.mutedGlyphNames = self.muted_glyphs
			sources.append(s)
		return sources


	def addSources(self, doc: DesignSpaceDocument, sources):
		"""
		Provided a designspace document and array of source descriptors, adds those sources to the designspace doc.
		"""
		for source in sources:
			doc.addSource(source)


	def getSpecialLayers(self) -> list[GSLayer]:
		"""
		Returns a list of GSLayers that are brace layers (have intermediate master coordinates).
		"""
		return [l for g in self.font.glyphs for l in g.layers if l.isSpecialLayer and l.attributes['coordinates']]


	def getSpecialLayerAxes(self) -> list[int]:
		"""
		Returns a list of dicts containing name and coordinate information for each axis
		"""
		special_layer_axes = []
		layers = self.special_layers
		for layer in layers:
			layer_axes = dict()
			for i, coords in enumerate(layer.attributes['coordinates']):
				layer_axes[self.font.axes[i].name] = int(
					layer.attributes['coordinates'][coords])
			if layer_axes not in special_layer_axes:
				special_layer_axes.append(layer_axes)
		return special_layer_axes


	def getSpecialGlyphNames(self, axes: list[int]) -> list[str]:
		"""
		Provided a list of axis coordinates, returns all glyphs inside those coordinates
		"""
		glyph_names = []
		for glyph in self.font.glyphs:
			for layer in glyph.layers:
				if layer.isSpecialLayer and layer.attributes['coordinates']:
					coords = list(
						map(int, layer.attributes['coordinates'].values()))
					if coords == axes:
						glyph_names.append(glyph.name)
						continue
		return glyph_names


	def getMasterById(self, id: str) -> GSFontMaster:
		for master in self.font.masters:
			if master.id == id:
				return master

	def getSpecialSources(self, format: str) -> list[SourceDescriptor]:
		"""
		Returns an array of designspaceLib SourceDescriptors
		"""
		sources = []
		special_layer_axes = self.special_layer_axes
		for i, special_layer_axis in enumerate(special_layer_axes):
			axes = list(special_layer_axis.values())
			s = SourceDescriptor()
			master = self.getMasterById(self.origin_master)
			if self.brace_layers_as_layers:
				if self.hasVariableFamilyName() and not self.to_build["static"]:
					font_name = self.getFamilyNameWithMaster(master, "variable")
				else:
					font_name = self.getFamilyNameWithMaster(master, "static")
			else:
				font_name = self.getNameWithAxis(axes)
			s.location = special_layer_axis
			s.familyName = self.getFamilyName(format)
			s.styleName = master.name
			s.familyName = font_name
			s.filename = "masters/%s.ufo" % font_name
			if self.brace_layers_as_layers:
				layer_axis_name= "{" + ",".join(str(x) for x in list(special_layer_axis.values())) + "}"
				s.layerName = layer_axis_name
			sources.append(s)
		return sources


	def getAxisMapToBuild(self) -> dict:
		"""
		Iterates over the GSInstances in the font and returns a dict compatible with the Axis Mappings custom parameter, based on the Axis Location custom parameter of those GSInstances
		"""
		axis_map = dict()
		for instance in self.font.instances:
			if instance.type == 0:
				for i, internal in enumerate(instance.axes):
					if instance.customParameters["Axis Location"]:
						external = instance.customParameters["Axis Location"][i]['Location']
					else:
						external = internal
					axis_tag = self.font.axes[i].axisTag
					try:
						axis_map[axis_tag][internal] = external
					except:
						axis_map[axis_tag] = dict()
						axis_map[axis_tag][internal] = external
		
		return axis_map

	# Slightly different than above, for axis location labels. todo, once glyphs supports them
	#
	# def getAxisInstanceMap(self) -> Union[dict, None]:
	# 	"""
	#	Iterate over the GSInstances and return a dict compatible with the Axis Mappings custom parameter, based on the Axis Location custom parameter of those GSInstances
	#	"""
	# 	axis_map = dict()
	# 	for instance in self.font.instances:
	# 		if instance.customParameters["Axis Location"]:
	# 			if instance.type == 0:
	# 				for i, internal in enumerate(instance.axes):
	# 					external = instance.customParameters["Axis Location"][i]['Location']
	# 					axis_tag = self.font.axes[i].axisTag
	# 					try:
	# 						axis_map[axis_tag][internal] = external
	# 					except:
	# 						axis_map[axis_tag] = dict()
	# 						axis_map[axis_tag][internal] = external
	# 	if len(axis_map):
	# 		return axis_map
	# 	else:
	# 	 	return None


	def getLabels(self, format: str) -> list[LocationLabelDescriptor]:
		"""
		Provided a font format string, return a list of LocationLabelDescriptors
		"""
		labels = []
		
		instances = [instance for instance in self.font.instances if instance.active == True and instance.type == 0]
		for instance in instances:
			if format == "variable" and instance.variableStyleName:
				style_name = instance.variableStyleName
			else:
				style_name = instance.name

			elidable = False
			for i,axis in enumerate(instance.axes):
				axis_tag = self.font.axes[i].axisTag
				if instance.customParameters["Elidable STAT Axis Value Name"] and instance.customParameters["Elidable STAT Axis Value Name"] == axis_tag:
					elidable = True
			
			if self.font.customParameters["Axis Mappings"]:
				axis_map = self.font.customParameters["Axis Mappings"]
			else:
				axis_map = self.axis_map_to_build
			
			user_location = dict()
			for i,axis in enumerate(instance.axes):
				user_name = self.font.axes[i].name
				user_coord = axis_map[self.font.axes[i].axisTag][axis]
				user_location[user_name] = user_coord

			label = LocationLabelDescriptor(name=style_name,userLocation=user_location,elidable=elidable)
			if label not in labels:
				labels.append(label)
		labels = list(dict.fromkeys(labels))
		return labels


	def addLabels(self,doc: DesignSpaceDocument, labels: list[LocationLabelDescriptor]) -> DesignSpaceDocument:
		"""
		Provided a DesignSpaceDocument and a list of LocationLabelDescriptors, adds those labels to the doc
		"""
		doc.locationLabels = labels
		return doc

	#
	# Once Glyphs supports full STAT....
	#
	# def getAxisLabelList(self,font,axis_index,format):
	# 	"""
	#	Provided a GSfont object, the index of a GSAxis, and the output format, returns a list of labels
	#	"""
	# 	axis_tag = font.axes[axis_index].axisTag
	# 	if font.customParameters["Axis Mappings"]:
	# 		axis_map = font.customParameters["Axis Mappings"][axis_tag]
	# 	else:
	# 		axis_map = self.getAxisInstanceMap(font)
		
	# 	axis_range = axis_map[axis_tag]
	# 	axis_list = list(axis_range.items())

	# 	labels = []
	# 	label_user = []
		
	# 	instances = [instance for instance in font.instances if instance.active == True and instance.type == 0]
	# 	for instance in instances:
	# 		#
	# 		# tricky if there's an opsz... or many axes ... see forum link above about Glyphs not really supporting this
	# 		#
	# 		# potentially, like:
	# 		#
	# 		# if format == "variable" and instance.variableStyleName:
	# 		#	style_name = instance.variableStyleName
	# 		# else:
	# 		#	style_name = instance.name
	# 		# 
	# 		# but also subfamily, etc...

	# 		if axis_tag == "opsz" and instance.customParameters["Optical Size"]:
	# 			style_name = instance.customParameters["Optical Size"].split(";")[-1]
	# 		else:
	# 			style_name = instance.name

	# 		if instance.customParameters["Style Name as STAT entry"] and instance.customParameters["Style Name as STAT entry"] == axis_tag:
	# 			if instance.customParameters["Elidable STAT Axis Value Name"]:
	# 				elidable = True
	# 			else:
	# 				elidable = False
	# 			user_min = axis_list[0][1]
	# 			user_max = axis_list[-1][1]
	# 			user_val = axis_range[instance.axes[axis_index]]
	# 			label = AxisLabelDescriptor(name=style_name,userValue=user_val, userMinimum=user_min, userMaximum=user_max,elidable=elidable)
	# 			if user_val not in label_user:
	# 				label_user.append(user_val)
	# 				labels.append(label)
	# 	return labels

		
	def addAxes(self, doc: DesignSpaceDocument):
		"""
		Provided a designspace doc and a font object, adds axes from that font to the designspace as AxisDescriptors
		"""
		for i, axis in enumerate(self.font.axes):
			if self.font.customParameters["Axis Mappings"]:
				axis_map = self.font.customParameters["Axis Mappings"][axis.axisTag]
			else:
				axis_map = self.axis_map_to_build
				if axis_map is not None:
					axis_map = axis_map[axis.axisTag]
			if axis_map:
				a = AxisDescriptor()
				
				axis_min, axis_max = self.getBoundsByTag(axis.axisTag)

				for k in sorted(axis_map.keys()):
					a.map.append((axis_map[k], k))
				try:
					a.maximum = axis_map[axis_max]
					a.minimum = axis_map[axis_min]
				except:
					self.w.status.set("\n\nError: the font's axis mappings don't match its real min/max coords\n\n" + self.w.status.get())
					print(" ")
				origin_coord = self.origin_coords[i]
				user_origin = axis_map[origin_coord]
				# todo for locationlabels
				#a.axisOrdering = i
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


	def getConditionsFromOT(self):
		"""
		Returns two arrays: one a list of OT substitution conditions, and one of the glyph replacements to make given those conditions. Each array has the same index.
	
		Example use:
		condition_list, replacement_list = getConditionsFromOT(font)

		"""
		feature_code = ""
		for feature_itr in self.font.features:
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
					axis_name = self.getAxisNameByTag(tag)
					m = re.findall("\d+(?:\.|)\d*", condition)
					cond_min = float(m[0])
					if len(m) > 1:
						cond_max = float(m[1])
						range_dict = dict(
							name=axis_name, minimum=cond_min, maximum=cond_max)
					else:
						_, cond_max = self.getBoundsByTag(tag)
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


	def removeSubsFromOT(self):
		"""
		Removes subsitutions in feature code
		"""
		feature_index = None
		# find which if any feature has the conditional substitutions
		for i, feature_itr in enumerate(self.font.features):
			for line in feature_itr.code.splitlines():
				if line.startswith("condition "):
					feature_index = i
					break
		if feature_index:
			self.font.features[feature_index].code = re.sub(
				r'#ifdef VARIABLE.*?#endif', '', self.font.features[feature_index].code, flags=re.DOTALL)
			# delete the feature if it's empty after removing the subs
			if not self.font.features[feature_index].code.strip():
				del(self.font.features[feature_index])
			


	def applyConditionsToRules(self, doc: DesignSpaceDocument, condition_list: list, replacement_list: list):
		"""
		Provided a designspace document, condition list, and replacement list (as provided by getConditionsFromOT), adds matching designspace RuleDescriptors to the doc
		"""
		rules = []
		for i, condition in enumerate(condition_list):
			r = RuleDescriptor()
			r.name = "Rule %s" % str(i+1)
			r.conditionSets.append(condition)
			for sub in replacement_list[i]:
				r.subs.append(sub)
			rules.append(r)
		doc.rules = rules


	def getInstances(self, format: str) -> list[InstanceDescriptor]:
		"""
		Provided a format string, returns a list of designspaceLib InstanceDescriptors
		"""
		instances_to_return = []
		for instance in self.font.instances:
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
				family_name = self.variable_font_family
			else:
				if instance.preferredFamily:
					family_name = instance.preferredFamily
				else:
					family_name = self.font.familyName
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
				design_location[self.font.axes[i].name] = axis_value
			ins.designLocation = design_location
			
			axis_map = self.axis_map_to_build
			user_location = {}
			for i, axis_value in enumerate(instance.axes):
				user_location[self.font.axes[i].name] = axis_map[self.font.axes[i].axisTag][axis_value]
			ins.userLocation = user_location

			instances_to_return.append(ins)
		return instances_to_return


	def addInstances(self, doc: DesignSpaceDocument, instances: list[InstanceDescriptor]):
		"""
		Provided a doc and list of designspace InstanceDescriptors, adds them to the doc
		"""
		for instance in instances:
			doc.addInstance(instance)


	def updateFeatures(self):
		"""
		Updates automatically generated OpenType features
		"""
		for feature in self.font.features:
			if feature.automatic:
				feature.update()


	def getDesignSpaceDocument(self, format: str) -> DesignSpaceDocument:
		"""
		Returns a designspaceLib DesignSpaceDocument populated with informated from the provided font object
		"""
		doc = DesignSpaceDocument()
		self.addAxes(doc)
		sources = self.getSources(format)

		self.addSources(doc, sources)
		special_sources = self.getSpecialSources(format)
		self.addSources(doc, special_sources)
		instances = self.getInstances(format)
		self.addInstances(doc, instances)
		labels = self.getLabels(format)
		self.addLabels(doc,labels)
		condition_list, replacement_list = self.getConditionsFromOT()
		self.applyConditionsToRules(doc, condition_list, replacement_list)
		doc.rulesProcessingLast = True
		return doc


	def generateMastersAtBraces(self, temp_project_folder: str, format: str):
		"""
		Provided an export destination and format string, exports all brace layers as individual UFO masters
		"""

		# todo - do this as a generic RFont and not using ins.interpolatedFont
		special_layer_axes = self.special_layer_axes
		for i, special_layer_axis in enumerate(special_layer_axes):
			axes = list(special_layer_axis.values())
			self.font.instances.append(GSInstance())
			ins = self.font.instances[-1]
			ins.name = self.getNameWithAxis(axes)
			ufo_file_name = "%s.ufo" % ins.name
			style_name = self.getStyleNameWithAxis(axes)
			ins.styleName = style_name
			ins.axes = axes
			brace_font = ins.interpolatedFont
			brace_font.masters[0].name = style_name
			brace_glyphs = self.getSpecialGlyphNames(axes)
			for glyph in self.font.glyphs:
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
			ufo = self.buildUfoFromMaster(brace_font.masters[0])
			ufo.save(ufo_file_path)

	
	def getIndexByMaster(self, font: GSFont, master: GSFontMaster) -> int:
		"""
		Provided a GSFontMaster, returns its index within its parent GSFont
		"""
		for i, m in enumerate(font.masters):
			if master.id == m.id:
				return i


	def addGroups(self, ufo: RFont) -> RFont:
		"""
		Provided an RFont, writes kerning groups from GSFont to RFont
		"""
		groups = {"left": {}, "right": {}}
		for glyph in self.font.glyphs:
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

	def formatValue(self,value,type: str) -> Union[int,float,bool,None]:
		# this function saves some lines of code when setting the ufo.info attributes
		if not value:
			return None
		if type == "int":
			return int(value)
		elif type == "float":
			return float(value)
		elif type == "bool":
			return bool(value)

	def addFontInfoToUfo(self,master: GSFontMaster, ufo: RFont) -> RFont:
		"""
		Provided a GSFontMaster and an RFont, returns an RFont with OpenType metadata from that master (and its parent GSFont)
		"""
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
		# ufo.info.openTypeNameCompatibleFullName = font.compatibleFullName - this returns "None"
		ufo.info.openTypeNameSampleText = font.sampleText
		#ufo.info.openTypeNameWWSFamilyName = font.customParameters["WWS Family Name"] but isnt this usually set in instanced?
		# These are for instances only, no? Hmmmmmmm, generate features and leave to build script to set this? todo
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

		ufo.info.openTypeOS2Panose = [int(p) for p in font.customParameters["panose"]] if font.customParameters["panose"] else None
		
		#ufo.info.openTypeOS2FamilyClass =  ? 
		#ufo.info.openTypeOS2UnicodeRanges =
		#ufo.info.openTypeOS2CodePageRanges = 

		ufo.info.openTypeOS2TypoAscender = self.formatValue(master.customParameters["typoAscender"],"int")
		ufo.info.openTypeOS2TypoDescender = self.formatValue(master.customParameters["typoDescender"],"int")
		ufo.info.openTypeOS2TypoLineGap = self.formatValue(master.customParameters["typoLineGap"],"int")

		ufo.info.openTypeOS2WinAscent = self.formatValue(master.customParameters["winAscent"],"int")
		ufo.info.openTypeOS2WinDescent = self.formatValue(master.customParameters["winDescent"],"int")

		try:
			ufo.info.openTypeOS2Type = [int(font.customParameters["fsType"]["value"])]
		except:
			ufo.info.openTypeOS2Type = [0]

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

	    # check font.customParams["Use Typo Metrics"] / convert upm

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

		# todo
		ufo.info.postscriptUniqueID = font.customParameters["uniqueID"]
		ufo.info.postscriptUnderlineThickness = self.formatValue(master.customParameters["underlineThickness"],"int")
		ufo.info.postscriptUnderlinePosition = self.formatValue(master.customParameters["underlinePosition"],"int")
		ufo.info.postscriptIsFixedPitch =  self.formatValue(font.customParameters["isFixedPitch"],"bool")

		#todo ufo.info.postscriptBlueValues = [float(b) for b in master.blueValues]
		#todo ufo.info.postscriptOtherBlues = [float(b) for b in master.otherBlues]
		#ufo.info.postscriptFamilyBlues = to calc
		#ufo.info.postscriptFamilyOtherBlues = 
		ufo.info.postscriptStemSnapH = [int(stem) for i,stem in enumerate(master.stems) if font.stems[i].horizontal]
		ufo.info.postscriptStemSnapV = [int(stem) for i,stem in enumerate(master.stems) if not font.stems[i].horizontal]

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
		# anything rleated to GPOS?
		# TTFZones / TTFBlueFuzz ??


		return ufo

	def getGlyphFromGSLayer(self, ufo: RFont, layer: GSLayer) -> RGlyph:
		"""
		Provided a GSLayer and an RFfont, creates an RGlyph like the layer and returns it, while adding glyph-level guides to the RFont
		"""
		glyph = RGlyph()
		glyph.width = layer.width
		glyph.leftMargin = layer.LSB
		glyph.rightMargin = layer.RSB
		glyph.name = layer.parent.name
		if layer.anchors:
			for anchor in layer.anchors:
				ufo_anchor = RAnchor()
				ufo_anchor.name = anchor.name
				ufo_anchor.x = anchor.x
				ufo_anchor.y = anchor.y
				glyph.appendAnchor(anchor=ufo_anchor)
		if layer.shapes:
			for shape in layer.shapes:
				# Countours
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
					glyph.appendContour(contour)
				# Components
				elif shape.shapeType == 4:
					component = RComponent()
					component.baseGlyph = shape.name
					component.scale = (shape.scale.x, shape.scale.y)
					component.transform = shape.transform
					component.rotateBy(shape.rotation)
					component.offset = (shape.x, shape.y)
					glyph.appendComponent(
						component=component)
		# Guidelines
		if layer.guides:
			for guide in layer.guides:
				guideline = RGuideline()
				guideline.x = guide.position.x
				guideline.y = guide.position.y
				guideline.angle = guide.angle
				guideline.name = guide.name
				ufo[glyph.name].appendGuideline(guideline=guideline)

		# Image - I don't think this is actually implemented in fontparts yet?
		# if layer.backgroundImage:
		# 	bg_img = layer.backgroundImage
		# 	path = bg_img.path
		# 	position = (int(bg_img.position.x), int(bg_img.position.y))
		# 	scale = (int(bg_img.scale.x), int(bg_img.scale.y))
		# 	transformation = bg_img.transform
		# 	rotation = bg_img.rotation
		# 	ufo_img = glyph.addImage(path=path,position=position,scale=scale)
		# 	ufo_img.rotateBy(rotation)
		# 	ufo_img.transformation = transformation

		return glyph
	

	def buildUfoFromMaster(self, master: GSFontMaster) -> RFont:
		"""
		Provided a GSMFontMaster and a list of glyph names to be used in that master, return a fontParts UFO
		"""
		font = master.font
		master_index = self.getIndexByMaster(font,master)
		print(master_index)

		self.w.status.set(("Building master: %s - %s" % (master.font.familyName, master.name)) + "\n" + self.w.status.get())
		print(" ")

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
					r_glyph = self.getGlyphFromGSLayer(ufo,layer)
					ufo[glyph.name] = r_glyph
					if glyph.unicodes is not None:
						ufo[glyph.name].unicodes = glyph.unicodes
					ufo[glyph.name].export = glyph.export
		return ufo

	def getKerning(self) -> dict:
		"""
		Returns a dict with two types of kerning: a string for features, and a list [left glyph, right glyph, value] for UFO kerning.
		"""
		kerning = { "feature": {}, "ufo": {}}
		
		if not self.font.kerning.items():
			return kerning
		
		glyph_ids = dict()
		
		feature_kerning = dict()
		ufo_kerning = dict()
		for glyph in self.font.glyphs:
			glyph_ids[glyph.id] = glyph.name
		for master_id, value in self.font.kerning.items():
			kerning_str = ""
			for left_group, value in self.font.kerning[master_id].items():
				if left_group[0:4] == "@MMK":
					left_ufo_group = "public.kern1." + left_group[7:]
				else:
					left_ufo_group = glyph_ids[left_group]
				for right_group, value in value.items():
					if right_group[0:4] == "@MMK":
						right_ufo_group = "public.kern2." + right_group[7:]
					else:
						right_ufo_group = glyph_ids[right_group]
					try:
						ufo_kerning[master_id].append([left_ufo_group,right_ufo_group,int(value)])
					except:
						ufo_kerning[master_id] = []
						ufo_kerning[master_id].append([left_ufo_group,right_ufo_group,int(value)])			
					continue
				kerning_str += f"""        pos {left_group} {right_group} {value};\n"""	
			kerning_str.strip()

			use_extension = " useExtension" if self.font.customParameters["Use Extension Kerning"] else None
			feature_kerning_str = f"""feature kern {{
    lookup kern_DFLT{use_extension if use_extension else ""} {{
{kerning_str}    }}
}}
"""
			try:
				feature_kerning[master_id] = feature_kerning_str
				kerning["ufo"][master_id] = ufo_kerning[master_id]
				kerning["feature"][master_id] = feature_kerning[master_id]
			except:
				pass

		return kerning


	def addUfoKerning(self, ufo: RFont, master_id: str) -> RFont:
		"""
		Given a dict of kerning, build kerning into the ufo and return it
		"""
		try:
			for l,r,v in self.kerning["ufo"][master_id]:
				ufo.kerning[(l,r)] = v
		except:
			pass
		return ufo


	def addFeatureIncludes(self, ufo: RFont, master: GSFontMaster) -> RFont:
		"""
		Provided an RFont master, add feature includes for classes and individual features, and write features specific to the master.
		"""
		features = self.getFeatureDict(master.font)
		feature_str = """include(../features/prefixes.fea);
include(../features/classes.fea);
"""
		font = master.font
		nl = "\n"
		for feature in features.keys():
			if not feature.startswith("size_"):
				feature_str = feature_str + f"""include(../features/{feature}.fea);{nl}"""
			ufo.features.text = feature_str

		# todo - feature kerning currently broken, need lookups etc, and right order -- uncomment when done

		# try:
		# 	ufo.features.text += self.kerning["feature"][master.id]
		# except:
		# 	pass

		return ufo

	def addGlyphLayersToUfo(self, ufo: RFont) -> RFont:
		"""
		Given an RFont, adds special layer at the Glyph level
		"""
		brace_layers = self.special_layers
		for layer in brace_layers:
			axes = list(dict.fromkeys(layer.attributes['coordinates'].values()))
			axes = [str(a) for a in axes]
			special_layer_name =  "{" + ",".join(axes) + "}"
			glyph = self.getGlyphFromGSLayer(ufo,layer)
			glyph.name = layer.parent.name
			try:
				r_layer = ufo.getLayer(special_layer_name)
			except:
				r_layer = RLayer()
				r_layer.name = special_layer_name
				r_layer = ufo.insertLayer(r_layer)
			r_layer.insertGlyph(glyph)
		return ufo


	def addLayersToUfo(self, ufo: RFont) -> RFont:
		special_layer_axes = self.special_layer_axes
		for i, special_layer_axis in enumerate(special_layer_axes):
			axes = list(special_layer_axis.values())
			axes = [str(a) for a in axes]
			special_layer_name =  "{" + ",".join(axes) + "}"
			try:
				r_layer = ufo.getLayer(special_layer_name)
			except:
				r_layer = RLayer()
				r_layer.name = special_layer_name
				r_layer = ufo.insertLayer(r_layer)
		return ufo


	def addSkipExport(self, ufo: RFont) -> RFont:
		__doc__ =  """Provided an RFont, adds an item to lib.plist for skipping glyphs that are non-exporting and returns that UFO"""
		lib = RLib()
		lib["public.skipExportGlyphs"] = [g.name for g in self.font.glyphs if g.export == False]
		ufo.lib.update(lib)
		return ufo


	def addGlyphOrder(self, ufo: RFont) -> RFont:
		ufo.glyphOrder = list(g.name for g in self.font.glyphs)
		return ufo


	def exportUFOMasters(self, dest: str, format: str):
		"""
		Provided a destination and format, exports a UFO for each master in the GSFont, not including special layers (for that use generateMastersAtBraces)
		"""
		for master in self.font.masters:
			font_name = self.getFamilyNameWithMaster(master, format)
			ufo_file_name = "%s.ufo" % font_name
			ufo_file_path = os.path.join(dest, ufo_file_name)
			ufo = self.buildUfoFromMaster(master)
			ufo = self.addGroups(ufo)
			ufo = self.addUfoKerning(ufo, master.id)
			ufo = self.addFeatureIncludes(ufo, master)
			ufo = self.addPostscriptNames(ufo)
			ufo = self.addGlyphOrder(ufo)
			ufo = self.addSkipExport(ufo)
			#ufo = self.zeroNonSpacingMarks(font,ufo)
			if self.brace_layers_as_layers:
				ufo = self.addLayersToUfo(ufo)
				if master.id == self.origin_master:
					ufo = self.addGlyphLayersToUfo(ufo)
			ufo.save(ufo_file_path)

	def getFeatureDict(self, font: GSFont) -> OrderedDict:
		"""
		Provided a GSFont object, build an ordered dictionary of feature names and feature code based on those GSFeatures.
		"""
		nl = "\n"
		features = OrderedDict()

		for feature in font.features:
			feature_code = ""
			for line in feature.code.splitlines():
				feature_code = feature_code + "  " + line + "\n"
			## If it's a stylistic set, concatenate into one feature file
			if feature.name[0:2] == "ss":
				feature_str = f"""feature {feature.name} {{ {nl}{feature_code}}} {feature.name};{nl}{nl}"""
				try:
					features["ss"] = features["ss"] + feature_str
				except:
					features["ss"] = feature_str
			## If it's a character variant, concatenate into one feature file
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
			pass
		try:
			features["cv"] = features["cv"].strip()
		except:
			pass

		# stat supercedes this, but keep around in case people need for static builds? todo: look into it
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


	def writeFeatureFiles(self, dest: str):
		"""
		Provided a destination, writes the feature files from the getFeatureDict() dictionary that are referenced inside of the fontParts UFO masters.
		"""

		# features 
		feature_dir = "features"
		os.mkdir(os.path.join(dest, feature_dir))
		features = self.getFeatureDict(self.font)
		for f_name, f_code in features.items():
			f_dest = os.path.join(dest, feature_dir, f"""{f_name}.fea""")
			f = open(f_dest, "w")
			f.write(f_code)
			f.close()

		# prefixes
		prefixes = ""
		for prefix in self.font.featurePrefixes:
			prefixes = prefixes + prefix.code + "\n"
		prefixes.strip()
		p_dest = os.path.join(dest, feature_dir, "prefixes.fea")
		f = open(p_dest, "w")
		f.write(prefixes)
		f.close()

		# classes
		font_classes = ""
		nl = "\n"
		for font_class in self.font.classes:
			font_classes = font_classes + \
				f"""@{font_class.name} = [{font_class.code.strip()}];{nl}{nl}"""
		font_classes.strip()
		c_dest = os.path.join(dest, feature_dir, "classes.fea")
		f = open(c_dest, "w")
		f.write(font_classes)
		f.close()

	def addPostscriptNames(self, ufo: RFont) -> RFont:
		"""
		Provided an RFont, adds a lib.plist item for PostScript names that should be swapped out for production names on build
		"""
		lib = RLib()
		lib["public.postscriptNames"] = dict()
		glyphs = [g for g in self.font.glyphs if g.export == True]
		for glyph in glyphs:
			if glyph.productionName is not None and glyph.productionName != glyph.name:
				lib["public.postscriptNames"][glyph.name] = glyph.productionName
		ufo.lib.update(lib)
		return ufo


	def decomposeSmartComponents(self):
		for glyph in self.font.glyphs:
			if glyph.smartComponentAxes: 
				for layer in glyph.layers:
					if layer.isMasterLayer or layer.isSpecialLayer:
						if len(layer.components) > 0:
							for component in layer.components:
								if component.smartComponentValues:
									component.decompose()
	
	def decomposeCorners(self):
		for glyph in self.font.glyphs:
			for layer in glyph.layers:
				if layer.isMasterLayer or layer.isSpecialLayer:
					layer.decomposeCorners()
					
	def main(self):
		# use a copy to prevent modifying the open Glyphs file
		# put all special layers on the same masterID
		self.alignSpecialLayers()
		# update any automatically generated features that need it
		self.updateFeatures()
		# decompose smart components
		self.decomposeSmartComponents()
		# decompose smart corners
		self.decomposeCorners()

		# remove overlaps and decompose glyphs if set at top
		self.removeOverlaps()
		self.decomposeGlyphs()

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
			self.removeSubsFromOT()

			# generate a designspace file based on metadata in the copy of the open font
			if self.to_build["static"] or self.to_build["variable"] and not self.has_variable_font_name:
				self.w.status.set(("Building designspace from font metadata...") + "\n" + self.w.status.get())
				print(" ")
				static_designspace_doc = self.getDesignSpaceDocument("static")
				static_designspace_path = "%s/%s.designspace" % (
					temp_project_folder, self.getFamilyName("static").replace(" ",""))
				static_designspace_doc.write(static_designspace_path)
			if self.to_build["variable"] and self.has_variable_font_name:
				self.w.status.set(("Building variable designspace from font metadata...") + "\n" + self.w.status.get())
				print(" ")
				variable_designspace_doc = self.getDesignSpaceDocument(f"variable")
				variable_designspace_path = "%s/%s.designspace" % (
					temp_project_folder, self.getFamilyName("variable").replace(" ", ""))
				variable_designspace_doc.write(variable_designspace_path)
			self.w.status.set(("Building UFOs for masters...") + "\n" + self.w.status.get())
			print(" ")
			# We only need one set of masters
			if self.to_build["variable"] and not self.to_build["static"]:
				self.exportUFOMasters(temp_project_folder, "variable")
				if not self.brace_layers_as_layers:
					self.w.status.set(("Building UFOs for brace layers if present...") + "\n" + self.w.status.get())
					print(" ")
					self.generateMastersAtBraces(temp_project_folder, "variable")
			else:
				self.exportUFOMasters(temp_project_folder, "static")
				if not self.brace_layers_as_layers:
					self.w.status.set(("Building UFOs for brace layers if present...") + "\n" + self.w.status.get())
					print(" ")
					self.generateMastersAtBraces(temp_project_folder, "static")

			for file in glob.glob(os.path.join(temp_project_folder, "*.ufo")):
				shutil.move(file, master_dir)
			if self.to_add_build_script:
				self.addBuildScript(temp_project_folder)

			# write feature files that are imported by the masters
			self.writeFeatureFiles(temp_project_folder)

			# copy from temp dir to the destination. after this, tempfile will automatically delete the temp files
			shutil.copytree(temp_project_folder, dest)

		# open the output dir
		os.system("open %s" % dest.replace(" ", "\ "))
		self.w.status.set(("Done!") + "\n" + self.w.status.get())
		print(" ")

ExportUFOAndDesignspace()
