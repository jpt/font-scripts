#MenuTitle: Update horizontal metrics
# -*- coding: utf-8 -*-

__doc__="""
Updates horizontal metrics (sidebearings). Re-interpolates special layer sidebearings and syncs all metric keys.
"""

font = Glyphs.font

for glyph in font.glyphs:
	for layer in glyph.layers:
		if layer.isSpecialLayer:
			layer.reinterpolateMetrics()
		layer.syncMetrics()
# have to sync twice, presumably to account for reversals e.g. =|n
for glyph in font.glyphs:
	for layer in glyph.layers:
		layer.syncMetrics()