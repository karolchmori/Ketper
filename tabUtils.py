import maya.cmds as mc
import ElementsUI as elUI
import util


def page(mainWidth, mainHeight):

    selectionMap = {}
    # ListValues:
    selectValueList = util.select.getTypeMapsTitle()
    searchDict = ['Scene','Hierarchy']
    renameDict = ['Numbers','Letters']

    # Tab 1 Layout
    #child = mc.columnLayout(adjustableColumn=True) # Begin columnLayout
    child = mc.columnLayout() # Begin columnLayout

    # -------------------------------------------------------
    # -------------------- SELECTION ------------------------
    # -------------------------------------------------------
    frame = mc.frameLayout(label='Search', collapsable=False, collapse=False, marginWidth=5, marginHeight=5)

    mc.rowLayout(nc=2, cw2=(mainWidth-110, 100))
    selectUI = elUI.doubleListUI(selectValueList, mainWidth-120, 100, 'searchMainList','searchSelectedList')
    mc.columnLayout()
    mc.button(l='Clear selection', w=90, c=lambda _: mc.select(clear=True))
    mc.text('')
    searchCol, searchRadioButtons = elUI.radioCollectionUI('Scope:', searchDict, searchDict[0])
    mc.setParent( '..' ) # End columnLayout  
    mc.setParent( '..' ) # End rowLayout
    
    # ---------------------- MAIN WORD + TRANSLATE + ROTATION  -------------------------
    mc.rowLayout(nc=2, adjustableColumn = 2)
    mc.columnLayout()
    mc.textField('searchTXT', placeholderText='Insert word', w=mainWidth-110)

    mc.rowLayout(nc=3) # Begin rowLayout
    mc.checkBox('translateCB',label="Translation", value=False)
    mc.checkBox('rotateCB',label="Rotation", value=False)
    mc.checkBox('scaleCB',label="Scale", value=False)
    #mc.checkBox('visibleCB',label="Visibility", value=True)
    mc.setParent( '..' ) # End rowLayout
    mc.setParent( '..' ) # End columnLayout
    mc.button(l='Select', w=60, c=lambda _: searchButtonAction(searchRadioButtons), h=40) 
    mc.setParent( '..' ) # End rowLayout

    # ---------------------- SELECTION SET -------------------------
    elUI.separatorTitleUI('Selection Sets',5,20,mainWidth-40)
    mc.rowLayout(nc=2, adjustableColumn = 2)
    selectionSetSL = mc.textScrollList('selectionSetSL', allowMultiSelection=False, height=100, w=mainWidth-130)
    mc.rowColumnLayout(nc= 2, adj=2)
    mc.button(l='View', c=lambda _: viewSelAction(selectionMap))
    mc.button(l='Load', c=lambda _: loadSelAction(selectionMap))
    mc.button(l='Add', c=lambda _: addSelAction(selectionMap))
    mc.button(l='Save', c=lambda _: saveSelAction(selectionMap))
    mc.button(l='Rename', c=lambda _: renameSelAction(selectionMap))
    mc.button(l='Remove', c=lambda _: removeSelAction(selectionMap))
    
    mc.setParent( '..' ) # End rowColumnLayout
    mc.setParent( '..' ) # End rowLayout

    mc.setParent( '..' ) # End frameLayout

    # -------------------------------------------------------
    # ---------------------- NAMING -------------------------
    # -------------------------------------------------------
    frame = mc.frameLayout(label='Naming', collapsable=False, collapse=False, marginWidth=5, marginHeight=5)

    mc.rowColumnLayout(nc=3, columnOffset=[(2, 'both', 5)]) 

    # ----------------- PREFIX / SUFFIX ---------------------
    mc.rowColumnLayout(nc=2, rowOffset=[(2, 'both', 5)])
    mc.text('Prefix')
    mc.text('Suffix')
    mc.textField('prefixTXT', w=(mainWidth/3)-40)
    mc.textField('suffixTXT', w=(mainWidth/3)-40)
    mc.setParent( '..' ) # End rowColumnLayout
    
    # ---------------------- REPLACE -------------------------
    mc.separator(style='single', horizontal=False, width=5, height=50)
    mc.rowColumnLayout(nc=2, cw=[(1,40),(2,(mainWidth/2)-65)])
    mc.text('From: ', w=20)
    mc.textField('replacefromTXT')
    mc.text('To: ', w=20)
    mc.textField('replacetoTXT', placeholderText='Leave blank to erase')
    mc.setParent( '..' ) # End rowColumnLayout

    # ----------------- BUTTONS FOR THE TOP  --------------------
    mc.button(l="Apply", c=lambda _: applyPrefixSuffixAction())
    mc.separator(style='single', horizontal=False, width=5, height=1)
    mc.button(l="Replace", c=lambda _: applyReplaceAction())

    mc.setParent( '..' ) # End rowColumnLayout

    # ---------------------- RENAME -------------------------
    elUI.separatorTitleUI('Rename',5,20,mainWidth-15)
    mc.rowColumnLayout(nc=4, cw=[(1,(mainWidth/2)+10),(2,50),(3,70)], columnOffset=[(2, 'both', 5),(3, 'right', 5),(4, 'left', 5)])
    mc.textField('renamemainTXT')
    mc.intField('renamedigitsTXT', value=3)
    renameCol, renameRadioButtons = elUI.radioCollectionUI('', renameDict, renameDict[0])
    #mc.separator(height=5, style='single')
    mc.button(l="OK", w=40, c=lambda _: applyRenameAction(renameRadioButtons))
    mc.setParent( '..' ) # End rowColumnLayout

    mc.setParent( '..' ) # End frameLayout
    
    # -------------------------------------------------------
    # -------------------- ATTRIBUTES -----------------------
    # -------------------------------------------------------

    frame = mc.frameLayout(label='Attributes', collapsable=False, collapse=False, marginWidth=5, marginHeight=5)
    mc.rowLayout(nc=4)
    mc.textField('objAttributeTXT', editable=False, placeholderText="Select one object", w=mainWidth - 130)
    mc.text('')
    mc.button(l="Load", c= lambda _: loadAttributeAction(), w=50)
    mc.button(l="Clean", c= lambda _: cleanAttributeAction(), w=50)
    mc.setParent( '..' ) # End rowLayout

    mc.rowLayout(nc=2)
    attributeUI = elUI.doubleListUI('', mainWidth-80, 100, 'attrMainList','attrSelectedList')
    mc.columnLayout()
    mc.button('attrResetB',l='Reset', c=lambda _: resetAttributeAction())
    mc.button('attrExportB',l='Export', c=lambda _: exportAttributeAction(), en=False)
    mc.button('attrImportB',l='Import', c=lambda _: importAttributeAction())
    mc.button('attrCopyB',l='Copy', c=lambda _: copyAttributeAction(), en=False)

    mc.setParent( '..' ) # End columnLayout
    mc.setParent( '..' ) # End rowLayout
    mc.setParent( '..' ) # End frameLayout

    mc.setParent( '..' ) # End columnLayout

    return child


