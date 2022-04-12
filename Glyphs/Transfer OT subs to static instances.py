#MenuTitle: Transfer OT subs to static instances
# -*- coding: utf-8 -*-
__doc__="""
Transfers substitutions defined in OpenType features to the 'Rename Glyphs' custom parameter. Warning: this will overwrite existing Rename Glyphs parameters.
"""
import re

Font = Glyphs.font

feature = ""
warn = ""
feature_code = ""

for feature_itr in Font.features:
	for line in feature_itr.code.splitlines():
		if line.startswith("condition "):
			if feature != "" and feature_itr.name != feature:
				warn = "Condition code found in both %s and %s, aborting." % (feature, feature_itr.name)
				break
			feature = feature_itr.name
			feature_code = feature_itr.code


if warn:
	print(warn)
else:
	print("Found feature code: \n", feature_code)
	condition_index = 0
	condition_list = []
	replacement_list = [[]]
	
	for line in feature_code.splitlines():
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
	
	replace_instances = []
	for i in range(0,len(condition_list)):
		replace_instances.append([])
		
	for ri, replacement in enumerate(replacement_list):
		conditions = condition_list[ri]
		for instance in Font.instances:
			if instance.type == 0:
				count = 0
				for x,ins_axis_val in enumerate(instance.axes):
					axis_tag = Font.axes[x].axisTag
					for condition in conditions:
						if condition['tag'] == axis_tag:
							if condition['axis_range'][1] == 'nomax':
								if ins_axis_val > condition['axis_range'][0]:
									count = count + 1
							else:
								if condition['axis_range'][0] <= ins_axis_val <= condition['axis_range'][1]:
									count = count + 1
				if count == len(conditions):
					replace_instances[ri].append(instance)
					

	for i,instance_list in enumerate(replace_instances):
		for instance in instance_list:
			print("Subbing %s in instance %s" % (replacement_list[i],instance.preferredFamily + " " + instance.name))
			try:
				instance.customParameters['Rename Glyphs'] = instance.customParameters['Rename Glyphs'] + tuple(replacement_list[i])
			except:
				instance.customParameters['Rename Glyphs'] = tuple(replacement_list[i])
