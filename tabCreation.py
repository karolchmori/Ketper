import maya.cmds as mc
import dataFunctions as utils
import ElementsUI as elUI
import util

selObjRandom = {}
selChanRandom = {}
channelLayout = None
randomFrame = None

def page(mainWidth, mainHeight):

    #Values
    shapesButtonDict = ['arrow','square','triangle','rhombus','circle','cube','sphere','none']
    # Define the values for the dropdown menus
    pivotMenuValues = ['negative', 'neutral', 'positive']

    child = mc.rowColumnLayout()

    # -------------------------------------------------------
    # ------------------------SHAPES ------------------------
    # -------------------------------------------------------
    mc.frameLayout(label='Shapes', collapsable=False, collapse=False, marginWidth=5, marginHeight=5)
    mc.columnLayout()
    
    mc.rowLayout(nc=2)
    shapeBuildCol, shapeBuildRadioButtons = elUI.radioCollectionUIHorizontal('', ['create','replace'], 'create')
    mc.button(l="Combine", c=lambda _: util.create.combineObjects())
    mc.setParent('..') # End rowLayout

    # Add buttons with a loop using the dictionary
    mc.rowColumnLayout(nc=4, columnSpacing=[(2, 5), (3, 5), (4, 5)])

    for shape in shapesButtonDict:
        mc.iconTextButton(w= 40, h= 40, style='iconOnly', bgc=(0.5, 0.5, 0.5),
                          image1='icons/'+shape+'.png', l=shape, command=lambda _=None, s=shape: buildShapes(s, shapeBuildRadioButtons))
    
    mc.setParent('..') # End rowColumnLayout
    
    mc.rowLayout(nc=2)
    mc.textField('textCurveTXT', w=100, placeholderText='Write Text to Curves')
    mc.button(l='Generate', c= lambda _: createTextToCurve())
    mc.setParent('..') # End rowLayout
    mc.setParent('..') # End ColumnLayout
    mc.setParent('..') # End frameLayout

    # -------------------------------------------------------
    # ------------------------ COLOR ------------------------
    # -------------------------------------------------------
    # A slider with a button that when its clicked changes the curves color
    frame = mc.frameLayout(l='Color', collapsable=False, collapse=False, marginWidth=5, marginHeight=5)
    slider = elUI.colorSlider()
    mc.setParent('..') # End frameLayout

    # -------------------------------------------------------
    # ----------------------- PIVOTS ------------------------
    # -------------------------------------------------------
    mc.frameLayout(l='Pivot', collapsable=False, collapse=False, marginWidth=5, marginHeight=5)
    pivotColumnWidth = (mainWidth + 20)/4
    mc.rowColumnLayout(nc=4, rowOffset=[(1,'bottom',5)],
                       columnWidth=[(1, pivotColumnWidth), (2, pivotColumnWidth), (3, pivotColumnWidth), (4, pivotColumnWidth)], 
                       columnOffset=[(4, 'left', 5)])
    mc.text(l='X')
    mc.text(l='Y')
    mc.text(l='Z')
    mc.text(l='') #placeholder
    
    # Create three dropdown menus
    elUI.dropdownUI('pivotXMenu', pivotMenuValues, pivotMenuValues[1])
    elUI.dropdownUI('pivotYMenu', pivotMenuValues, pivotMenuValues[1])
    elUI.dropdownUI('pivotZMenu', pivotMenuValues, pivotMenuValues[1])

    mc.button(l="OK", c=lambda _: utils.movePivot(
        choiceX=mc.optionMenu('pivotXMenu', q=True, v=True),
        choiceY=mc.optionMenu('pivotYMenu', q=True, v=True),
        choiceZ=mc.optionMenu('pivotZMenu', q=True, v=True)
        ))

    mc.setParent('..') # End rowColumnLayout
    mc.setParent('..') # End frameLayout

    # -------------------------------------------------------
    # ----------------------- RANDOM ------------------------
    # -------------------------------------------------------
    randomFrame = mc.frameLayout(l='Random', collapsable=False, collapse=False, marginWidth=5, marginHeight=5)
    sliderWidth = mainWidth-150
    floatWidth = 40

    mc.rowLayout(nc=5, cw=[(1,50),(2,mainWidth-(60*4)),(3,70),(4,60),(5,60)])
    mc.button(l='New Sel', c=lambda _: saveOriginalTransforms())
    mc.floatSliderGrp('selSlider', en=False, columnWidth=[(1, 40)], minValue=0.0, maxValue=1.0, value=1.0, pre=2, field=True, dragCommand=lambda _:updateSelectionAction())
    mc.button('newRandB',l='New Result', en=False, c=lambda _: newRandomAction())
    mc.button('retouchRanB', l='Retouch', en=False, c=lambda _: retouchRandomAction())
    mc.button(l='Clear', c=lambda _: clearRandomAction())
    mc.setParent('..') # End rowLayout
    # -------------------------- TITLES -------------------------
    randomColW = 18
    
    mc.rowColumnLayout(nc=6, cw=[(1,randomColW),(2,randomColW),(3,randomColW),(4,randomColW),(5,floatWidth+15),(6,mainWidth-(randomColW * 4)-floatWidth-10)])
    mc.text(l='')
    mc.text(l='X')
    mc.text(l='Y')
    mc.text(l='Z')
    mc.text(l='Multiply')
    mc.rowLayout(nc=3, cw3=(sliderWidth-((floatWidth*2)-10),floatWidth,floatWidth))
    mc.text(l=' Range')
    mc.text(l='Min')
    mc.text(l='Max')
    mc.setParent('..') # End rowLayout
    # ----------------------- TRANSLATE ------------------------
    mc.text(l='T  ')
    mc.checkBox('translateNumX', l='', v=True)
    mc.checkBox('translateNumY', l='', v=True)
    mc.checkBox('translateNumZ', l='', v=True)
    mc.floatField('translateNumMulti', pre=2, v=1, w=floatWidth)
    elUI.sliderMinMaxUI(sliderWidth, 'translateNumSlider','translateNumMin','translateNumMax', 2, floatWidth, 0.0, 10.0, True, 'float', sliderCallback=sliderTranslateChange)
    # ----------------------- ROTATE ------------------------
    mc.text(l='R  ')
    mc.checkBox('rotateNumX', l='', v=True)
    mc.checkBox('rotateNumY', l='', v=True)
    mc.checkBox('rotateNumZ', l='', v=True)
    mc.floatField('rotateNumMulti', pre=2, v=1, w=floatWidth)
    elUI.sliderMinMaxUI(sliderWidth, 'rotateNumSlider','rotateNumMin','rotateNumMax', 2, floatWidth, 0.0, 90.0, True, 'float', sliderCallback=sliderRotateChange)
    # ----------------------- SCALE ------------------------
    mc.text(l='S  ')
    mc.checkBox('scaleNumX', l='', v=True)
    mc.checkBox('scaleNumY', l='', v=True)
    mc.checkBox('scaleNumZ', l='', v=True)
    mc.floatField('scaleNumMulti', pre=2, v=1, w=floatWidth)
    elUI.sliderMinMaxUI(sliderWidth, 'scaleNumSlider','scaleNumMin','scaleNumMax', 2, floatWidth, 1.0, 5.0, False, 'float', sliderCallback=sliderScaleChange)
    mc.setParent('..') # End rowColumnLayout
    mc.rowLayout(nc=2)
    elUI.separatorTitleUI('Channels',5,20,mainWidth-60)
    mc.button('loadChanB', l='Load', en=False, c=lambda _: loadChannelSelectionAction(mainWidth, floatWidth+20, randomFrame))
    mc.setParent('..') # End rowLayout
    mc.setParent('..') # End frameLayout

    mc.setParent( '..' ) # End columnLayout


    return child #important to return all information

