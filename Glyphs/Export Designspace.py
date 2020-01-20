#MenuTitle: Export Designspace
# -*- coding: utf-8 -*-

__doc__="""
Exports a Designspace file. Proof of concept stage; currently only supports weight axis; mapping may be weird too. Assumes you do not use special layers.
"""

from Foundation import *
from AppKit import *
import GlyphsApp, vanilla, os


class ExportDesignspace( object ):
  def __init__( self ):
    
    windowWidth  = 306
    windowHeight = 382

    self.w = vanilla.FloatingWindow(
      ( windowWidth, windowHeight ), 
      "Export Designspace",
    )

    linePos, inset, lineHeight = 12, 15, 22


    self.w.isVFText = vanilla.TextBox( (inset, linePos, 140, 17), "Interpolation Library:", sizeStyle='small')
    linePos += lineHeight

    self.interpolationOptions = [
      {'width':(windowWidth-inset*2)/2-1, 'title':'varLib'},
      {'width':(windowWidth-inset*2)/2-1, 'title':'MutatorMath'},
    ]

    self.w.interpolationRadio = vanilla.SegmentedButton((inset, linePos, windowWidth - inset*2, 17), self.interpolationOptions, callback=self.setLib)

    self.w.interpolationRadio.set(0)

    linePos += lineHeight*1.2
 
    self.w.previewText = vanilla.TextBox( (inset, linePos, 140, 17), "Preview:", sizeStyle='small')

    linePos += lineHeight


    template = self.buildTemplate(self.w.interpolationRadio.get())
    
    self.w.designSpaceText = vanilla.TextEditor((inset, linePos, -inset, 256), template)

    linePos += 256 + 12

    self.w.exportButton = vanilla.Button((inset,linePos, 120, 17), "Export Designspace", sizeStyle='small', callback=self.exportDesignspace)
    self.w.setDefaultButton( self.w.exportButton )


    self.w.open()

  def setLib(self, sender):
    template = self.buildTemplate(self.w.interpolationRadio.get())
    self.w.designSpaceText.set(template)


  def exportDesignspace(self, sender):
    firstDoc = Glyphs.orderedDocuments()[0]
    if firstDoc.isKindOfClass_(GSProjectDocument):
      exportPath = firstDoc.exportPath()
    else:
      thisFont = Glyphs.font # frontmost font
      exportPath = currentWebExportPath()
    content = self.w.designSpaceText.get()
    fileName = Glyphs.font.familyName + '.designspace'
    saveFileLocation = "%s/%s" % (exportPath,fileName)
    saveFileLocation = saveFileLocation.replace( "//", "/" )
    f = open( saveFileLocation, 'w' )
    print "Exporting to:", f.name
    f.write( content )
    f.close()
    return True

  def currentWebExportPath():
    exportPath = Glyphs.defaults["DesignspaceExportPathManual"]
    if Glyphs.defaults["DesignspaceExportPath"]:
      exportPath = Glyphs.defaults["DesignspaceExportPath"]


  def affine(a,b,c,d,x): # minInput, maxInput, minOutput, maxOutput, x -- see https://math.stackexchange.com/q/377169
    return (x-a)*((d-c)/(b-a))+c

  def findMiddle(inputList):
      middle = float(len(inputList))/2
      if middle % 2 != 0:
          return inputList[int(middle - .5)]
      else:
          return (inputList[int(middle)], inputList[int(middle-1)])

  def buildTemplate(self, vf):

    if vf == 0:
      vf = 1
    else:
      vf = 0

    font = Glyphs.font
    inputVal = 100.0
    maps = ''
    sources = ''
    instances = ''
    familyName = font.familyName
    masterValInputs = []
    masterValOutputs = []
    instanceValInputs = []
    instanceValOutputs = []

    if vf:
      mathModel = 'previewVarLib'
    else:
      mathModel = 'previewMutatorMath'

    for master in font.masters:
       masterValInputs.append(master.axes[0])

    masterMin = min(masterValInputs)
    masterMax = max(masterValInputs)

    for instance in font.instances:
       instanceValInputs.append(instance.weightValue)

    if vf:
      minWeightOutput = 0
      maxWeightOutput = 1000
    else:
      minWeightOutput = masterMin
      maxWeightOutput = masterMax


    if vf:
      for masterVal in masterValInputs:
           i = affine(masterMin, masterMax, minWeightOutput, maxWeightOutput, masterVal)
           masterValOutputs.append(i)
    else:
      masterValOutputs = masterValInputs


    default = findMiddle(masterValOutputs)


    for i, master in enumerate(font.masters):

        sourceVals = {
            'familyName': familyName,
            'masterName': familyName + '-' +  master.name + '.ufo',
            'styleName': master.name,
            'xValue': masterValOutputs[i],
            'i': i
        }

        sources += "    <source familyname=\"{familyName}\" filename=\"{masterName}\" stylename=\"{styleName}\" name=\"master_{i}\">\n      <location>\n        <dimension name=\"weight\" xvalue=\"{xValue}\"/>\n      </location>\n    </source>\n".format(**sourceVals)

    minWeightInput = min(masterValInputs)
    maxWeightInput = max(masterValInputs)

    if vf:
      for instanceVal in instanceValInputs:
        i = affine(minWeightInput, maxWeightInput, minWeightOutput, maxWeightOutput, instanceVal)
        instanceValOutputs.append(i)
    else:
        instanceValOutputs = instanceValInputs

    for i, instance in enumerate(font.instances):

        mapVals = {
            'inputVal': inputVal,
            'output': instanceValOutputs[i],
        }
        instanceVals = {
            'styleName': instance.name,
            'fileName': 'instances/' + familyName + '-' + instance.name + '.ufo',
            'xValue': instanceValOutputs[i],
            'familyName': familyName,
            'postScriptFontName': familyName.replace(" ", "") + '-' + instance.name.replace(" ", "")
        }

        maps += "      <map input=\"{inputVal}\" output=\"{output}\" />\n".format(**mapVals)
        instances += "    <instance familyname=\"{familyName}\" postscriptfontname=\"{postScriptFontName}\" stylename=\"{styleName}\" filename=\"{fileName}\">\n      <location>\n        <dimension name=\"weight\" xvalue=\"{xValue}\"/>\n      </location>\n    </instance>\n".format(**instanceVals)
        inputVal += 100


    templateVals = {
        'sources': sources.rstrip(),
        'maps': maps.rstrip(),
        'instances': instances.rstrip(),
        'minWeightOutput': minWeightOutput,
        'maxWeightOutput': maxWeightOutput,
        'mathModel': mathModel,
        'default': default
    }
    template = """<?xml version='1.0' encoding='UTF-8'?>
  <designspace format="3">
    <axes>
      <axis tag="wght" name="weight" minimum="{minWeightOutput}" maximum="{maxWeightOutput}" default="{default}">
        <labelname xml:lang="en">Weight</labelname>
  {maps}
      </axis>
    </axes>
    <sources>
  {sources}
    </sources>
    <instances>
  {instances}
    </instances>
    <lib>
      <dict>
        <key>com.letterror.mathModelPref</key>
        <string>{mathModel}</string>
      </dict>
    </lib>
  </designspace>"""

    template = template.format(**templateVals)
    return template

ExportDesignspace()