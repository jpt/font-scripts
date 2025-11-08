# MenuTitle: Better oblique

# #
#
# NOTE: uncomment and try at your own risk, this script may not work as intended, and will apply actions to entire masters that cannot be undone
#
##

# __doc__ = """
# Set the italic angle of your masters first. Acknowledgements: Jacques Le Bailly and Alexei Vanyashin (method for very_rounds array), Charles Dix (method for rounds array), Thomas Phinney (list of dont_slants), Frederik Berlaen and Lukas Schneider (x_offset math).
# """

# from GlyphsApp import NSAffineTransform 
# from math import radians, tan, pi

# Font = Glyphs.font

# dots_not_rectangles_in_punctuation = True
# dont_slants = "asterisk plus less equal greater asciicircum bar asciitilde trademark copyright logicalnot registered degree plusminus .notdef logicalnotReversed servicemark published estimated leftArrow rightArrow upArrow downArrow lessequal greaterequal approxequal notequal minusplus infinity lozenge integral radical blackSquare upBlackTriangle upWhiteTriangle rightBlackTriangle rightWhiteTriangle downBlackTriangle downWhiteTriangle leftBlackTriangle leftWhiteTriangle fisheye blackDiamond ballotBox ballotBoxWithCheck checkmark upperRightShadowedWhiteSquare".split()
# very_rounds = "B C D G O OE P Q R S Germandbls Schwa ae b c dcroat e g o oe p s germandbls Be-cy Ve-cy Ze-cy Ef-cy Softsign-cy Hardsign-cy Ereversed-cy Iu-cy Yat-cy Obarred-cy be-cy ve-cy ze-cy ef-cy softsign-cy hardsign-cy ereversed-cy iu-cy dje-cy yat-cy obarred-cy ia-cy zero two three five six eight nine at ampersand dollar euro".split()
# rounds = "a J f h jdotless m n r t tbar El-cy Che-cy Tshe-cy Shha-cy de-cy mu che-cy parenleft braceleft".split()

# if dots_not_rectangles_in_punctuation: 
# 	very_rounds.append("periodcentered dotaccentcomb commaturnedabovecomb commaaccentcomb quoteright dotbelowcomb dotaccentcomb dieresiscomb period comma".split())

# very_round_factor = 1.0
# selected_glyphs = []
# master_angles = []
# uniques = []

# for glyph in Font.glyphs:
# 	if(glyph.glyphInfo):
# 		autoAligned = False
# 		autoAlignedComponents = 0
# 		componentCount = 0
# 		for layer in glyph.layers:
# 			if layer.isMasterLayer:
# 				for component in layer.components:
# 					componentCount += 1
# 					if component.automaticAlignment is True:
# 						autoAlignedComponents += 1
# 		if(componentCount > 0 and componentCount == autoAlignedComponents):
# 			autoAligned = True
# 		if autoAligned is False:
# 			uniques.append(glyph)

# x_height = None
# italic_angle = None
# for glyph in uniques:
# 	if glyph.name in dont_slants:
# 		continue
# 	for layer in glyph.layers:
# 		if layer.isMasterLayer:
# 			x_height = layer.master.xHeight
# 			italic_angle = layer.master.italicAngle
# 			if not italic_angle or italic_angle == 0:
# 				print("[ERROR] Italic angle not set for master %s: skipping %s %s." % (layer.master.name, glyph.name, layer.name))
# 				continue
# 			x_shift = -round(tan(italic_angle * pi / 180) * (x_height * 0.5))
# 			t = NSAffineTransform()
# 			if glyph.name not in rounds and glyph.name not in very_rounds:				
# 				t.skew(radians(italic_angle))
# 				layer.transform(t)
# 				layer.applyTransform([1,0,0,1,x_shift,0])
# 			else:
# 				if glyph.name in very_rounds:
# 					italic_angle = italic_angle * very_round_factor
# 					old_pos = layer.bounds.origin
# 					layer.applyTransform([
# 							1.0, # x scale factor
# 							 -radians(italic_angle) * 0.5, # x skew factor
# 							radians(italic_angle), # y skew factor
# 							1.0, # y scale factor
# 							x_shift, # x position
# 							0.0  # y position
# 					])
# 					new_pos = layer.bounds.origin
# 					y_shift = old_pos.y - new_pos.y
# 					layer.applyTransform([1, 0, 0, 1, 0, y_shift])
# 					layer.addNodesAtExtremes()
# 					print("[REMINDER] Remove old extremes on %s %s and manually tweak" % (glyph.name, layer.name))
# 				elif glyph.name in rounds:
# 					t.skew(radians(italic_angle))
# 					t.rotate(italic_angle)
# 					t.rotate(-italic_angle)
# 					layer.transform(t)
# 					layer.applyTransform([1,0,0,1,x_shift,0])
# 					print("[REMINDER] Adjust height of %s %s" % (glyph.name, layer.name))
# 			print ("[SUCCESS] Obliqued %s %s" % (glyph.name, layer.master.name))
# for glyph in uniques:
#     for layer in glyph.layers:
#         if layer.isSpecialLayer and glyph.name not in dont_slants:
#             print("[WARN] Re-interpolating %s %s" % (glyph.name, layer.name))
#             layer.reinterpolate()