def buildShapes(s, shapeBuildRadioButtons):
    selectedObjects = mc.ls(selection=True)

    for button in shapeBuildRadioButtons:
        if mc.radioButton(button, query=True, select=True):
            valueRadio = mc.radioButton(button, query=True, label=True)
            break
    
    if valueRadio == 'create':
        util.create.createShape(s)
    elif valueRadio == 'replace':
        if selectedObjects:
            for obj in selectedObjects:
                newObj = util.create.createShape(s)
                util.create.replaceCurve(obj, newObj)
    mc.select(cl=True)

def createTextToCurve():
    textC = mc.textField('textCurveTXT', q=True, tx=True)
    if textC:
        util.create.createTextCurves(textC) 



#region Random Channel

def applyChannelAction(newValue, sliderFieldName):
    #def applyTransformation(transformationType, newValue, multiplyValueKey, boolKeys, minValKey):
    # GET VALUES
    if selObjRandom and selChanRandom:
        attrName = ''

        for attr, data in selChanRandom.items():
            if data['name'] == sliderFieldName:
                attrName = attr

        channelType = selChanRandom[attrName]['type']
        minName = sliderFieldName + "NumMin"
        
        if channelType == 'double' or channelType == 'float' or channelType == 'doubleLinear':
            typeField = mc.floatField
        elif channelType == 'bool' or channelType == 'int' or channelType == 'long':
            typeField = mc.intField

        selectedObjects = mc.ls(selection=True)
        selectedObjects = util.select.filterFlattenSelection(selectedObjects)
        if selectedObjects:
            for obj in selectedObjects:
                if obj in selObjRandom:
                    minVal = typeField(minName, q=True, v=True)
                    initialPosition = selObjRandom[obj][attrName]
                    if initialPosition or initialPosition == 0:
                        if newValue != minVal:
                            newPosition = util.random.getNumber([minVal, newValue])
                            resultingPosition = initialPosition + newPosition
                            mc.setAttr(f"{obj}.{attrName}", resultingPosition)
                        else:
                            mc.setAttr(f"{obj}.{attrName}", initialPosition)
                else:
                    mc.confirmDialog(title='Error', message=obj + " can't be found in the selection. Please create a New Selection", button=['OK'], defaultButton='OK')
                    break
    else:
        mc.confirmDialog(title='Error', message='Please create a New Selection or load Channels', button=['OK'], defaultButton='OK')


