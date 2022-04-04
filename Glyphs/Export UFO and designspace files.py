# MenuTitle: Export UFO and designspace files
__doc__ = """
Exports UFO and designspace files. Supports substitutions defined in OT features, but not bracket layers. Brace layers supported, but not yet as support layers for Skateboard. With contributions from Rafał Buchner. Thanks to Frederik Berlaen and Joancarles Casasín for ideas that served as inspiration (https://robofont.com/documentation/how-tos/converting-from-glyphs-to-ufo/), and to the maintainers of designspaceLib.
"""

from GlyphsApp import GSInstance
import re
import os
import tempfile
import shutil
from plistlib import FMT_XML, load, dump
from AppKit import NSClassFromString, NSURL
from fontTools.designspaceLib import (
    DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor, RuleDescriptor)
import glob
import subprocess


#### Edit this as you wish. Will eventually be vanilla UI

to_build = {
    "variable": True,
    "static": True,
}

delete_unnecessary_glyphs = True # Set to False if you want brace layers to be full masters and not just affected glyphs
use_production_names = False # Set to true for production unicode glyph names — warning, this probably will mess up feature code. Just let fontmake rename your glyphs.
decompose_smart_stuff = True # Not sure what happens if this is set to False. Good luck! :D
add_mastername_as_stylename = True # Needed for ScaleFast and potentially other Robofont plugins
add_build_script = True # adds a minimal build script to the output dir

