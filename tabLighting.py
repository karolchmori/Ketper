import maya.cmds as mc
import ElementsUI as elUI
import util

AOVsButtons = ['addAOVsBTT','impAOVsBTT','expAOVsBTT']


def page(mainWidth, mainHeight):

    child = mc.columnLayout()
    mc.frameLayout(label='Render Layer', collapsable=False, collapse=False, marginWidth=5, marginHeight=5)
    mc.rowLayout(nc=4)
    mc.text(l='Current Layer: ')
    mc.textField('currentLayerTXT', en=False, w=mainWidth-140)
    mc.text(l='')
    mc.button('currentLayerButton', l='Load', c= lambda _:loadCurrentLayer())
    mc.setParent('..') # End rowLayout

    mc.setParent('..') # End frameLayout
    mc.frameLayout(label='AOV', collapsable=True, collapse=False, marginWidth=5, marginHeight=5)

    mc.rowLayout(nc=2, adjustableColumn = 2)
    selectionAOVs = elUI.doubleListUI('', mainWidth - 80, 100, 'activeAOVList','enabledAOVList')
    mc.columnLayout()

    mc.button(AOVsButtons[0], l='Modify', en=False, c= lambda _: modifyEnabledAOVs()) # Able to delete all enabled AOVs, updates checking if the enabled are active or not.
    mc.button(AOVsButtons[1], l='Import', en=False, c= lambda _: importEnabledAOVs()) # Imports the json file with the selected AOV's and updates (upsert)
    mc.button(AOVsButtons[2], l='Export', en=False, c= lambda _: exportEnabledAOVs()) # Creates a json with the selection 
    mc.setParent( '..' ) # End columnLayout
    mc.setParent( '..' ) # End rowLayout

    
    mc.button(l='TEST2')
    mc.setParent('..') # End frameLayout
    mc.setParent( '..' ) # End columnLayout  

    return child

def loadCurrentLayer():
    currentLayer = util.rendering.getCurrentLayer()
    currentLayer = util.naming.modifyName("delete",currentLayer,"rs_")
    
    mc.textScrollList('enabledAOVList', edit=True, removeAll=True)
    mc.textScrollList('activeAOVList', edit=True, removeAll=True)

    if currentLayer:
        mc.textField('currentLayerTXT', e=True, tx=currentLayer)
        
        util.select.modifyButtonList(AOVsButtons, True)

        #Load available AOVs and Active
        activeAOVList = util.rendering.getactiveAOVs()
        enabledAOVList = util.rendering.getenabledAOV(currentLayer)
        
        #Starting point
        for aov in activeAOVList:
            if len(aov) != 0:
                newName = util.naming.modifyName('delete', aov, 'aiAOV_')
                if aov in enabledAOVList:
                    mc.textScrollList('enabledAOVList', edit=True, append=newName)
                else:
                    mc.textScrollList('activeAOVList', edit=True, append=newName)

    else: 
        mc.confirmDialog( title='Error', message='Please set a visible Layer', button=['OK'], defaultButton='OK')

    util.select.setfocusMaya()

#TODO IF IT EXISTS DON'T ADD
def modifyEnabledAOVs():
    currentLayer = mc.textField('currentLayerTXT', q=True, tx=True)
    visibleLayer = util.rendering.getCurrentLayer()
    visibleLayer = util.naming.modifyName("delete",currentLayer,"rs_")
    
    if currentLayer == visibleLayer:
        selectedAOVs = util.select.getSelectedValuesDoubleList('enabledAOVList')
        
        if selectedAOVs:
            #first we create the collection with original names
            util.rendering.createAOVCollection(currentLayer, selectedAOVs)
            #Modify values (BE CAREFUL NAMING)
            selectedAOVs = util.naming.modifyNameList('prefix', selectedAOVs,'aiAOV_', '')

            for aov in selectedAOVs:
                mc.setAttr(f"{aov}.enabled", 1)
        else:
            util.rendering.deleteAOVCollection(currentLayer)
            loadCurrentLayer()
    else: 
        mc.confirmDialog( title='Error', message="Please make sure loaded layer and visible are the same", button=['OK'], defaultButton='OK')


def importEnabledAOVs():
    currentLayer = mc.textField('currentLayerTXT', q=True, tx=True)
    visibleLayer = util.rendering.getCurrentLayer()
    visibleLayer = util.naming.modifyName('delete',currentLayer,"rs_")
    activeAOVs = util.select.getSelectedValuesDoubleList('activeAOVList')

    if currentLayer == visibleLayer:
        # Define a filename (or use a file dialog to choose one)
        result = mc.fileDialog2(fileMode=1, caption='Load AOVs', fileFilter='JSON Files (*.json)')
        importingList = []
        if result:
            for filename in result:
                #filename = result[0]
                baseFilename = util.file.getFileName(filename)
                data = util.file.readFile(filename)
                importingList = data

                #We validate that the importing value is in active AOVS and also if its there we add it and delete it from active AOVs list
                for aov in importingList:
                    if aov in activeAOVs:
                        mc.textScrollList('activeAOVList', edit=True, removeItem=aov)
                        mc.textScrollList('enabledAOVList', edit=True, append=aov)
    else: 
        mc.confirmDialog( title='Error', message="Please make sure loaded layer and visible are the same", button=['OK'], defaultButton='OK')


def exportEnabledAOVs():
    currentLayer = mc.textField('currentLayerTXT', q=True, tx=True)
    visibleLayer = util.rendering.getCurrentLayer()
    visibleLayer = util.naming.modifyName('delete',currentLayer,"rs_")

    selectedAOVs = util.select.getSelectedValuesDoubleList('enabledAOVList')
    if currentLayer == visibleLayer:
        if selectedAOVs:
            selection = selectedAOVs

            # Define a filename (or use a file dialog to choose one)
            result = mc.fileDialog2(fileMode=0, caption='Save AOVs', dir= currentLayer + "_AOVs" +'.json', fileFilter='JSON Files (*.json)')
            if result:
                filename = result[0]
                if not filename.lower().endswith('.json'):
                    filename += '.json'
                util.file.createFile(filename, selection)
    else: 
        mc.confirmDialog( title='Error', message="Please make sure loaded layer and visible are the same", button=['OK'], defaultButton='OK')
