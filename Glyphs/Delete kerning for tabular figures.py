#MenuTitle: Delete kerning for tabular figures
# -*- coding: utf-8 -*-
__doc__="""
Delete kerning and groups for tabular figures
"""

Font = Glyphs.font

numbers = "zero one two three four five six seven eight nine".split()
for i in range(0,10):
	for n in range(0,10):
		left = str(numbers[i])  + ".tf"
		right = str(numbers[n]) + ".tf"
		for master in Font.masters:
			print("Removing kerning and groups for %s-%s in %s master" % (left, right, master.name))
			if Font.glyphs[left].rightKerningGroup:
				Font.glyphs[left].rightKerningGroup = None
			if Font.glyphs[left].leftKerningGroup:
				Font.glyphs[left].leftKerningGroup = None
			if Font.glyphs[right].rightKerningGroup:
				Font.glyphs[right].rightKerningGroup = None
			if Font.glyphs[right].leftKerningGroup:
				Font.glyphs[right].leftKerningGroup = None
            Font.removeKerningForPair(master.id,left,right)