import maya.cmds as mc
import dataFunctions as utils


#region UI elements
def checkerTableUI(rows, columns, rowTitles, columnTitles, columnWidth):
    #columnAlign=[(1, 'left'), (2, 'center'), (3, 'center'), (4, 'center'), (5, 'center'), (6, 'center'), (7, 'center'), (8, 'center')]

    mc.rowColumnLayout(bgc=[1,0.5,1] , nc=columns, 
                       cw=[(i, columnWidth) for i in range(1, columns+1)], 
                       cal=[(i,'center') for i in range(1, columns+1)])
    for row in range(rows):
        for col in range(columns):
            if row == 0 and col == 0 and columnTitles:
                mc.text(l=columnTitles[row]) 
            elif row == 0 and rowTitles:
                mc.text(l=rowTitles[col])
            elif col == 0 and columnTitles:
                mc.text(l=columnTitles[row]) 
            else:
                mc.checkBox(value=True, l='')
    mc.setParent('..')

#elUI.checkerTableUI(4,4,['','X','Y','Z'],['','T','R','S'], 17)

def separatorTitleUI(text, heightSep, widthStart, widthTotal):
    mc.rowColumnLayout(nc=3, columnOffset=[(2, 'both', 5)])
    mc.separator(height=heightSep, style='single', w=widthStart)
    mc.text(text)
    mc.separator(height=heightSep, style='single', w=widthTotal-widthStart-len(text)-45)
    mc.setParent('..')

# ColorSlider and printing the color when the button is pressed
def colorSlider():
    mc.rowColumnLayout(numberOfColumns=2)
    slider = mc.colorIndexSliderGrp(min=1, max=32)
    mc.button(l="OK", command=lambda _: utils.changeColorShape(slider))
    mc.setParent('..')

# Creates a Dropdown based on a list
def dropdownUI(name, label, listValues,defaultValue):
    dropdown = mc.optionMenu(name, l=label)
    for value in listValues:
        mc.menuItem(l=value)

    mc.optionMenu(name, e=True, v=defaultValue)



#Updates when the fields MIN - MAX changes
def updateSliderMinMax(sliderFieldName,minFieldName,maxFieldName, allowNegative, typeSlider):

    if typeSlider == 'float':
        typeField = mc.floatField
        sliderGrp = mc.floatSliderGrp
    elif typeSlider == 'int':
        typeField = mc.intField
        sliderGrp = mc.intSliderGrp

    # Get the values from the fields and the slider
    newMinValue = typeField(minFieldName, query=True, value=True)
    newMaxValue = typeField(maxFieldName, query=True, value=True)
    currentSliderValue = sliderGrp(sliderFieldName, q=True, v=True)

    if not allowNegative and (newMinValue < 0 or newMaxValue <0):
        mc.confirmDialog( title='Error', message='Values needs to be positive', button=['OK'], defaultButton='OK')
        typeField(minFieldName, edit=True, value=0)
        typeField(maxFieldName, edit=True, value=1)
        newMinValue, newMaxValue = 0, 1  # Update local values to reflect changes
    else:
        if newMaxValue > newMinValue:
            sliderGrp(sliderFieldName, edit=True, minValue=newMinValue, maxValue=newMaxValue)
            if currentSliderValue > newMaxValue:
                sliderGrp(sliderFieldName, edit=True, v=newMaxValue)
            if currentSliderValue < newMinValue:
                sliderGrp(sliderFieldName, edit=True, v=newMinValue)
        else:
            typeField(maxFieldName, edit=True, value=newMinValue + 1)
            mc.confirmDialog( title='Error', message='Max Value needs to be bigger than Min', button=['OK'], defaultButton='OK')

