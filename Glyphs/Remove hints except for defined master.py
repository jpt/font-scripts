#MenuTitle: Remove hints except for defined master
# -*- coding: utf-8 -*-

__doc__="""
Removes all PS and TT hints except for those in the defined master (Font->Customer Parameters->Get Hints From Master) 
"""

Font = Glyphs.font
master_id = Font.customParameters['Get Hints From Master']
for glyph in Font.glyphs:
	for layer in glyph.layers:
		if layer.isMasterLayer and layer.master.id != master_id:
			if len(layer.hints) > 0:
				for i,hint in enumerate(layer.hints):
					if hint.isTrueType:
						print("Removing TrueType hints from %s %s" % (glyph.name, layer.name))
					elif hint.isPostScript:
						print("Removing PostScript hints from %s %s" % (glyph.name, layer.name))
				for i in range(len(layer.hints)-1, -1, -1):
					del layer.hints[i]
		elif layer.isMasterLayer and layer.master.id == master_id:
			print("Keeping hints in %s %s" % (glyph.name, layer.name))