# if you want
to_decompose = "Dzhe-cy Geupturn-cy dzhe-cy geupturn-cy tse-cy dhe-cy tetse-cy Tse-cy Dhe-cy Tetse-cy upArrow.small Ohorntilde ohorntilde rightArrow.small downArrow.small leftArrow.small upArrow.smallWhite rightArrow.smallWhite downArrow.smallWhite leftArrow.smallWhite A.small B.small C.small D.small E.small F.small G.small H.small I.small J.small K.small L.small M.small N.small O.small P.small Q.small R.small R.small.ss03 S.small T.small U.small V.small W.small X.small Y.small Z.small A.smallWhite B.smallWhite C.smallWhite D.smallWhite E.smallWhite F.smallWhite G.smallWhite H.smallWhite I.smallWhite J.smallWhite K.smallWhite L.smallWhite M.smallWhite N.smallWhite O.smallWhite P.smallWhite Q.smallWhite R.smallWhite R.smallWhite.ss03 S.smallWhite T.smallWhite U.smallWhite V.smallWhite W.smallWhite X.smallWhite Y.smallWhite Z.smallWhite zero.smallWhite one.smallWhite two.smallWhite three.smallWhite four.smallWhite five.smallWhite six.smallWhite seven.smallWhite eight.smallWhite nine.smallWhite six.smallWhite.ss06 nine.smallWhite.ss06 upArrow.smallWhite rightArrow.smallWhite downArrow.smallWhite leftArrow.smallWhite zero.dnom one.dnom two.dnom three.dnom four.dnom five.dnom six.dnom six.dnom.ss06 seven.dnom eight.dnom nine.dnom nine.dnom.sso6 six.sinf.ss06 nine.sinf.ss06 period, colon semicolon ellipsis exclam exclamdown question questiondown periodcentered bullet asterisk numbersign slash backslash periodcentered.case periodcentered.loclCAT period.ss10 comma.ss10 colon.ss10 semicolon.ss10 ellipsis.ss10 exclam.ss10 exclamdown.ss10 question.ss10 questiondown.ss10 periodcentered.ss10 bullet.ss10 periodcentered.loclCAT.case periodcentered.case.ss10 periodcentered.loclCAT.ss10 periodcentered.loclCAT.case.ss10  hyphen endash emdash hyphentwo underscore parenleft parenright braceleft braceright bracketleft bracketright quotesinglbase quotedblbase quotedblleft quotedblright quoteleft quoteright quotedbl quotesingle quotesinglbase.ss10 quotedblbase.ss10 quotedblleft.ss10 quotedblright.ss10 quoteleft.ss10 quoteright.ss10 brevecomb_acutecomb brevecomb_gravecomb brevecomb_hookabovecomb brevecomb_tildecomb circumflexcomb_acutecomb circumflexcomb_gravecomb circumflexcomb_hookabovecomb circumflexcomb_tildecomb brevecomb-cy ̈̇̀́̋ caroncomb.alt circumflexcomb caroncomb brevecomb ringcomb tildecomb macroncomb hookabovecomb candraBinducomb commaturnedabovecomb dotbelowcomb dieresisbelowcomb ringbelowcomb commaaccentcomb cedillacomb ogonekcomb brevebelowcomb macronbelowcomb strokeshortcomb strokelongcomb doublemacronbelowcomb dieresis dotaccent grave acute hungarumlaut circumflex caron breve ring tilde macron strokeshortcomb.case  caroncomb.alt.loclCSYSKY gravecomb.loclVIT acutecomb.loclVIT circumflexcomb.loclVIT brevecomb.loclVIT tildecomb.loclVIT dieresiscomb.ss10 dieresiscomb.case dieresiscomb.ss10.case dotaccentcomb.ss10 candraBinducomb.ss10 commaturnedabovecomb.ss10 dotbelowcomb.ss10 commaaccentcomb.ss10 exclamdotless ligstrokecomb lowerhookcomb ordcomb questiondotless spike-cy spikebar-cy spikecenter-cy spikedescender-cy tittle lowerhookcomb.case shortstrokecomb.case spike-cy.case spikebar-cy.case spikecenter-cy.case spikedescender-cy.case daggerdbl daggerdbl.sup currency leftRightArrow upDownArrow reversecommamod reversecommamod.ss10 apostrophemod commareversedmod commaturnedmod primemod commareversedmod.ss10 commaturnedmod.ss10 ringhalfleft  dieresiscomb.case dotaccentcomb.case gravecomb.case acutecomb.case hungarumlautcomb.case caroncomb.alt.case circumflexcomb.case circumflexcomb_gravecomb.case circumflexcomb_acutecomb.case circumflexcomb_tildecomb.case circumflexcomb_hookabovecomb.case caroncomb.case brevecomb.case brevecomb_gravecomb.case brevecomb_acutecomb.case brevecomb_tildecomb.case brevecomb_hookabovecomb.case ringcomb.case tildecomb.case macroncomb.case hookabovecomb.case commaturnedabovecomb.case  dotbelowcomb.case dieresisbelowcomb.case ringbelowcomb.case commaaccentcomb.case cedillacomb.case ogonekcomb.case brevebelowcomb.case macronbelowcomb.case strokeshortcomb.case slashlongcomb.case doublemacronbelowcomb.case ogonekcomb.flat.case caroncomb.alt.loclCSYSKY.case dieresiscomb.loclUKR.case gravecomb.loclVIT.case acutecomb.loclVIT.case circumflexcomb.loclVIT.case brevecomb.loclVIT.case tildecomb.loclVIT.case macroncomb.narrow.case dieresiscomb.ss10.case dotaccentcomb.ss10.case dotaccentcomb.case.loclVIT dieresiscomb.ss10.loclUKR.case dieresiscomb.loclUKR.narrow.case tildecomb.loclVIT.case.left dotaccentcomb.ss10.case.loclVIT upArrow.circled rightArrow.circled downArrow.circled leftArrow.circled upArrow.blackCircled rightArrow.blackCircled downArrow.blackCircled leftArrow.blackCircled   brevecomb_acutecomb  brevecomb_gravecomb  brevecomb_hookabovecomb  brevecomb_tildecomb  circumflexcomb_acutecomb  circumflexcomb_gravecomb  circumflexcomb_hookabovecomb  circumflexcomb_tildecomb  circumflexcomb_gravecomb.case  circumflexcomb_acutecomb.case  circumflexcomb_tildecomb.case  circumflexcomb_hookabovecomb.case  brevecomb_gravecomb.case  brevecomb_acutecomb.case  brevecomb_tildecomb.case  brevecomb_hookabovecomb.case".split(" ")
to_remove_overlap = "upArrow.small rightArrow.small downArrow.small leftArrow.small A.smallWhite B.smallWhite C.smallWhite D.smallWhite E.smallWhite F.smallWhite G.smallWhite H.smallWhite I.smallWhite J.smallWhite K.smallWhite L.smallWhite M.smallWhite N.smallWhite O.smallWhite P.smallWhite Q.smallWhite R.smallWhite R.smallWhite.ss03 S.smallWhite T.smallWhite U.smallWhite V.smallWhite W.smallWhite X.smallWhite Y.smallWhite Z.smallWhite zero.smallWhite one.smallWhite two.smallWhite three.smallWhite four.smallWhite five.smallWhite six.smallWhite seven.smallWhite eight.smallWhite nine.smallWhite six.smallWhite.ss06 nine.smallWhite.ss06 upArrow.smallWhite rightArrow.smallWhite downArrow.smallWhite leftArrow.smallWhite leftArrow.blackCircled rightArrow.blackCircled upArrow.blackCircled downArrow.blackCircled".split(" ")