#region Attributes
def cleanAttributeAction():
    loadedObject = mc.textField('objAttributeTXT', query=True, text=True)
    if loadedObject:
        mc.textField('objAttributeTXT', edit=True, text='')
        mc.textScrollList('attrSelectedList', edit=True, removeAll=True)
        mc.textScrollList('attrMainList', edit=True, removeAll=True)

    util.select.setfocusMaya()


def importAttributeAction():
    selectedObjects = mc.ls(selection=True)

    if selectedObjects:
        #Read attributes from json
        result = mc.fileDialog2(fileMode=1, caption='Import Attributes', fileFilter='JSON Files (*.json)')
        if result:
            filename = result[0]
            #baseFilename = util.file.getgetFileName(filename)
            listAttr = util.file.readFile(filename)
            #for each selected object
            for obj in selectedObjects:
                #for each attribute
                for attr, value in listAttr:
                    #apply attribute if exists 
                    existAttr = mc.attributeQuery(attr, node=obj, exists=True)
                    if existAttr:
                        mc.setAttr(f'{obj}.{attr}', value)

    else: 
        mc.confirmDialog( title='Error', message='Please select at least one child object.', button=['OK'], defaultButton='OK')

    util.select.setfocusMaya()

def exportAttributeAction():
    exportAttr = []
    loadedObject = mc.textField('objAttributeTXT', query=True, text=True)
    if loadedObject:
        selectedAttributes = util.select.getSelectedValuesDoubleList('attrSelectedList')
        if selectedAttributes:
            for attr in selectedAttributes:
                currentValue = util.select.getValueField(loadedObject, attr)
                exportAttr.append([attr, currentValue])
            #save it to a file:
            # Define a filename (or use a file dialog to choose one)
            result = mc.fileDialog2(fileMode=0, caption='Export Attributes', dir= loadedObject +'_attr.json', fileFilter='JSON Files (*.json)')
            if result:
                filename = result[0]
                if not filename.lower().endswith('.json'):
                    filename += '.json'
                util.file.createFile(filename, exportAttr)
        else:
            mc.confirmDialog( title='Error', message='No attributes have been selected', button=['OK'], defaultButton='OK')
    else: 
        mc.confirmDialog( title='Error', message='Please select ONE object', button=['OK'], defaultButton='OK') 

    util.select.setfocusMaya()
    #print(exportAttr)

