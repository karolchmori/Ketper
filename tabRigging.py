import maya.cmds as mc
import ElementsUI as elUI
import util

armLocators = []

def page(mainWidth, mainHeight):

    child = mc.columnLayout()
    mc.frameLayout(label='Structure', collapsable=True, collapse=False, marginWidth=5, marginHeight=5)
    mc.button(l='Generate Structure', c= lambda _: util.rigging.createStructureClass())

    mc.rowLayout(nc=3)
    mc.textField('structureTXT', w=mainWidth/2, tx='GRP;ANM;OFFSET')
    mc.button(l='Create Groups', w=90, c= lambda _: createCTLStructure())
    mc.setParent('..') # End rowLayout

    mc.textField('structureNameTXT', w=mainWidth/2, placeholderText='Leave empty to use first selection name')

    mc.setParent('..') # End frameLayout
    mc.frameLayout(label='Arm', collapsable=False, collapse=False, marginWidth=5, marginHeight=5)
    mc.rowColumnLayout(nc=2)
    mc.text(l='Create Locators: ')
    mc.button(l='GO', c=lambda _: createLocatorArm())

    mc.text(l='Create Arm Joints: ')
    mc.button(l='GO', c=lambda _: createArmJoints())
    mc.setParent('..') # End rowLayout
    mc.setParent('..') # End frameLayout
    mc.setParent( '..' ) # End columnLayout  

    return child

def createLocatorArm():
    global armLocators
    armLocators = util.rigging.createLocatorArm('L')

def createArmJoints():
    global armLocators
    util.rigging.createArmChain(armLocators)

def createCTLStructure():
    selectedObjects = mc.ls(selection=True)
    lastGroup = ''
    groupName = mc.textField('structureNameTXT', q=True, tx=True)
    if groupName == '':
        groupName = selectedObjects[0]
    
    if selectedObjects:
        structureValue = mc.textField('structureTXT', q=True, tx=True)
        lastGroup = util.create.createGroupStructure(structureValue,groupName,None)

        for obj in selectedObjects:
            mc.parent(obj, lastGroup)