#Appart from creating the UI needs to save the values of the selected objects in the dictionary
def loadChannelSelectionAction(mainWidth, floatWidth, randomFrame):
    global selChanRandom
    global channelLayout
    selChanRandom.clear()

    # Fetch selected channels
    selectedObject = mc.ls(selection=True)[0]
    selectedChannels = util.select.getSelectedChannels(selectedObject)
    #print("Sel channels: ", selectedChannels)
    textWidth = 80
    sliderWidth = mainWidth - textWidth - 25
    allowedChannels = ['int','float','bool','double','long','doubleLinear']
    
    if selectedObject in selObjRandom:
        if selectedChannels:

            cleanChanAction(channelLayout, randomFrame)

            channelLayout = mc.scrollLayout(h=110, bv=True)
            mc.columnLayout()

            mc.rowColumnLayout(nc=2, cw=[(1,textWidth),(2,mainWidth-textWidth-20)])
            mc.text(l='')
            mc.rowLayout(nc=3, cw3=(sliderWidth-((floatWidth*2)-10),floatWidth,floatWidth))
            mc.text(l=' Range')
            mc.text(l='Min')
            mc.text(l='Max')
            mc.setParent('..') # End rowLayout

            for channel in selectedChannels:

                channelType = util.select.getTypeField(selectedObject, channel)
                #print(channelType)
                if channelType and channelType in allowedChannels:
                    minValue = 0
                    maxValue = 10.0
                    minValueF = util.select.getMinValueField(selectedObject, channel)
                    maxValueF = util.select.getMaxValueField(selectedObject, channel)

                    if minValueF:
                        minValue = minValueF
                        if minValue == maxValue:
                            maxValue = minValue + 1
                            
                    if maxValueF:
                        maxValue = maxValueF
                        if minValue == maxValue:
                            minValue = maxValue - 1

                    saveChannelTransforms(channel)   

                    mc.text(l=" " + channel)
                    selectionName = f"slider_{len(selChanRandom) + 1}"
                    selChanRandom[channel] = {'name': selectionName, 'type': channelType}
                    if channelType == 'double' or channelType == 'float' or channelType == 'doubleLinear':
                        elUI.sliderMinMaxUI(sliderWidth, selectionName,selectionName+'NumMin',selectionName+'NumMax', 2, floatWidth, minValue, maxValue, True, 'float', sliderCallback=applyChannelAction)
                    elif channelType == 'bool' or channelType == 'int' or channelType == 'long':
                        elUI.sliderMinMaxUI(sliderWidth, selectionName,selectionName+'NumMin',selectionName+'NumMax', 0, floatWidth, minValue, maxValue, True, 'int', sliderCallback=applyChannelAction)
                
            mc.setParent('..') # End rowColumnLayout
            mc.setParent('..') # End columnLayout
            mc.setParent('..') # End scrollLayout
            #for channel, name in selChanRandom.items():
            #    print(f"Object: {channel}, Name: {name}")

            #for obj, transforms in selObjRandom.items():
            #    print(f"Object: {obj}, Transformations: {transforms}")
    else:
        mc.confirmDialog( title='Error', message='The object selected is not in the Selection, please verify', button=['OK'], defaultButton='OK')