### Careful editing beyond here! 

def addBuildScript(font,dest):
    __doc__ = """Provided a font, destination and font name, creates a build script for the project"""
    global add_build_script
    if not add_build_script:
        return
    static_font_name = getFamilyName(font,"static").replace(" ", "\ ")
    vf_font_name = getFamilyName(font,"variable").replace(" ", "\ ")
    build_script = f"""#!/bin/bash
python3 -m fontmake -m ../{vf_font_name}.designspace -o variable --output-dir ../build/vf
python3 -m fontmake -i -m ../{static_font_name}.designspace -o ttf --output-dir ../build/ttf
python3 -m fontmake -i -m ../{static_font_name}.designspace -o otf --output-dir ../build/otf
"""
    make_woff_script ="""#!/bin/bash"
woff2_compress ../build/vf/*.ttf
woff2_compress ../build/ttf/*.ttf
mkdir ../build/woff
mv ../build/vf/*.woff2 ../build/woff
mv ../build/ttf/*.woff2 ../build/woff
"""
    def makeScript(script,type):
        script_name =  os.path.join(dest,type + ".sh")
        f = open(script_name, "w")
        f.write(script)
        f.close()
        subprocess.run(["chmod","+x",script_name])
    makeScript(build_script, "build")
    makeScript(make_woff_script, "woff")

def decomposeGlyphs(font):
    __doc__ = """Provided a font object, decomposes glyphs defined in to_decompose"""
    global to_decompose
    for glyph in to_decompose:
        if font.glyphs[glyph]:
            for layer in font.glyphs[glyph].layers:
                if len(layer.components) > 0:
                    if layer.isMasterLayer or layer.isSpecialLayer:
                        layer.decomposeComponents()


def removeOverlaps(font):
    __doc__ = """Provided a font object, removes overlaps in glyphs defined in to_remove_overlap"""
    global to_remove_overlap
    for glyph in to_remove_overlap:
        if font.glyphs[glyph]:
            for layer in font.glyphs[glyph].layers:
                if layer.isMasterLayer or layer.isSpecialLayer:
                    layer.removeOverlap()


def getMutedGlyphs(font):
    __doc__ = "Provided a font object, returns an array of non-exporting glyphs to be added as muted glyphs in the designspace"
    return [glyph.name for glyph in font.glyphs if not glyph.export]


def getBoundsByTag(font, tag):
    __doc__ = """Provided a font object and an axis tag, returns an array in the form of [minimum, maximum] representing the bounds of an axis. 

Example use: 
min, max = getBoundsByTag(Glyphs.font,"wght")"""
    min = None
    max = None
    for i, axis in enumerate(font.axes):
        if axis.axisTag != tag:
            continue
        for master in font.masters:
            coord = master.axes[i]
            if min == None or coord < min:
                min = coord
            if max == None or coord > max:
                max = coord
    return [min, max]


def getOriginMaster(font):
    __doc__ = """Provided a font object, returns a string of the master ID referencing the master that is set to the variable font origin by custom paramter"""
    master_id = None
    for parameter in font.customParameters:
        if parameter.name == "Variable Font Origin":
            master_id = parameter.value
    if master_id is None:
        return font.masters[0].id
    return master_id


def getOriginCoords(font):
    __doc__ = """Provided a font object, returns an array of axis coordinates specified on the variable font origin master."""
    for parameter in font.customParameters:
        if parameter.name == "Variable Font Origin":
            master_id = parameter.value
    if master_id is None:
        master_id = font.masters[0].id
    for master in font.masters:
        if master.id == master_id:
            return list(master.axes)


def getAxisNameByTag(font, tag):
    __doc__ = """Provided a font object an axis tag, returns an axis name"""
    for axis in font.axes:
        if axis.axisTag == tag:
            return axis.name


def hasVariableFamilyName(font):
    __doc__ = """Provided a font object, returns a boolean as to whether or not the font has a different VF name"""
    for instance in font.instances:
        if instance.type == 1:
            return True

