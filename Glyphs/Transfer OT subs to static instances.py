#MenuTitle: Transfer OT subs to static instances
# -*- coding: utf-8 -*-
__doc__="""
Transfers substitutions defined in OpenType features to the 'Rename Glyphs' custom parameter. Warning: this will overwrite existing Rename Glyphs parameters.
"""

import vanilla, re

Font = Glyphs.font

class SelectAndTransfer( object ):

	def __init__( self ):

		margin_x = 20
		margin_y = 16
		button_width = 220
		button_height = 24
		spacer = 6
		input_width = button_width
		input_height = button_height
		label_width = button_width
		label_height = button_height
		window_width  = button_width + margin_x * 2
		window_height = (button_height * 3) + (spacer * 1) + (margin_y * 2)
		self.w = vanilla.FloatingWindow(
			( window_width, window_height ),
			"Transfer OT subs to instances"
		)

		xPos = margin_x
		yPos = margin_y

		self.w.Label = vanilla.TextBox((xPos, yPos, label_width, label_height),"Select the feature where your subs are:", sizeStyle="small")
		
		yPos = yPos + label_height
		
		features = []
		rlig = False
		for feature in Font.features:
			if feature.name != "rlig": # Make rlig first since it's what Glyphs tutorial suggests
				features.append(feature.name)
			else:
				rlig = True
				continue
		if rlig:
			features.insert(0,"rlig")
		
		self.w.FeatureList = vanilla.PopUpButton((xPos, yPos, button_width, button_height),features)
		
		yPos = yPos + spacer + button_height
		
		self.w.Button = vanilla.Button((xPos, yPos, button_width, button_height),"Add subs to instances",callback=self.buttonCallback)

		self.w.open()

	def getAxisTagByIndex(self, index):
		return Font.axes[index].axisTag
			
	def buttonCallback( self, sender ):
		feature = self.w.FeatureList.getItems()[self.w.FeatureList.get()]
		feature_code = Font.features["rlig"].code.splitlines()
		condition_index = 0
		
		condition_list = []
		replacement_list = [[]]
		
		for line in feature_code:
			if line.startswith("condition"):
				conditions = []
				replacements = []
				conditions_list = line.split(",")
				ranges = []
				for condition in conditions_list:
					m = re.findall("< (\w{4})", condition)
					tag = m[0]
					m = re.findall("\d+(?:\.|)\d*", condition)
					cond_min = float(m[0])
					if len(m) > 1:
						cond_max = float(m[1])
					else:
						cond_max = "nomax"
					range_dict = dict(tag=tag,axis_range=[cond_min,cond_max])
					conditions.append(range_dict)
				condition_list.append(conditions)
				condition_index = condition_index + 1
			elif line.startswith("sub"):	
				m = re.findall("sub (.*) by (.*);", line)[0]
				replace = m[0] + "=" + m[1]
				try:
					replacement_list[condition_index-1].append(replace)
				except:
					replacement_list.append(list())
					replacement_list[condition_index-1].append(replace)
		
					
		for instance in Font.instances:
			for n,axis in enumerate(instance.axes):
				axis_tag = Font.axes[n].axisTag
				conditions_to_meet = len(condition_list)
				conditions_met = 0
				for i,sub_list in enumerate(condition_list):		
					for sub in sub_list:
						if(sub['tag'] == axis_tag):
							if sub['axis_range'][1] == "nomax":
								if axis > sub['axis_range'][0]:
									conditions_met = conditions_met + 1
									
							else:
								if sub['axis_range'][0] <= axis <= sub['axis_range'][1]:
									conditions_met = conditions_met + 1
					if conditions_met == conditions_to_meet:
						print("Subbing %s in instance %s" % (replacement_list[i],instance))
						instance.customParameters['Rename Glyphs'] = tuple(replacement_list[i])
						conditions_met = 0
						continue

						
SelectAndTransfer()