def cleanChanAction(channelLayout, randomFrame):
    if channelLayout and mc.layout(channelLayout, exists=True):
            #print(f"Deleting layout: {channelLayout}")
            mc.deleteUI(channelLayout, layout=True)
            channelLayout = None

    # Ensure the correct frameLayout is set as the parent
    if randomFrame and mc.frameLayout(randomFrame, exists=True):
        mc.setParent(randomFrame)
        #print ("MOVED the parent to: {0}".format(mc.setParent(q=True)))


def saveChannelTransforms(nameAtt):
    originalSelection = list(selObjRandom.keys())

    for obj in originalSelection:
        if mc.attributeQuery(nameAtt, node=obj, exists=True):
            attrValue = mc.getAttr(f'{obj}.{nameAtt}')
            #attrValue = mc.attributeQuery(nameAtt, node=obj, v=True)
            selObjRandom[obj][nameAtt] = attrValue

#endregion

#region Random

def updateSelectionAction():
    newValue = mc.floatSliderGrp('selSlider', query=True, value=True)
    originalSelection = list(selObjRandom.keys())

    mc.select(originalSelection)
    currentSelection = mc.ls(selection=True)
    currentSelection = util.select.filterFlattenSelection(currentSelection)

    numSelect = int(newValue * len(originalSelection))
    # Randomly select a subset
    selectedSubset = util.random.getSample(originalSelection, numSelect)
    
    mc.select(selectedSubset)

#Does it until there is no more touching
def retouchRandomAction():
    def randomizeAgain(touchingObjects):
        mc.select(touchingObjects)
        newRandomAction()
        mc.select(selectedObjects)

    selectedObjects = mc.ls(selection=True)
    touchingObjects = []
    
    max_iterations = 100
    iteration_count = 0

    #Will break when all objects are in the same position
    while iteration_count < max_iterations:
        touchingObjects = util.intersection.checkTouchingObjList(selectedObjects)
        if touchingObjects:
            randomizeAgain(touchingObjects)
            iteration_count += 1
        else:
            break

    if iteration_count >= max_iterations:
        mc.warning("Max iterations reached. Objects may still be touching.")

def clearRandomAction():
    #To avoid modifying selected objects, we will clear the selection do the changes and then modify
    selObjRandom.clear()

    mc.floatSliderGrp('selSlider', e=True, en=False, value=1.0)
    util.select.modifyButtonList(['newRandB','retouchRanB','loadChanB'], False)
    cleanChanAction(channelLayout, randomFrame)
    checkboxList = ['translateNumX', 'translateNumY', 'translateNumZ', 'rotateNumX','rotateNumY','rotateNumZ','scaleNumX','scaleNumY','scaleNumZ']
    util.select.modifyCheckBoxList(checkboxList, True, True)
    # ----------------------- TRANSLATE ------------------------
    mc.floatField('translateNumMulti', e=True, v=1)
    mc.floatField('translateNumMin', e=True, v=0.0)
    mc.floatField('translateNumMax', e=True, v=10.0)
    mc.floatSliderGrp('translateNumSlider', e=True, v=0.0)
    # ----------------------- ROTATE ------------------------
    mc.floatField('rotateNumMulti', e=True, v=1)
    mc.floatField('rotateNumMin', e=True, v=0.0)
    mc.floatField('rotateNumMax', e=True, v=90.0)
    mc.floatSliderGrp('rotateNumSlider', e=True, v=0.0)
    # ----------------------- SCALE ------------------------
    mc.floatField('scaleNumMulti', e=True, v=1)
    mc.floatField('scaleNumMin', e=True, v=1.0)
    mc.floatField('scaleNumMax', e=True, v=5.0)
    mc.floatSliderGrp('scaleNumSlider', e=True, v=1.0)