def getVariableFontFamily(font):
    __doc__ = """Provided a font object, returns the name associated with a Variable Font Setting export"""
    for instance in font.instances:
        if instance.type == 1:
            return font.familyName + " " + instance.name
    return font.familyName


def getFamilyName(font, format):
    __doc__ = """Provided a font object, returns a font family name"""
    if format == "variable":
        family_name = getVariableFontFamily(font)
    else:
        family_name = font.familyName
    return family_name


def getFamilyNameWithMaster(font, master, format):
    __doc__ = """Provided a font object and a master, returns a font family name"""
    master_name = master.name
    if hasVariableFamilyName(font):
        if format == "static":
            font_name = "%s - %s" % (font.familyName, master_name)
        else:
            font_name = "%s - %s" % (getVariableFontFamily(font), master_name)
    else:
         font_name = "%s - %s" % (font.familyName, master_name)

    return font_name


def getStyleNameWithAxis(font, axes):
    style_name = ""
    for i, axis in enumerate(axes):
        style_name = "%s %s %s" % (style_name, font.axes[i].name, axis)
    return style_name.strip()


def getNameWithAxis(font, axes, format):
    __doc__ = """Provided a font and a dict of axes for a brace layer, returns a font family name"""
    if format =="static":
        font_name = "%s -" % (font.familyName)
    else:
        font_name = "%s -" % (getVariableFontFamily(font))
    for i, axis in enumerate(axes):
        font_name = "%s %s %s" % (font_name, font.axes[i].name, axis)
    return font_name


def alignSpecialLayers(font):
    __doc__ = """Applies the same master ID referencing the variable font origin to all brace layers"""
    master_id = getOriginMaster(font)
    special_layers = getSpecialLayers(font)
    for layer in special_layers:
        layer.associatedMasterId = master_id


def getSources(font,format):
    __doc__ = """Provided a font object, creates and returns a list of designspaceLib SourceDescriptors"""
    sources = []
    for i, master in enumerate(font.masters):
        s = SourceDescriptor()
        if hasVariableFamilyName(font):
            font_name = getFamilyNameWithMaster(font, master,format)
        else:
            font_name = getFamilyNameWithMaster(font, master,"static")
        s.filename = "masters/%s.ufo" % font_name
        s.familyName = getFamilyName(font,format)
        s.styleName = master.name
        locations = dict()
        for x, axis in enumerate(master.axes):
            locations[font.axes[x].name] = axis
        s.location = locations
        origin_master_id = getOriginMaster(font)
        if master.id == origin_master_id:
            s.copyLib = True
            s.copyFeatures = True
            s.copyGroups = True
            s.copyInfo = True
        s.mutedGlyphNames = getMutedGlyphs(font)
        sources.append(s)
    return sources


def addSources(doc, sources):
    __doc__ = """Provided a designspace document and array of source descriptors, adds those sources to the designspace doc."""
    for source in sources:
        doc.addSource(source)


def getSpecialLayers(font):
    __doc__ = """Provided a font object, returns a list of GSLayers that are brace layers (have intermediate master coordinates)."""

    return [l for g in font.glyphs for l in g.layers if l.isSpecialLayer and l.attributes['coordinates']]


def getSpecialLayerAxes(font):
    __doc__ = """Provided a font object, returns a list of dicts containing name and coordinate information for each axis"""
    special_layer_axes = []
    layers = getSpecialLayers(font)
    for layer in layers:
        layer_axes = dict()
        for i, coords in enumerate(layer.attributes['coordinates']):
            layer_axes[font.axes[i].name] = int(
                layer.attributes['coordinates'][coords])
        if layer_axes not in special_layer_axes:
            special_layer_axes.append(layer_axes)
    return special_layer_axes


def getNonSpecialGlyphs(font, axes):
    __doc__ = """Provided a font and a list of axis coordinates, returns all glyphs without those coordinates"""
    glyph_names_to_delete = []
    for glyph in font.glyphs:
        delete_glyph = True
        for layer in glyph.layers:
            if layer.isSpecialLayer and layer.attributes['coordinates']:
                coords = list(
                    map(int, layer.attributes['coordinates'].values()))
                if coords == axes:
                    delete_glyph = False
        if delete_glyph:
            if glyph.name not in glyph_names_to_delete:
                glyph_names_to_delete.append(glyph.name)
    return glyph_names_to_delete


