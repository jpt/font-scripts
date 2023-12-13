# MenuTitle: Align brace layers to default master
__doc__ = """Aligns all brace layers to the master associated with the variable font origin, or, if undefined, the first master in the font."""

Font = Glyphs.font
special_layers =  [l for g in Font.glyphs for l in g.layers if l.isSpecialLayer and l.attributes['coordinates']]
master_id = next((p.value for p in Font.customParameters if p.name == "Variable Font Origin"), Font.masters[0].id)
for layer in special_layers:
	layer.associatedMasterId = master_id
