#MenuTitle: Find glyphs by regex
# -*- coding: utf-8 -*-
__doc__="""
Opens a new tab with glyphs that match provided regex
"""

import vanilla
import re

Font = Glyphs.font
		
class FindAndOpen( object ):

	def __init__( self ):
		# Window 'self.w':

		margin_x = 20
		margin_y = 16
		button_width = 220
		button_height = 24
		spacer = 6
		input_width = button_width
		input_height = button_height
		window_width  = button_width + margin_x * 2
		window_height = button_height + input_height + (spacer * 2) + (margin_y * 1.5)

		self.w = vanilla.FloatingWindow(
			( window_width, window_height ), # default window size
			"Find glyphs by regex" # window title
		)
		
		xPos = margin_x
		yPos = margin_y
		self.w.RegexField = vanilla.EditText((xPos, yPos, input_width, input_height))
		yPos = yPos + spacer + button_height
		
		self.w.FindButton = vanilla.Button((xPos, yPos, button_width, button_height), "Find", sizeStyle='regular', callback=self.buttonCallback)
		
		self.w.open()

	def buttonCallback( self, sender ):
		pattern = self.w.RegexField.get()
		if pattern != "":
			regex = re.compile('.*' + pattern + '.*')
			matches = ""
			for glyph in Font.glyphs:
				m = re.match(regex, glyph.name)
				if m is not None:
					matches = matches + "/" + glyph.name
			Font.newTab(matches)

FindAndOpen()