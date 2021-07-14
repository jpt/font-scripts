#MenuTitle: Reset Kern-On
# -*- coding: utf-8 -*-
__doc__="""
Deletes all Kern-On userData. To delete kerning and groups, use the other script.
"""

font = Glyphs.font

for master in font.masters:
	if(master.userData['KernOnIndependentPairs']):
		del(master.userData['KernOnIndependentPairs'])
	if(master.userData['KernOnModels']):
		del(master.userData['KernOnModels'])	
for glyph in font.glyphs:
	if(glyph.userData['KernOnSpecialSpacing']):
		del(glyph.userData['KernOnSpecialSpacing'])	