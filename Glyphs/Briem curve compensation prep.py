
# MenuTitle: Briem curve compensation prep
__doc__ = """
For selected layer, slants, rotates, shifts baseline, and adds two layers necessary for performing curve compensation. Set your master's italic angle and x-height first. TODO: automate it all.
"""

from GlyphsApp import NSAffineTransform 
from math import radians, tan, pi

def main():
    font = Glyphs.font
    selectedGlyph = font.selectedLayers[0].parent.name
    xHeight = None
    angle = None
    for master in font.masters:
        if master.id == font.selectedLayers[0].associatedMasterId:
            xHeight = master.xHeight
            angle = master.italicAngle
            break

    if xHeight is None:
        print("Set an x-height for this master.")
        return
    if angle is None:
        print("Set an italic angle for this master before running the script.")
        return
    if selectedGlyph is None:
        print("Select a glyph in the editor or font menu.")
        return
    
    slantedLayer = font.selectedLayers[0].copy()
    slantedLayer.name = font.selectedLayers[0].name + " Slanted"
    
    offset = -round(tan(angle * pi / 180) * (xHeight * 0.5)) # see https://robofont.com/documentation/how-tos/working-with-italic-slant/#setting-the-italic-slant-offset
    font.glyphs[selectedGlyph].layers.append(slantedLayer)
    
    for path in slantedLayer.paths:
        path.applyTransform([1,0,radians(angle),1,offset,0])
        path.addNodesAtExtremes()
    print(selectedGlyph)
    slantedRotatedLayer = font.selectedLayers[0].copy()
    slantedRotatedLayer.name = font.selectedLayers[0].name + " Slanted and Rotated"
    offset = -round(tan((angle/2) * pi / 180) * (xHeight * 0.5)) #
    for path in slantedRotatedLayer.paths:
        path.applyTransform([1,0,radians(angle/2),1,offset,0])
        
    t = NSAffineTransform()
    print(font.selectedLayers[0].bounds)
    t.rotate(-(angle/2),(font.selectedLayers[0].bounds.size.width/2,font.selectedLayers[0].bounds.size.height/2))
    for path in slantedRotatedLayer.paths:
        path.addNodesAtExtremes()
    slantedRotatedLayer.transform(t)
    font.glyphs[selectedGlyph].layers.append(slantedRotatedLayer)
main()