def getSpecialSources(font,format):
    __doc__ = """Provided a font object, returns an array of designspaceLib SourceDescriptors """

    sources = []
    special_layer_axes = getSpecialLayerAxes(font)
    for i, special_layer_axis in enumerate(special_layer_axes):
        axes = list(special_layer_axis.values())
        s = SourceDescriptor()
        s.location = special_layer_axis
        font_name = getNameWithAxis(font, axes, format)
        s.filename = "masters/%s.ufo" % font_name
        sources.append(s)
    return sources


def addAxes(doc, font):
    __doc__ = """Provided a designspace doc and a font object, adds axes from that font to the designspace as AxisDescriptors"""
    for i, axis in enumerate(font.axes):
        try:
            axis_map = font.customParameters["Axis Mappings"][axis.axisTag]
        except:
            continue
        a = AxisDescriptor()
        axis_min, axis_max = getBoundsByTag(font, axis.axisTag)

        for k in sorted(axis_map.keys()):
            a.map.append((axis_map[k], k))
        try:
            a.maximum = axis_map[axis_max]
            a.minimum = axis_map[axis_min]
        except:
            print("Error: the font's axis mappings don't match its real min/max coords")
        origin_coord = getOriginCoords(font)[i]
        user_origin = axis_map[origin_coord]
        a.default = user_origin
        a.name = axis.name
        a.tag = axis.axisTag

        doc.addAxis(a)


def getConditionsFromOT(font):
    __doc__ = """Provided a font object, returns two arrays: one a list of OT substitution conditions, and one of the glyph replacements to make given those conditions. Each array has the same index.
	
Example use:
condition_list, replacement_list = getConditionsFromOT(font)
"""
    feature_code = ""
    for feature_itr in font.features:
        for line in feature_itr.code.splitlines():
            if line.startswith("condition "):
                feature_code = feature_itr.code
    condition_index = 0
    condition_list = []
    replacement_list = [[]]
    for line in feature_code.splitlines():
        if line.startswith("condition"):
            conditions = []
            conditions_list = line.split(",")
            for condition in conditions_list:
                m = re.findall("< (\w{4})", condition)
                tag = m[0]
                axis_name = getAxisNameByTag(font, tag)
                m = re.findall("\d+(?:\.|)\d*", condition)
                cond_min = float(m[0])
                if len(m) > 1:
                    cond_max = float(m[1])
                    range_dict = dict(
                        name=axis_name, minimum=cond_min, maximum=cond_max)
                else:
                    _, cond_max = getBoundsByTag(font, tag)
                    range_dict = dict(
                        name=axis_name, minimum=cond_min, maximum=cond_max)
                conditions.append(range_dict)
            condition_list.append(conditions)
            condition_index = condition_index + 1
        elif line.startswith("sub"):
            m = re.findall("sub (.*) by (.*);", line)[0]
            replace = (m[0], m[1])
            try:
                replacement_list[condition_index-1].append(replace)
            except:
                replacement_list.append(list())
                replacement_list[condition_index-1].append(replace)
    return [condition_list, replacement_list]


def removeSubsFromOT(font):
    __doc__ = """Provided a font object, removes subsitutions in feature code"""
    feature_index = None
    for i, feature_itr in enumerate(font.features):
        for line in feature_itr.code.splitlines():
            if line.startswith("condition "):
                feature_index = i
                break
    if(feature_index):
        font.features[feature_index].code = re.sub(
            r'#ifdef VARIABLE.*?#endif', '', font.features[feature_index].code, flags=re.DOTALL)


def applyConditionsToRules(doc, condition_list, replacement_list):
    __doc__ = """Provided a designspace document, condition list, and replacement list (as provided by getConditionsFromOT), adds matching designspace RuleDescriptors to the doc"""
    rules = []
    for i, condition in enumerate(condition_list):
        r = RuleDescriptor()
        r.name = "Rule %s" % str(i+1)
        r.conditionSets.append(condition)
        for sub in replacement_list[i]:
            r.subs.append(sub)
        rules.append(r)
    doc.rules = rules


