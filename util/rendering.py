import maya.cmds as mc
from . import naming
from maya.app.renderSetup.model import renderLayer, renderSetup, collection

def getCurrentLayer():
    # Get the current render layer
    currentLayer = mc.editRenderLayerGlobals(query=True, currentRenderLayer=True)
    return currentLayer

def viewRenderLayer(layerName):
    mc.editRenderLayerGlobals(currentRenderLayer=layerName)


#I will work without the first aiAOV_ , SO KEEP IN MINE WHEN SELECTING AND SEARCHING
def getactiveAOVs():
    activeAOVs = mc.ls(type="aiAOV")
    return activeAOVs

def getenabledAOV(layerName):
    activeAOVList = getactiveAOVs()
    
    enabledList = []
    for aov in activeAOVList:
        enabled = mc.getAttr(f"{aov}.enabled")
        if enabled:
            enabledList.append(aov)
    
    return enabledList

def createAOVCollection(layerName, aovList):

    layer = renderSetup.instance().getRenderLayer(layerName) 

    try:
        aovCollection = layer.getCollectionByName("AOVCollection")
        if aovCollection:
            deleteAOVCollection(layerName)
    except Exception:
        pass  # or you could use 'continue'

    aovCollection = layer.aovCollectionInstance()

    for aov in aovList:
        subColle = collection.create(aov, collection.AOVChildCollection.kTypeId, aovName=aov)
        aovCollection.appendChild(subColle)
        override = subColle.createAbsoluteOverride('aiAOV_' + aov, 'enabled')  #(aov name, attr name)

    #print(f'Created AOV Collection: {layerName} with AOVs: {aovList}')

def deleteAOVCollection(layerName):
    layer = renderSetup.instance().getRenderLayer(layerName)  # any layer

    aovCollection = layer.getCollectionByName("AOVCollection")
    collection.delete(aovCollection)


