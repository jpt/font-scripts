# MenuTitle: Export UFO and Designspace files
__doc__ = """
Export UFO and designspace files. Supports axis mappings and brace layers.  
"""

import os.path
from re import findall
from fontTools.designspaceLib import (
    DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor)

doc = DesignSpaceDocument()
exporter = NSClassFromString('GlyphsFileFormatUFO').alloc().init()
font = Glyphs.font

# Update auto features 
for feature in font.features:
    if feature.automatic:
        feature.update()

# Add Sources (Masters) to designspace, and export UFOs while we're at it
# Thanks to https://robofont.com/documentation/how-tos/converting-from-glyphs-to-ufo/ for inspiration
for i, master in enumerate(font.masters):
    s = SourceDescriptor()
    exporter.setFontMaster_(master)
    filePath = font.parent.fileURL().path()
    fontName = font.fontName
    fileName = "%s - %s.glyphs" % (font.fontName, master.name)
    folderName = os.path.dirname(filePath)
    ufoFolder = os.path.join(folderName, 'ufo')
    ufoFileName = fileName.replace('.glyphs', '.ufo')
    ufoFilePath = os.path.join(ufoFolder, ufoFileName)
    s.path = ufoFilePath
    s.name = "%s %s" % (fontName, master.name)
    locations = {}
    for x, axis in enumerate(master.axes):
        locations[font.axes[x].name] = axis
    s.location = locations
    doc.addSource(s)

    if not os.path.exists(ufoFolder):
        os.mkdir(ufoFolder)
    exporter.writeUfo_toURL_error_(
        master, NSURL.fileURLWithPath_(ufoFilePath), None)

# Add Glyphs intermediate masters, formerly known as brace layers (these are called support layers in Skateboard)
# todo: add option to generate ufo with separate glyphs
axisMatches = []
for glyph in font.glyphs:
    for layer in glyph.layers:
        if layer.isSpecialLayer:
            for i, axis in enumerate(findall("(\d+)\s*,*", layer.name)):
                masterName = font.masters[layer.associatedMasterId].name
                name = "%s %s %s" % (font.familyName, masterName, layer.name)
                axisName = font.axes[i].name
                supportLayer = dict(name=name, layerName=layer.name,
                                    axisName=axisName, master=masterName, coord=axis)
                if supportLayer not in axisMatches:
                    axisMatches.append(supportLayer)

for i, support in enumerate(axisMatches):
    sp = SourceDescriptor()
    fontName = font.fontName
    fileName = "%s - %s.glyphs" % (fontName, support['master'])
    folderName = os.path.dirname(filePath)
    ufoFolder = os.path.join(folderName, 'ufo')
    ufoFileName = fileName.replace('.glyphs', '.ufo')
    ufoFilePath = os.path.join(ufoFolder, ufoFileName)
    sp.path = ufoFilePath
    location = {}
    location[support['axisName']] = float(support['coord'])
    sp.layerName = support['layerName']
    sp.name = support['name']
    exists = False
    for i, source in enumerate(doc.sources):
        if support['name'] == source.name:
            exists = True
            break
    if exists == True:
        doc.sources[i].location[support['axisName']] = float(support['coord'])
    else:
        sp.location = location
        doc.addSource(sp)

# Add axis maps if defined in Glyphs (Font Info...->Font->Custom Parameters->Axis Mappings)
for i, axis in enumerate(font.axes):
    try:
        axisMap = font.customParameters["Axis Mappings"][axis.axisTag]
    except:
        continue
    a = AxisDescriptor()
    axisMin = None
    axisMax = None
    for k in sorted(axisMap.keys()):
        a.map.append((axisMap[k], k))
        if axisMin is None or axisMap[k] < axisMin:
            axisMin = axisMap[k]
        if axisMax is None or axisMap[k] > axisMax:
            axisMax = axisMap[k]
    a.maximum = axisMax
    a.minimum = axisMin
    a.default = axisMin
    # Could do something like this, but defaults should really be
    # defined by user: question is where
    # if axis.axisTag == "wght" and axisMin < 400 and axisMax > 400:
    #     a.default = 400
    a.name = axis.name
    a.tag = axis.axisTag
    doc.addAxis(a)

# Add instances (now also known as Exports: Font Info...->Exports)
for instance in font.instances:
    if not instance.active:
        continue
    ins = InstanceDescriptor()
    postScriptName = instance.fontName
    if instance.isBold:
        styleMapStyle = "bold"
    elif instance.isItalic:
        styleMapStyle = "italic"
    else:
        styleMapStyle = "regular"
    ins.familyName = instance.preferredFamily
    ins.filename = "%s.ufo" % postScriptName
    ins.postScriptFontName = postScriptName
    ins.styleMapFamilyName = "%s %s" % (ins.familyName, instance.name)
    ins.styleMapStyleName = styleMapStyle
    for i, axisValue in enumerate(instance.axes):
        axisName = {}
        axisName[font.axes[i].name] = axisValue
        ins.location = axisName
    doc.addInstance(ins)

designspaceFilePath = "%s/%s.designspace" % (ufoFolder, fontName)
doc.write(designspaceFilePath)
os.system("open %s" % ufoFolder)
