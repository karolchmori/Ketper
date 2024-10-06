import maya.cmds as mc
import ElementsUI as elUI
import util

armLocators = []
armJoints = []

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
    mc.button('armLocButton', l='GO', c=lambda _: createLocatorArm())

    mc.text(l='Create Arm Joints: ')
    mc.button('armCreateButton', l='GO', c=lambda _: createArmJoints())

    mc.text(l='Restart: ')
    mc.button(l='GO', c=lambda _: restartArmChain())
    mc.setParent('..') # End rowLayout
    mc.setParent('..') # End frameLayout
    mc.setParent( '..' ) # End columnLayout  

    return child

def createLocatorArm():
    global armLocators
    armLocators = util.rigging.createLocatorArm()
    mc.button('armLocButton', e=True, en=False)
    util.select.setfocusMaya()


def createArmJoints():
    global armJoints
    groupStructure = 'GRP;ANIM;OFFSET'
    firstGroup = groupStructure.split(';')[0]

    #Create arms and duplicate to IK and FK
    armJoints.append(util.rigging.createArmChain(armLocators))
    
    #Create IK ARM
    armJoints.append(util.rigging.copyJoints(armJoints[0],'IK'))
    ikHandle = mc.ikHandle(n='IK_Arm_HDL', sj=armJoints[1][0], ee=armJoints[1][2], sol='ikRPsolver')[0] 
    listControls = util.rigging.createIkCTLJointList(ikHandle, armJoints[1][1] ,groupStructure)
    mc.parentConstraint(listControls[0], ikHandle, mo=True, w=1)
    mc.poleVectorConstraint( listControls[1], ikHandle)
    mc.orientConstraint( listControls[0], armJoints[1][2], mo=True)
    lastGroup = util.create.createGroupStructure(groupStructure,'IK_Arm_Controls',None)
    mc.parent('IK_Arm_' + firstGroup, lastGroup)
    mc.parent('IK_Arm_PV_' + firstGroup, lastGroup)
    


    #Create FK ARM Chain with all Groups
    armJoints.append(util.rigging.copyJoints(armJoints[0],'FK'))
    listControls = util.rigging.createCTLJointList(armJoints[2],groupStructure)
    util.rigging.parentControlJoints(listControls,armJoints[2])
    tempName = util.naming.modifyName('replace',armJoints[2][0],'_JNT','')
    tempRoot = tempName + '_' + firstGroup
    lastGroup = util.create.createGroupStructure(groupStructure,'FK_Arm_Controls',None)
    mc.parent(tempRoot, lastGroup)


    lastGroup = util.create.createGroupStructure(groupStructure,'Arm_Preferences_Controls',None)

    mc.button('armCreateButton', e=True, en=False)
    print(armJoints)
    util.select.setfocusMaya()


def restartArmChain():
    global armLocators
    global armJoints
    armLocators = []
    armJoints = []
    mc.button('armLocButton', e=True, en=True)
    mc.button('armCreateButton', e=True, en=True)


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