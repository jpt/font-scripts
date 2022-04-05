# MenuTitle: Add Axis Mappings from Axis Locations
__doc__ = """
Given a font with Axis Location custom parameters on all exporting instances, this script will create axis mappings (avar) for you
"""

def getAxisMappings(F):
	axis_map = dict()
	for instance in F.instances:
		if instance.type == 0:
			for i,internal in enumerate(instance.axes):
				#print(F.customParameters["Axis Mappings"]["wght"])
				external = instance.customParameters["Axis Location"][i]['Location']
				axis_tag = F.axes[i].axisTag
				try:
					axis_map[axis_tag][internal] = external
				except:
					axis_map[axis_tag] = dict()
					axis_map[axis_tag][internal] = external
	return axis_map

F = Glyphs.font
axis_map = getAxisMappings(F)
print(axis_map)
if not F.customParameters["Axis Mappings"]:
	F.customParameters["Axis Mappings"] = dict()
F.customParameters["Axis Mappings"] = axis_map