def getInstances(font,format):
    __doc__ = """Provided a font object, returns a list of designspaceLib InstanceDescriptors"""
    instances_to_return = []
    for instance in font.instances:
        if not instance.active:
            continue
        if not instance.familyName:  # skip Variable Font Setting, which is an instance
            continue
        ins = InstanceDescriptor()
        postScriptName = instance.fontName
        if instance.isBold:
            style_map_style = "bold"
        elif instance.isItalic:
            style_map_style = "italic"
        else:
            style_map_style = "regular"
        if format=="variable":
            family_name = getVariableFontFamily(font)
        else:
            if instance.preferredFamily:
                family_name = instance.preferredFamily
            else:
                family_name = font.familyName
        ins.familyName = family_name
        if format=="variable":
            style_name = instance.variableStyleName
        else:
            style_name = instance.name
        ins.styleName = style_name
        ins.filename = "instances/%s.ufo" % postScriptName
        ins.postScriptFontName = postScriptName
        ins.styleMapFamilyName = instance.preferredFamily
        ins.styleMapStyleName = style_map_style
        axis_name = {}
        for i, axis_value in enumerate(instance.axes):
            axis_name[font.axes[i].name] = axis_value
        ins.location = axis_name
        instances_to_return.append(ins)
    return instances_to_return


def addInstances(doc, instances):
    __doc__ = """Provided a doc and list of designspace InstanceDescriptors, adds them to the doc"""
    for instance in instances:
        doc.addInstance(instance)


def updateFeatures(font):
    __doc__ = """Provided a font object, updates its automatically generated OpenType features"""
    for feature in font.features:
        if feature.automatic:
            feature.update()


def getDesignSpaceDocument(font, format):
    __doc__ = """Returns a designspaceLib DesignSpaceDocument populated with informated from the provided font object"""
    doc = DesignSpaceDocument()
    addAxes(doc, font)
    sources = getSources(font,format)
    addSources(doc, sources)
    special_sources = getSpecialSources(font,format)
    addSources(doc, special_sources)
    instances = getInstances(font, format)
    addInstances(doc, instances)
    condition_list, replacement_list = getConditionsFromOT(font)
    applyConditionsToRules(doc, condition_list, replacement_list)
    return doc


def generateMastersAtBraces(font, temp_project_folder, format):
    __doc__ = """Provided a font object and export destination, exports all brace layers as individual UFO masters"""
    global delete_unnecessary_glyphs
    special_layer_axes = getSpecialLayerAxes(font)
    for i, special_layer_axis in enumerate(special_layer_axes):
        axes = list(special_layer_axis.values())
        font.instances.append(GSInstance())
        ins = font.instances[-1]
        ins.name = getNameWithAxis(font, axes, format)
        ufo_file_name = "%s.ufo" % ins.name
        style_name = getStyleNameWithAxis(font, axes)
        ins.styleName = style_name
        ins.axes = axes
        brace_font = ins.interpolatedFont
        brace_font.masters[0].name = style_name
        if delete_unnecessary_glyphs:
            glyph_names_to_delete = getNonSpecialGlyphs(font, axes)
            for glyph in glyph_names_to_delete:
                del(brace_font.glyphs[glyph])
            feature_keys = [feature.name for feature in brace_font.features]
            for key in feature_keys:
                del(brace_font.features[key])
            class_keys = [font_class.name for font_class in brace_font.classes]
            for key in class_keys:
                del(brace_font.classes[key])
            for glyph in brace_font.glyphs:
                if glyph.rightKerningGroup:
                    glyph.rightKerningGroup = None
                if glyph.leftKerningGroup:
                    glyph.leftKerningGroup = None
                if glyph.topKerningGroup:
                    glyph.topKerningGroup = None
                if glyph.bottomKerningGroup:
                    glyph.bottomKerningGroup = None
            brace_font.kerning = {}
            brace_font.kerningRTL = {}
            brace_font.kerningVertical = {}
        ufo_file_path = os.path.join(temp_project_folder, ufo_file_name)
        exportSingleUFObyMaster(
            brace_font.masters[0], ufo_file_path)


def fixStyleName(name, path):
    __doc__ = """Provided a master name and its path, swaps the styleName attribute in fontinfo.plist for the master name. This is required by some plugins like ScaleFast."""
    new_path = os.path.join(path, "fontinfo.plist")
    with open(new_path, "rb") as file:
        pl = load(file)
        pl["styleName"] = name
    with open(new_path, "wb") as file:
        dump(pl, file, fmt=FMT_XML)