def resetAttributeAction():
    loadedObject = mc.textField('objAttributeTXT', query=True, text=True)
    selectedObjects = mc.ls(selection=True)
    defaultAttributes = util.select.getDefaultAttributes()

    if loadedObject:
        selectedAttributes = util.select.getSelectedValuesDoubleList('attrSelectedList')
        if selectedAttributes:
            for attr in selectedAttributes:
                currentValue = util.select.getValueField(loadedObject, attr)
                defaultValue = util.select.getDefaultValueField(loadedObject, attr)
                if currentValue != defaultValue:
                    mc.setAttr(f'{loadedObject}.{attr}', defaultValue)
        else:
            mc.confirmDialog( title='Error', message='No attributes have been selected', button=['OK'], defaultButton='OK')
    else: 
        if selectedObjects:
            for obj in selectedObjects:
                for attr in defaultAttributes:
                    currentValue = util.select.getValueField(obj, attr)
                    defaultValue = util.select.getDefaultValueField(obj, attr)
                    if currentValue != defaultValue:
                        mc.setAttr(f'{obj}.{attr}', defaultValue)
        else:
            mc.confirmDialog( title='Error', message='Please select at least one object.', button=['OK'], defaultButton='OK')

    util.select.setfocusMaya()


def copyAttributeAction():
    loadedObject = mc.textField('objAttributeTXT', query=True, text=True)
    selectedObjects = mc.ls(selection=True)

    if loadedObject:
        if selectedObjects:
            selectedAttributes = util.select.getSelectedValuesDoubleList('attrSelectedList')
            if selectedAttributes:
                for obj in selectedObjects:
                    if obj != loadedObject:
                        #print("OBJ: " , obj)
                        for attr in selectedAttributes:
                            currentValue = util.select.getValueField(loadedObject, attr)
                            #check if the attribute exists in the child
                            existAttr = mc.attributeQuery(attr, node=obj, exists=True)
                            if existAttr:
                                mc.setAttr(f'{obj}.{attr}', currentValue)
            else:
                mc.confirmDialog( title='Error', message='No attributes have been selected', button=['OK'], defaultButton='OK')
        else: 
            mc.confirmDialog( title='Error', message='Please select at least one child object.', button=['OK'], defaultButton='OK')
    else: 
        mc.confirmDialog( title='Error', message='Please select one parent object.', button=['OK'], defaultButton='OK')

    util.select.setfocusMaya()

