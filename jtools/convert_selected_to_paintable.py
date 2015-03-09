# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# Convert selected layers to paintable layers
# coding: utf-8
# Written by Jorel Latraille
# ------------------------------------------------------------------------------
# DISCLAIMER & TERMS OF USE:
#
# Copyright (c) The Foundry 2014.
# All rights reserved.
#
# This software is provided as-is with use in commercial projects permitted.
# Redistribution in commercial projects is also permitted
# provided that the above copyright notice and this paragraph are
# duplicated in accompanying documentation,
# and acknowledge that the software was developed
# by The Foundry.  The name of the
# The Foundry may not be used to endorse or promote products derived
# from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED ``AS IS'' AND WITHOUT ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


import mari

version = "0.01"


# ------------------------------------------------------------------------------    
# The following are used to find multi selections no matter where in the Mari Interface:
# returnTru(),getLayerList(),findLayerSelection()
# 
# This is to support a) Layered Shader Stacks b) deeply nested stacks (maskstack,adjustment stacks),
# as well as cases where users are working in pinned or docked channels without it being the current channel

# ------------------------------------------------------------------------------

def returnTrue(layer):
    """Returns True for any object passed to it."""
    return True
    
# ------------------------------------------------------------------------------
def getLayerList(layer_list, criterionFn):
    """Returns a list of all of the layers in the stack that match the given criterion function, including substacks."""
    matching = []
    for layer in layer_list:
        if criterionFn(layer):
            matching.append(layer)
        if hasattr(layer, 'layerStack'):
            matching.extend(getLayerList(layer.layerStack().layerList(), criterionFn))
        if layer.hasMaskStack():
            matching.extend(getLayerList(layer.maskStack().layerList(), criterionFn))
        if hasattr(layer, 'hasAdjustmentStack') and layer.hasAdjustmentStack():
            matching.extend(getLayerList(layer.adjustmentStack().layerList(), criterionFn))
        
    return matching
# ------------------------------------------------------------------------------

def findLayerSelection():
    """Searches for the current selection if mari.current.layer is not the same as layer.isSelected"""
    
    curGeo = mari.geo.current()
    curChannel = curGeo.currentChannel()
    channels = curGeo.channelList()
    curLayer = mari.current.layer()
    layers = ()
    layerSelList = []
    chn_layerList = ()
    
    layerSelect = False
     
    if curLayer.isSelected():
   
        chn_layerList = curChannel.layerList()
        layers = getLayerList(chn_layerList,returnTrue)
        
        for layer in layers:
    
            if layer.isSelected():

                layerSelList.append(layer)
                layerSelect = True       

    else:
    
        for channel in channels:
            
            chn_layerList = channel.layerList()
            layers = getLayerList(chn_layerList,returnTrue)
        
            for layer in layers:
    
                if layer.isSelected():
                    curLayer = layer
                    curChannel = channel
                    layerSelList.append(layer)
                    layerSelect = True

    
    if not layerSelect:
        mari.utils.message('No Layer Selection found. \n \n Please select at least one Layer.')


    return curGeo,curLayer,curChannel,layerSelList


# ------------------------------------------------------------------------------
def convertToPaintable():
    "Convert selected layers to paintable layers."
    if not isProjectSuitable(): #Check if project is suitable
        return False
    
    geo_data = findLayerSelection()
    selected = geo_data[3]
        
    for layer in selected:
        layer.makeCurrent()
        convertToPaintable = mari.actions.get('/Mari/Layers/Convert To Paintable')
        convertToPaintable.trigger()
                
    
# ------------------------------------------------------------------------------
def isProjectSuitable():
    "Checks project state and Mari version."
    MARI_2_0V1_VERSION_NUMBER = 20001300    # see below
    if mari.app.version().number() >= MARI_2_0V1_VERSION_NUMBER:
        
        if mari.projects.current() is None:
            mari.utils.message("Please open a project before running.")
            return False
            
        geo = mari.geo.current()
        if geo is None:
            mari.utils.message("Please select an object to run.")
            return False
        
        chan = geo.currentChannel()
        if chan is None:
            mari.utils.message("Please select a channel to run.")
            return False
            
        if len(chan.layerList()) == 0:
            mari.utils.message("Please select a layer to run.")
            return False

        return True
        
    else:
        mari.utils.message("You can only run this script in Mari 2.6v3 or newer.")
        return False

# ------------------------------------------------------------------------------
if __name__ == "__main__":
    convertToPaintable()

# ------------------------------------------------------------------------------
# Add action to Mari menu.
action = mari.actions.create(
    "Convert Selected To Paintable", "mari.jtools.convertSelectedToPaintable()"
    )
mari.menus.addAction(action, "MainWindow/&Layers", "Convert To Paintable")
icon_filename = "Painting.png"
icon_path = mari.resources.path(mari.resources.ICONS) + "/" + icon_filename
action.setIconPath(icon_path)