def saveOriginalTransforms():
    global selObjRandom
    selObjRandom.clear()
    selectedObjects = mc.ls(selection=True)
    checkGeometry = util.select.checkIfGeometry(selectedObjects)
    selectedObjects = util.select.filterFlattenSelection(selectedObjects)

    if selectedObjects:
        mc.floatSliderGrp('selSlider',e=True, en=True, v=1.0)
        util.select.modifyButtonList(['newRandB','loadChanB'], True)
        cleanChanAction(channelLayout, randomFrame)
        checkboxList = ['rotateNumX','rotateNumY','rotateNumZ','scaleNumX','scaleNumY','scaleNumZ']

        if checkGeometry:
            util.select.modifyCheckBoxList(checkboxList, True, True)
            mc.floatField('translateNumMax', e=True, v=10.0)
            mc.button('retouchRanB', e=True, en=True)
        else:
            util.select.modifyCheckBoxList(checkboxList, False, False)
            mc.floatField('translateNumMax', e=True, v=0.25)
            mc.button('retouchRanB', e=True, en=False)

        for obj in selectedObjects:
            translate = mc.xform(obj, query=True, worldSpace=True, translation=True)
            rotate = mc.xform(obj, query=True, worldSpace=True, rotation=True)
            scale = mc.xform(obj, query=True, worldSpace=True, scale=True)

            selObjRandom[obj] = {
                'translation': translate,
                'rotation': rotate,
                'scale': scale
            }
    else:
        mc.confirmDialog( title='Error', message='Please select any object', button=['OK'], defaultButton='OK')
    # Print the dictionary to verify
    #for obj, transforms in selObjRandom.items():
       #print(f"Object: {obj}, Transformations: {transforms}")

def newRandomAction():
    if selObjRandom:
        translateNumValue = mc.floatSliderGrp('translateNumSlider', query=True, value=True)
        rotateNumValue = mc.floatSliderGrp('rotateNumSlider', query=True, value=True)
        scaleNumValue = mc.floatSliderGrp('scaleNumSlider', query=True, value=True)

        sliderTranslateChange(translateNumValue,'translateNumSlider')
        sliderRotateChange(rotateNumValue,'rotateNumSlider')
        sliderScaleChange(scaleNumValue,'scaleNumSlider')
    else:
        mc.confirmDialog( title='Error', message='Please create a New Selection', button=['OK'], defaultButton='OK')


def applyTransformation(transformationType, newValue, multiplyValueKey, boolKeys, minValKey):
    # GET VALUES
    multiplyValue = mc.floatField(multiplyValueKey, q=True, v=True)
    boolValues = [mc.checkBox(key, q=True, v=True) for key in boolKeys]
    minVal = mc.floatField(minValKey, q=True, v=True)

    if selObjRandom:
        selectedObjects = mc.ls(selection=True)
        selectedObjects = util.select.filterFlattenSelection(selectedObjects)
        if selectedObjects:
            for obj in selectedObjects:
                if obj in selObjRandom:
                    initialPosition = selObjRandom[obj][transformationType]
                    if initialPosition:
                        if newValue != minVal:
                            newPosition = util.random.getPosition(multiplyValue, [minVal, newValue], *boolValues)
                            resultingPosition = [initialPosition[0] + newPosition[0], initialPosition[1] + newPosition[1], initialPosition[2] + newPosition[2]]
                            mc.xform(obj, **{transformationType: resultingPosition})
                        else:
                            mc.xform(obj, **{transformationType: initialPosition})
                else:
                    mc.confirmDialog(title='Error', message=obj + " can't be found in the selection. Please create a New Selection", button=['OK'], defaultButton='OK')
                    break
    else:
        mc.confirmDialog(title='Error', message='Please create a New Selection', button=['OK'], defaultButton='OK')


def sliderTranslateChange(newValue, sliderFieldName):
    applyTransformation('translation', newValue, 'translateNumMulti', ['translateNumX', 'translateNumY', 'translateNumZ'], 'translateNumMin')


def sliderRotateChange(newValue, sliderFieldName):
    applyTransformation('rotation', newValue, 'rotateNumMulti', ['rotateNumX', 'rotateNumY', 'rotateNumZ'], 'rotateNumMin')

def sliderScaleChange(newValue, sliderFieldName):
    applyTransformation('scale', newValue, 'scaleNumMulti', ['scaleNumX', 'scaleNumY', 'scaleNumZ'], 'scaleNumMin')

#endregion