def loadAttributeAction():
    selectedObjects = mc.ls(selection=True)
    mc.textScrollList('attrSelectedList', edit=True, removeAll=True)
    mc.textScrollList('attrMainList', edit=True, removeAll=True)

    if len(selectedObjects) == 1:
        mc.textField('objAttributeTXT', edit=True, text=selectedObjects[0])
        allAttr = util.select.getAttributeObject(selectedObjects[0])
        standardAttr = util.select.getDefaultAttributes()

        #Starting point
        for attr in allAttr:
            if attr in standardAttr and len(attr) != 0:
                mc.textScrollList('attrSelectedList', edit=True, append=attr)
            else:
                mc.textScrollList('attrMainList', edit=True, append=attr)
        mc.button('attrResetB', edit=True, enable=True)
        mc.button('attrExportB', edit=True, enable=True)
        mc.button('attrCopyB', edit=True, enable=True)
        #print(allAttr)
    else: 
        mc.confirmDialog( title='Error', message='Please select ONE object', button=['OK'], defaultButton='OK')

    util.select.setfocusMaya()
#endregion

#region Selection SETS
def addSelAction(selectionList):
    selectionName = f"Selection_{len(selectionList) + 1}"
    selectedObjects = mc.ls(selection=True)
    if selectedObjects:
        # Add to the dictionary
        selectionList[selectionName] = selectedObjects
        mc.textScrollList('selectionSetSL', edit=True, append=selectionName)
        #print(selectionList)
    else: 
        mc.confirmDialog( title='Error', message='Please select objects', button=['OK'], defaultButton='OK')
    util.select.setfocusMaya()


def viewSelAction(selectionList):

    selectedItem = mc.textScrollList('selectionSetSL', query=True, selectItem=True)
    if selectedItem:
        selectionName = selectedItem[0]
        selectedObjects = selectionList.get(selectionName, [])

        if selectedObjects:
            mc.select(selectedObjects)
        #print(f"Selection '{selectionName}' contains objects: {selectedObjects}")
    else:
        mc.confirmDialog( title='Error', message='Please select an item from the Selection Set', button=['OK'], defaultButton='OK')
    util.select.setfocusMaya()

def removeSelAction(selectionList):
    selectedItem = mc.textScrollList('selectionSetSL', query=True, selectItem=True)
    if selectedItem:
        selectionName = selectedItem[0]

        # Remove from the dictionary
        if selectionName in selectionList:
            del selectionList[selectionName]
        
        # Remove from the text scroll list
        mc.textScrollList('selectionSetSL', edit=True, removeItem= selectionName)
    #print(selectionList)
    else:
        mc.confirmDialog( title='Error', message='Please select an item from the Selection Set', button=['OK'], defaultButton='OK')
    util.select.setfocusMaya()

def saveSelAction(selectionList):
    selectedItem = mc.textScrollList('selectionSetSL', query=True, selectItem=True)
    if selectedItem:
        selectionName = selectedItem[0]
        selection = selectionList.get(selectionName, [])

        # Define a filename (or use a file dialog to choose one)
        result = mc.fileDialog2(fileMode=0, caption='Save Selection', dir= selectionName+'.json', fileFilter='JSON Files (*.json)')
        if result:
            filename = result[0]
            if not filename.lower().endswith('.json'):
                filename += '.json'
            util.file.createFile(filename, selection)
    else:
        mc.confirmDialog( title='Error', message='Please select an item from the Selection Set', button=['OK'], defaultButton='OK')
    util.select.setfocusMaya()

def loadSelAction(selectionList):
    # Define a filename (or use a file dialog to choose one)
    result = mc.fileDialog2(fileMode=4, caption='Load Selection', fileFilter='JSON Files (*.json)')
    
    if result:
        for filename in result:
            #filename = result[0]
            baseFilename = util.file.getFileName(filename)
            data = util.file.readFile(filename)

            #Add to dictionary
            selection_name = baseFilename
            selectionList[selection_name] = data
            #Add to textScrollList
            mc.textScrollList('selectionSetSL', edit=True, append=selection_name)
    util.select.setfocusMaya()


