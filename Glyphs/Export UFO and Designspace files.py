# MenuTitle: Export UFO and Designspace files
__doc__ = """
Export UFO and designspace files
"""

import re
import os.path
from fontTools.designspaceLib import (
    DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor)

doc = DesignSpaceDocument()
exporter = NSClassFromString('GlyphsFileFormatUFO').alloc().init()
font = Glyphs.font

for feature in font.features:
    if feature.automatic:
        feature.update()

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
    s.name = "master%s.%s" % (i, master.name.lower().replace(" ", "_"))
    locations = {}

    for x, axis in enumerate(master.axes):
        locations[font.axes[x].name] = axis

    s.location = locations
    doc.addSource(s)

    if not os.path.exists(ufoFolder):
        os.mkdir(ufoFolder)

    exporter.writeUfo_toURL_error_(
        master, NSURL.fileURLWithPath_(ufoFilePath), None)

for i, axis in enumerate(font.axes):
    try:
        axisMap = font.customParameters["Axis Mappings"][axis.axisTag]
    except:
        axisMap = None
    if axisMap is None:
        continue
  
    a = AxisDescriptor()
    axisMin = None
    axisMax = None

    for k in sorted(axisMap.keys()):
        a.map.append((axisMap[k], k))
        if axisMin is None:
            axisMin = axisMap[k]
        if axisMax is None:
            axisMax = axisMap[k]
        if axisMap[k] < axisMin:
            axisMin = axisMap[k]
        if axisMap[k] > axisMax:
            axisMax = axisMap[k]

    a.maximum = axisMax
    a.minimum = axisMin
    a.default = axisMin
    a.name = axis.name
    a.tag = axis.axisTag
    doc.addAxis(a)

for instance in font.instances:
    if not instance.active:
        continue
    ins = InstanceDescriptor()
    m = re.match("^(.*)-(.*)$", instance.fontName)
    postScriptName = m.group(0)
    familyName = m.group(1)
    ins.familyName = instance.familyName
    ins.styleName = m.group(2)
    ins.filename = postScriptName + ".ufo"
    ins.postScriptFontName = postScriptName
    ins.styleMapFamilyName = familyName + m.group(2)
    ins.styleMapStyleName = m.group(2).lower()

    for i, axisValue in enumerate(instance.axes):
        axisName = {}
        axisName[font.axes[i].name] = axisValue
        ins.location = axisName

    doc.addInstance(ins)

designspaceFilePath = ufoFolder + "/" + fontName + ".designspace"
doc.write(designspaceFilePath)
os.system("open %s" % ufoFolder)