#
def sliderMinMaxUI(width, sliderFieldName, minFieldName, maxFieldName, precisionValue, valueWidth, minValue, maxValue, allowNegative, typeSlider, sliderCallback=None):
    sliderWidth = width - (valueWidth * 2)
    # Create a column layout
    mc.rowLayout(nc=3)

    if typeSlider == 'float':
        mc.floatSliderGrp(sliderFieldName, field=True, minValue=minValue, maxValue=maxValue, value=minValue, w=sliderWidth, columnWidth=[(1, valueWidth)], pre=precisionValue,
                      dragCommand=lambda *args: sliderCallback(mc.floatSliderGrp(sliderFieldName, query=True, value=True), sliderFieldName) if sliderCallback else None)
        
        # Create floatFields for minimum and maximum values
        mc.floatField(minFieldName, value=minValue, changeCommand=lambda *args: updateSliderMinMax(sliderFieldName, minFieldName, maxFieldName, allowNegative, typeSlider), pre=precisionValue, w=valueWidth)
        mc.floatField(maxFieldName, value=maxValue, changeCommand=lambda *args: updateSliderMinMax(sliderFieldName, minFieldName, maxFieldName, allowNegative, typeSlider), pre=precisionValue, w=valueWidth)

    elif typeSlider == 'int':
        mc.intSliderGrp(sliderFieldName, field=True, minValue=minValue, maxValue=maxValue, value=minValue, w=sliderWidth, columnWidth=[(1, valueWidth)],
                      dragCommand=lambda *args: sliderCallback(mc.intSliderGrp(sliderFieldName, query=True, value=True), sliderFieldName) if sliderCallback else None)
        # Create floatFields for minimum and maximum values
        mc.intField(minFieldName, value=minValue, changeCommand=lambda *args: updateSliderMinMax(sliderFieldName, minFieldName, maxFieldName, allowNegative, typeSlider), w=valueWidth)
        mc.intField(maxFieldName, value=maxValue, changeCommand=lambda *args: updateSliderMinMax(sliderFieldName, minFieldName, maxFieldName, allowNegative, typeSlider), w=valueWidth)
    
    mc.setParent( '..' ) # End rowLayout
    


#Move items list from the doubleListUI
def moveItemsList(sourceList, targetList):
    # Get selected items from the source list
    selectedItems = mc.textScrollList(sourceList, query=True, selectItem=True)
    if selectedItems:

        # Get the current items in the target list
        currentItems = mc.textScrollList(targetList, query=True, allItems=True) or []

        # Convert all items to a set to ensure uniqueness before appending
        current_items_set = set(currentItems)
        selected_items_set = set(selectedItems)
        updated_items_set = current_items_set.union(selected_items_set)

        # Convert the set back to a sorted list
        sortedItems = sorted(updated_items_set)

        # Clear the target list
        mc.textScrollList(targetList, edit=True, removeAll=True)

        # Append the sorted items to the target list
        mc.textScrollList(targetList, edit=True, append=sortedItems)

        # Remove selected items from the source list
        mc.textScrollList(sourceList, edit=True, removeItem=selectedItems)


def doubleListUI(selectValueList, width, height, mainListName, selectedListName):

    middleWidth = 15
    #listWidth = (width-middleWidth)/3
    listWidth = (width/2)-middleWidth
    mc.rowLayout(numberOfColumns=3)
    
    mc.textScrollList(mainListName, allowMultiSelection=True, append=selectValueList, w=listWidth, h=height)
    
    mc.columnLayout()
    # Buttons for moving items between lists
    mc.button(label='>>', command=lambda _: moveItemsList(mainListName, selectedListName))
    mc.button(label='<<', command=lambda _: moveItemsList(selectedListName, mainListName))
    mc.setParent( '..' ) # End columnLayout

    mc.textScrollList(selectedListName, allowMultiSelection=True, append=[], w=listWidth, h=height)

    mc.setParent( '..' ) # End rowLayout


def radioCollectionUI(title, valuesDict, defaultValue):
    mc.columnLayout()
    if title != '':
        mc.text(title)
    searchCol = mc.radioCollection()
    
    radioButtons = []
    #We save the button we are going to use as default later
    for value in valuesDict:
        tempButton = mc.radioButton(l=value)
        radioButtons.append(tempButton)
        if defaultValue == value:
            defaultBut = tempButton

    mc.radioButton(defaultBut, edit=True, select=True)

    mc.setParent( '..' ) # End columnLayout

    return searchCol, radioButtons


def radioCollectionUIHorizontal(title, valuesDict, defaultValue):
    mc.rowLayout(nc=2)
    if title != '':
        mc.text(title)
    searchCol = mc.radioCollection()
    
    radioButtons = []
    #We save the button we are going to use as default later
    for value in valuesDict:
        tempButton = mc.radioButton(l=value)
        radioButtons.append(tempButton)
        if defaultValue == value:
            defaultBut = tempButton

    mc.radioButton(defaultBut, edit=True, select=True)

    mc.setParent( '..' ) # End rowLayout

    return searchCol, radioButtons
#endregion