def renameSelAction(selectionList):
    
    selectedItem = mc.textScrollList('selectionSetSL', query=True, selectItem=True)
    if selectedItem:
        oldName = selectedItem[0]

        # Step 2: Prompt the user for a new name
        result = mc.promptDialog( title='Rename Selection', message='Enter new name:', button=['OK', 'Cancel'],
            defaultButton='OK',  cancelButton='Cancel', dismissString='Cancel')
        
        if result == 'OK':
            newName = mc.promptDialog(query=True, text=True)
            if util.naming.isTextNumber(newName):
                # Step 3: Update the textScrollList with the new name
                mc.textScrollList('selectionSetSL', edit=True, removeItem=oldName)
                mc.textScrollList('selectionSetSL', edit=True, append=newName)
                
                # Step 4: Update the dictionary key with the new name
                selectionList[newName] = selectionList.pop(oldName)
            else:
                mc.confirmDialog( title='Error', message='Only letters, numbers and underscores (_) are allowed', button=['OK'], defaultButton='OK')
    else:
        mc.confirmDialog( title='Error', message='Please select an item from the Selection Set', button=['OK'], defaultButton='OK')
    util.select.setfocusMaya()
#endregion


#region Rename
def applyRenameAction(renameButtons):
    renamemainTextValue = mc.textField('renamemainTXT', query=True, text=True)
    renamedigitsTextValue = mc.intField('renamedigitsTXT', query=True, value=True)
    
    selectedRename = None
    for button in renameButtons:
        if mc.radioButton(button, query=True, select=True):
            selectedRename = mc.radioButton(button, query=True, label=True)
            break

    selectedObjects = mc.ls(selection=True, type='transform') #we select only transform to change names
    selectedObjects = util.select.getOutlinerOrder(selectedObjects,True)
    numberArray = []

    if selectedRename == 'Letters':
        numberArray = util.naming.generateArrayColumns(1,renamedigitsTextValue)
        numberArray = util.naming.getArrayColumnsByPosition(numberArray, len(selectedObjects),1,25)

    
    #print('Sorted objects: ', util.select.getOutlinerOrder(selectedObjects))

    i = len(selectedObjects) + 1
    if selectedObjects:
        if renamemainTextValue:
            if renamedigitsTextValue:
                for item in selectedObjects:
                    newName = renamemainTextValue
                    if selectedRename == 'Numbers':
                        i = i - 1
                        numberTag = util.naming.fillNumber(i, '0', renamedigitsTextValue, 'R')
                        newName = util.naming.addSuffix(newName,'_' + numberTag)
                    elif selectedRename == 'Letters':
                        #SOLVED in a horrible way, maybe the only one
                        # Problem with reverse --> We have to get the last possible combination and go downwards
                        wordArray = util.naming.generateLetterByNumber(numberArray)
                        newName = util.naming.addSuffix(newName,'_' + wordArray)
                        wordArray = util.naming.getLastNumArray(numberArray,25,1)
                        #print(newName)
                    mc.rename(item,newName)

            else: 
                mc.confirmDialog( title='Error', message='Digits cannot be blank', button=['OK'], defaultButton='OK')
                
        else:
            mc.confirmDialog( title='Error', message='Please insert a value', button=['OK'], defaultButton='OK')
            
    else:
        mc.confirmDialog( title='Error', message='Please select an object', button=['OK'], defaultButton='OK')

    util.select.setfocusMaya()    
    
    #print(renamemainTextValue + '__' + str(renamedigitsTextValue))


def applyReplaceAction():
    repfromTextValue = mc.textField('replacefromTXT', query=True, text=True)
    reptoTextValue = mc.textField('replacetoTXT', query=True, text=True)

    selectedObjects = mc.ls(selection=True, type='transform') #we select only transform to change names
    if selectedObjects:
        if repfromTextValue:
            for item in selectedObjects:
                newName = util.naming.replaceText(item, repfromTextValue, reptoTextValue)
                mc.rename(item,newName)
        else:
            mc.confirmDialog( title='Error', message='Please insert a value', button=['OK'], defaultButton='OK')
    else:
        mc.confirmDialog( title='Error', message='Please select an object', button=['OK'], defaultButton='OK')
    util.select.setfocusMaya()

    #print(repfromTextValue + '__' + reptoTextValue)