def exportSingleUFObyMaster(master, dest):
    __doc__ = """Provided a master and destination path, exports a UFO"""
    global use_production_names
    global decompose_smart_stuff
    global add_mastername_as_stylename
    __doc__ = """Provided a master, destination, and name, exports a UFO file of that master"""
    exporter = NSClassFromString('GlyphsFileFormatUFO').alloc().init()
    exporter.setFontMaster_(master)
    exporter.setConvertNames_(use_production_names)
    exporter.setDecomposeSmartStuff_(decompose_smart_stuff)
    print("Exporting master: %s - %s" % (master.font.familyName, master.name))
    exporter.writeUfo_toURL_error_(master, NSURL.fileURLWithPath_(dest), None)
    if add_mastername_as_stylename:
        fixStyleName(master.name, dest)


def exportUFOMasters(font, dest, format):
    __doc__ = """Provided a font object and a destination, exports a UFO for each master in the UFO, not including special layers (for that use generateMastersAtBraces)"""
    for master in font.masters:
        font_name = getFamilyNameWithMaster(font, master, format)
        file_name = "%s.glyphs" % font_name
        ufo_file_name = file_name.replace('.glyphs', '.ufo')
        ufo_file_path = os.path.join(dest, ufo_file_name)
        exportSingleUFObyMaster(master, ufo_file_path)


def main():
    global to_build
    global add_build_script
    # use a copy to prevent modifying the open Glyphs file
    font = Glyphs.font.copy()
    # put all special layers on the same masterID
    alignSpecialLayers(font)
    # update any automatically generated features that need it
    updateFeatures(font)
    # remove overlaps and decompose glyphs if set at top
    removeOverlaps(font)
    decomposeGlyphs(font)

    # as a destination path (and empty it first if it exists)
    file_path = Glyphs.font.parent.fileURL().path()
    file_dir = os.path.dirname(file_path)
    dest = os.path.join(file_dir, 'ufo')
    if os.path.exists(dest):
        shutil.rmtree(dest)
    

    # when creating files below, export them to tmp_dir before we copy it over.
    # tempfile will automatically delete the temp files we generated
    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_project_folder = os.path.join(tmp_dir, "ufo")
        os.mkdir(temp_project_folder)
        master_dir = os.path.join(temp_project_folder,"masters")
        os.mkdir(master_dir)
        
        # remove the OpenType substituties as they are now in the designspace as conditionsets
        removeSubsFromOT(font)

        # generate a designspace file based on metadata in the copy of the open font
        print("Building variable designspace from font metadata...")
        designspace_doc = getDesignSpaceDocument(font, "variable")
        print("Building static designspace from font metadata...")
        if to_build["static"] or (to_build["variable"] and not hasVariableFamilyName(font)):
            static_designspace_doc = getDesignSpaceDocument(font, "static")
            static_designspace_path = "%s/%s.designspace" % (temp_project_folder, getFamilyName(font,"static"))
            static_designspace_doc.write(static_designspace_path)
        if to_build["variable"] and hasVariableFamilyName(font):
            variable_designspace_doc = getDesignSpaceDocument(font, "variable")
            variable_designspace_path = "%s/%s.designspace" % (temp_project_folder, getFamilyName(font, "variable"))
            variable_designspace_doc.write(variable_designspace_path)
        print("Building UFOs for masters...")
        # We only need one set of masters
        if to_build["static"] and not to_build["variable"]:
            exportUFOMasters(font, temp_project_folder, "static")
            print("Building UFOs for brace layers if present...")
            generateMastersAtBraces(font, temp_project_folder, "static")
        else:
            exportUFOMasters(font, temp_project_folder, "variable")
            print("Building UFOs for brace layers if present...")
            generateMastersAtBraces(font, temp_project_folder, "variable")

        for file in glob.glob(os.path.join(temp_project_folder,"*.ufo")):
            shutil.move(file,master_dir)
        if add_build_script:
            script_dir = os.path.join(temp_project_folder,"scripts")
            if os.path.exists(script_dir):
                shutil.rmtree(script_dir)
            else:
                os.mkdir(script_dir)
            addBuildScript(font,temp_project_folder)
            for file in glob.glob(os.path.join(temp_project_folder,"*.sh")):
                shutil.move(file, script_dir)

        # copy from temp dir to the destination. after this, tempfile will automatically delete the temp files
        shutil.copytree(temp_project_folder, dest)

    # open the output dir
    os.system("open %s" % dest.replace(" ", "\ "))
    print("Done!")

main()
