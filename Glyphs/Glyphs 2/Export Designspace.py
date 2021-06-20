#MenuTitle: Export Designspace
# -*- coding: utf-8 -*-

__doc__="""
Exports a Designspace file. Proof of concept stage; currently only supports weight axis. Assumes you do not use special (bracket, brace) layers.
"""

import GlyphsApp, vanilla

class ExportDesignspace( object ):
  def __init__( self ):
    
    windowWidth  = 306
    windowHeight = 460

    self.w = vanilla.FloatingWindow(
      ( windowWidth, windowHeight ), 
      "Export Designspace",
    )

    linePos, inset, lineHeight = 12, 15, 22


    self.w.isVFText = vanilla.TextBox( (inset, linePos, 140, 17), "Interpolation Library:", sizeStyle='small')
    linePos += lineHeight-4

    self.interpolationOptions = [
      {'width':(windowWidth-inset*2)/2-1, 'title':'varLib'},
      {'width':(windowWidth-inset*2)/2-1, 'title':'MutatorMath'},
    ]

    self.w.interpolationRadio = vanilla.SegmentedButton((inset, linePos, windowWidth - inset*2, 17), self.interpolationOptions, callback=self.toggle)

    self.w.interpolationRadio.set(0)

    linePos += lineHeight

    self.w.distributeCheck = vanilla.CheckBox((inset, linePos, -inset, 17), "Transform weight axis from stem width", sizeStyle='small', callback=self.toggle, value=True)

    self.w.distributeCheck.set(1)

    linePos += lineHeight

    self.w.axisMinText = vanilla.TextBox( (inset, linePos+2, 110, 17), "Output axis min:", sizeStyle='small')
    self.w.axisMin = vanilla.EditText( (inset+100, linePos, 46, 20), 0, sizeStyle = 'small', callback=self.toggle)
    
    linePos += lineHeight

    self.w.axisMaxText = vanilla.TextBox( (inset, linePos+2, 110, 17), "Output axis max:", sizeStyle='small')
    self.w.axisMax = vanilla.EditText( (inset+100, linePos, 46, 20), 1000, sizeStyle = 'small',  callback=self.toggle)
    

    linePos += lineHeight

    self.w.cssCheck = vanilla.CheckBox((inset, linePos, -inset, 17), "Map instances to CSS values", sizeStyle='small', callback=self.toggle, value=True)

    self.w.cssCheck.set(1)


    linePos += lineHeight*1.2
 
    self.w.previewText = vanilla.TextBox( (inset, linePos, 140, 17), "Preview:", sizeStyle='small')

    linePos += lineHeight


    template = self.buildTemplate(self.w.interpolationRadio.get(), self.w.distributeCheck.get(), int(self.w.axisMin.get()), int(self.w.axisMax.get()), self.w.cssCheck.get())

    self.w.designSpaceText = vanilla.TextEditor((inset, linePos, -inset, 256), template)

    linePos += 266

    self.w.exportButton = vanilla.Button((inset,linePos, 120, 17), "Export Designspace", sizeStyle='small', callback=self.exportDesignspace)
    self.w.setDefaultButton( self.w.exportButton )


    self.w.open()

  def toggle(self, sender):
    template = self.buildTemplate(self.w.interpolationRadio.get(), self.w.distributeCheck.get(), int(self.w.axisMin.get()), int(self.w.axisMax.get()), self.w.cssCheck.get())
    self.w.designSpaceText.set(template)

  def currentUFOExportPath(self):
    exportPath = Glyphs.defaults["WebfontPluginExportPathManual"]
    if Glyphs.defaults["WebfontPluginUseExportPath"]:
      exportPath = Glyphs.defaults["WebfontPluginExportPath"]
    return exportPath
    
    #
    # This should really export where the UFOs are, but Glyphs.defaults is mostly undocumented... 
    # See https://github.com/mekkablue/Glyphs-Scripts/blob/master/Test/Webfont%20Test%20HTML.py
    # Help, @mekkablue ! :D
    #
    # exportPath = Glyphs.defaults["UFOExportPathManual"]
    # if Glyphs.defaults["UFOPluginUseExportPath"]:
    #   exportPath = Glyphs.defaults["UFOExportPath"]
    # return exportPath

  def exportDesignspace(self, sender):
    firstDoc = Glyphs.orderedDocuments()[0]
    if firstDoc.isKindOfClass_(GSProjectDocument):
      exportPath = firstDoc.exportPath()
    else:
      thisFont = Glyphs.font # frontmost font
      exportPath = self.currentUFOExportPath()
    content = self.w.designSpaceText.get()
    fileName = Glyphs.font.familyName + '.designspace'
    saveFileLocation = "%s/%s" % (exportPath,fileName)
    saveFileLocation = saveFileLocation.replace( "//", "/" )
    f = open( saveFileLocation, 'w' )
    print "Exporting to:", f.name
    f.write( content )
    f.close()
    return True


  def affine(self,a,b,c,d,x): # minInput, maxInput, minOutput, maxOutput, x -- see https://math.stackexchange.com/q/377169
    return (x-a)*((d-c)/(b-a))+c

  def findMiddle(self,inputList):
      middle = float(len(inputList))/2
      if middle % 2 != 0:
          return inputList[int(middle - .5)]
      else:
          return (inputList[int(middle)], inputList[int(middle-1)])

  def buildTemplate(self, lib, distribute, minOutput, maxOutput, css):

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
    gfCSS = {
      "Thin": 250,
      "ExtraLight": 275,
      "UltraLight": 275,
      "Light": 300,
      "Regular": 400, 
      "Medium": 500,
      "SemiBold": 600,
      "DemiBold": 600,
      "Bold": 700,
      "ExtraBold": 800,
      "UltraBold": 800,
      "Black": 900,
      "Heavy": 900
    }

    if lib == 0:
      mathModel = 'previewVarLib'
    else:
      mathModel = 'previewMutatorMath'

    for master in font.masters:
       masterValInputs.append(master.axes[0])

    masterMin = min(masterValInputs)
    masterMax = max(masterValInputs)

    for instance in font.instances:
       instanceValInputs.append(instance.weightValue)

    if distribute:
      minWeightOutput = minOutput
      maxWeightOutput = maxOutput
    else:
      minWeightOutput = masterMin
      maxWeightOutput = masterMax


    if distribute:
      for masterVal in masterValInputs:
           i = self.affine(masterMin, masterMax, minWeightOutput, maxWeightOutput, masterVal)
           masterValOutputs.append(i)
    else:
      masterValOutputs = masterValInputs


    default = self.findMiddle(masterValOutputs)


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

    if distribute:
      for instanceVal in instanceValInputs:
        i = self.affine(minWeightInput, maxWeightInput, minWeightOutput, maxWeightOutput, instanceVal)
        instanceValOutputs.append(i)
    else:
        instanceValOutputs = instanceValInputs

    if self.w.cssCheck.get():
      maps = "\n"
      for i, instance in enumerate(font.instances):
        mapVals = {
          'inputVal': gfCSS[instance.weight],
          'output': instanceValOutputs[i],
        }
        maps += "      <map input=\"{inputVal}\" output=\"{output}\" />\n".format(**mapVals)


    for i, instance in enumerate(font.instances):
        instanceVals = {
            'styleName': instance.name,
            'fileName': 'instances/' + familyName + '-' + instance.name + '.ufo',
            'xValue': instanceValOutputs[i],
            'familyName': familyName,
            'postScriptFontName': familyName.replace(" ", "") + '-' + instance.name.replace(" ", "")
        }

        instances += "    <instance familyname=\"{familyName}\" postscriptfontname=\"{postScriptFontName}\" stylename=\"{styleName}\" filename=\"{fileName}\">\n      <location>\n        <dimension name=\"weight\" xvalue=\"{xValue}\"/>\n      </location>\n    </instance>\n".format(**instanceVals)
        

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
      <labelname xml:lang="en">Weight</labelname>{maps}
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