def applyPrefixSuffixAction():
    prefixTextValue = mc.textField('prefixTXT', query=True, text=True)
    suffixTextValue = mc.textField('suffixTXT', query=True, text=True)

    selectedObjects = mc.ls(selection=True, type='transform') #we select only transform to change names
    if selectedObjects:
        for item in selectedObjects:
            newName = item
            if prefixTextValue:
                if util.naming.notNumber(prefixTextValue):
                    newName = util.naming.addPrefix(newName,prefixTextValue)
                else:
                    mc.confirmDialog( title='Error', message='Numbers are not allowed as Prefix.', button=['OK'], defaultButton='OK')
                    util.select.setfocusMaya()
                    return
                    
            if suffixTextValue:
                newName = util.naming.addSuffix(newName,suffixTextValue)
            mc.rename(item,newName)
    else:
        mc.confirmDialog( title='Error', message='Please select an object', button=['OK'], defaultButton='OK')
    
    util.select.setfocusMaya()

    #print(prefixTextValue + '__' + suffixTextValue)
#endregion

#region Search
#SOLVED: We have a problem selecting elements when they have the same name. Can we avoid it?? --> FIXED by going backwards
def searchButtonAction(searchButtons):

    #GET SCOPE
    selectedScope = None
    for button in searchButtons:
        if mc.radioButton(button, query=True, select=True):
            selectedScope = mc.radioButton(button, query=True, label=True)
            break

    #GET SELECTED VALUES
    selectedObjects = []
    selectedTypes = util.select.getSelectedValuesDoubleList('searchSelectedList')
    searchTextValue = mc.textField('searchTXT', query=True, text=True)
    translateCBValue = mc.checkBox("translateCB", query=True, value=True)
    rotateCBValue = mc.checkBox("rotateCB", query=True, value=True)
    scaleCBValue = mc.checkBox("scaleCB", query=True, value=True)
    

    # WE get an initial seleccion, either by hierarchy or everything
    if selectedScope == 'Hierarchy':
        selectedRoot = mc.ls(selection=True, type='transform')
        #If we have a selected element --> get hierarchy and select it
        if selectedRoot:
            selectedObjects = mc.listRelatives(selectedRoot, allDescendents=True, fullPath=True)
            mc.select(selectedObjects)
        else:
            mc.confirmDialog( title='Error', message='Please select an object', button=['OK'], defaultButton='OK')
            util.select.setfocusMaya()
            return
        
    elif selectedScope == 'Scene':
        selectedObjects = mc.ls(dag=True, type='transform')
        selectedObjects = util.select.filterDefaultCam(selectedObjects)
        mc.select(selectedObjects)
        #print('SCENE: ', selectedObjects)

    
    # SEARCH BY TYPE
    if selectedTypes:
        print(selectedTypes)
        selectedObjects = util.select.filterByType(selectedTypes)        
        mc.select(selectedObjects)

    # SEARCH TEXT VALUE
    if searchTextValue:
        selectedObjects = util.select.selectByNameAndList(searchTextValue)
        mc.select(selectedObjects)    

    # ROTATE    
    if rotateCBValue:
        selectedObjects = util.select.filterObjectsTransform('rotate',0)
        mc.select(selectedObjects)
    
    # TRANSLATE   
    if translateCBValue:
        selectedObjects = util.select.filterObjectsTransform('translate',0)
        mc.select(selectedObjects)
    
    # SCALE   
    if scaleCBValue:
        selectedObjects = util.select.filterObjectsTransform('scale',1)
        mc.select(selectedObjects)

    
    if selectedObjects == []: mc.confirmDialog( title='Result', message='No results', button=['OK'], defaultButton='OK')
    util.select.setfocusMaya()
    #print(selectedObjects)
#endregion