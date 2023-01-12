# MenuTitle: Zero out blueFuzz for instances at master coordinates

__doc__ = """
Zero out blueFuzz for instances at master coordinates
"""

def main():
	font = Glyphs.font
	master_axes = [master.axes for master in font.masters]
	for instance in font.instances:
		if(instance.active and instance.axes in master_axes and instance.customParameters['blueFuzz'] != 0):
			print(f"Zeroing {instance.fullName}")
			instance.customParameters['blueFuzz'] = 0
main()
