import maya.cmds as mc
from . import create
from . import naming
from . import select

orientAttr = ['jointOrientX','jointOrientY','jointOrientZ']



def createStructureClass():

    # Create the main asset group
    mc.group(em=True, name='assetName')
    mc.group(em=True, name='controls_GRP', parent='assetName')

    create.createGroupStructure('GRP;ANM','C_characterNode','controls_GRP')

    char_node_ctl = create.createShape('compass')
    mc.xform(char_node_ctl,s=(5,5,5))
    mc.FreezeTransformations()
    selection = mc.ls(sl=True)[0]
    mc.parent(selection, 'C_characterNode_ANM')
    mc.rename(selection,'C_characterNode_CTL')

    create.createGroupStructure('GRP;ANM','C_masterWalk','C_characterNode_CTL')

    master_walk_ctl = create.createShape('compass')
    mc.xform(master_walk_ctl,s=(4,4,4))
    mc.FreezeTransformations()
    selection = mc.ls(sl=True)[0]
    mc.parent(selection, 'C_masterWalk_ANM')
    mc.rename(selection,'C_masterWalk_CTL')

    create.createGroupStructure('GRP;ANM','C_preferences','C_masterWalk_CTL')

    preferences_ctl = create.createTextCurves('P')
    mc.xform(preferences_ctl,t=(0,5,-5))
    selection = mc.ls(sl=True)[0]
    mc.parent(selection, 'C_preferences_ANM')
    mc.rename(selection,'C_preferences_CTL')

    mc.group(em=True, name='rig_GRP', parent='assetName')
    mc.group(em=True, name='modules_GRP', parent='rig_GRP')
    mc.group(em=True, name='skel_GRP', parent='rig_GRP')
    mc.group(em=True, name='geoLayering_GRP', parent='rig_GRP')
    mc.group(em=True, name='skeletonHierarchy_GRP', parent='rig_GRP')

    mc.group(em=True, name='model_GRP', parent='assetName')
    mc.group(em=True, name='groom_GRP', parent='assetName')
    mc.group(em=True, name='clothSim_GRP', parent='assetName')


def nullJointOrients(joint):
    mc.setAttr(joint + '.' + orientAttr[0], 0)
    mc.setAttr(joint + '.' + orientAttr[1], 0)
    mc.setAttr(joint + '.' + orientAttr[2], 0)

def getPositionLoc(locatorList):
    positionList = []
    for loc in locatorList:
        position = mc.xform(loc, q=True, ws=True, t=True)
        positionList.append(position)

    return positionList

def addInternalName(item, name):
    mc.addAttr(item, longName="internalName", dataType="string")
    mc.setAttr(item + ".internalName", name, type="string", cb=True, l=True, k=False)

def getInternalName(item):
    if mc.attributeQuery('internalName', node=item, exists=True):
        internalName = mc.getAttr(item + ".internalName")
        return internalName
    
def getObjByInternalName(internalName):
    #Select original Arm Locators
    selectedObjects = mc.ls(dag=True, type='transform')
    mc.select(selectedObjects)

    #Get InternalNames
    for obj in selectedObjects:
        originalName = getInternalName(obj)
        if originalName and originalName == internalName:
            newObject = obj
            return newObject

def displayLabelJoint(itemsList):
    #Display Label
    for item in itemsList:
        mc.setAttr(f"{item}.type", 18) 
        mc.setAttr(f"{item}.drawLabel", 1)
        mc.setAttr(f"{item}.otherType", item, type='string')

#region Arm Related

def createLocatorArm(side):
    locatorNames = ['shoulder_LOC','elbow_LOC', 'wrist_LOC']

    if side == 'L':
        locatorNames = naming.modifyNameList('prefix',locatorNames,'L_','')
    else:
        locatorNames = naming.modifyNameList('prefix',locatorNames,'R_','')

    mc.spaceLocator(n=locatorNames[0])
    addInternalName(locatorNames[0], locatorNames[0])
    mc.spaceLocator(n=locatorNames[1])
    addInternalName(locatorNames[1], locatorNames[1])
    mc.spaceLocator(n=locatorNames[2])
    addInternalName(locatorNames[2], locatorNames[2])

    return locatorNames

def createArmChain(locatorList):
    
    #We get original internal names ex L_shoulder_LOC and we need to look for the new names ex L_joint_01_JNT
    newLocatorList = [] #Equals to L_joint_01_JNT ------- NEW NAME
    mainName = [] #Equals to L_joint_01 ------- NEW NAME
    internalJointNames = [] #Equals to L_shoulder_JNT  --------- OLD NAME

    # Select only locators with OLD NAMES but saving in the same order with NEW NAME
    for loc in locatorList:
        newLoc = getObjByInternalName(loc)
        if newLoc: 
            newLocatorList.append(newLoc)
 
    
    # Get position using NEW NAMES
    positionList = getPositionLoc(newLocatorList)

    # Create NEW NAMES
    mainName = naming.modifyNameList('replace',newLocatorList,'_LOC', '')
    jointNames = naming.modifyNameList('suffix',mainName,'_JNT', '')

    # Create OLD NAMES
    internalJointNames = naming.modifyNameList('replace', locatorList, '_LOC', '_JNT')
    #Delete Arm locators
    mc.delete(newLocatorList)
    
    
    # When creating a joint without parenting we are also saving the OLD NAME in an attribute
    mc.select(cl=True)

    shoulder = mc.joint(p=positionList[0], name = jointNames[0])
    addInternalName(jointNames[0], internalJointNames[0])
    mc.select(cl=True)

    elbow = mc.joint(p=positionList[1],  name = jointNames[1])
    addInternalName(jointNames[1], internalJointNames[1])
    mc.select(cl=True)

    wrist = mc.joint(p=positionList[2], name = jointNames[2])
    addInternalName(jointNames[2], internalJointNames[2])
    mc.select(cl=True)

    #Aim Constraints to get the correct orientation
    mc.aimConstraint(jointNames[1],jointNames[0], wut='object', wuo=jointNames[2], aim=(1,0,0), u=(0,0,1))
    mc.delete( f"{jointNames[0]}_aimConstraint1")

    mc.aimConstraint(jointNames[2],jointNames[1], wut='object', wuo=jointNames[0], aim=(1,0,0), u=(0,0,1))
    mc.delete( f"{jointNames[1]}_aimConstraint1")

    #Freeze transformation in rotation
    mc.select(jointNames)
    mc.makeIdentity(apply=True, rotate=True )
    mc.select(cl=True)

    #Group them
    mc.parent(jointNames[2],jointNames[1])
    mc.parent(jointNames[1],jointNames[0])
    
    #Clear JointOrients of last joint (Important to do it at the end)
    nullJointOrients(jointNames[2])

    

#endregion

#TODO CHECK --------------------------------------------------------------------------------------------------------------------
def mirrorJointChain():
    selected_joints = mc.ls(selection=True, type='joint')

    if len(selected_joints) > 1 or len(selected_joints) == 0:
        print("Please select a joint chain")
        return
    for joint in selected_joints:
        mirrored_joint = mc.mirrorJoint(joint, mirrorYZ=True, searchReplace=('_L', '_R'))


#TODO: REVIEW and TEST
def orientJoints():
    sel = mc.ls(sl=1,o=1,type='joint')
    mc.OrientJoint()
    jointChildren = mc.listRelatives(sel,ad=1)
    endJoint = jointChildren[0]
    mc.setAttr(endJoint + '.jointOrientX',0)
    mc.setAttr(endJoint + '.jointOrientY',0)
    mc.setAttr(endJoint + '.jointOrientZ',0)





#Show orientation of selected joints
def showJointOrientation():
    selected_joints = mc.ls(selection = True, type = 'joint')

    for joint in selected_joints:
        mc.setAttr(f"{joint}.displayLocalAxis", 1)



#Create a IK leg
def createLegIK():
    # Create the joint chain
    hip_joint = mc.joint(p=(0, 10, 0), name="L_hip_joint")
    knee_joint = mc.joint(p=(0, 5, 2), name="L_knee_joint")
    ankle_joint = mc.joint(p=(0, 0, 0), name="L_ankle_joint")
    mc.select(clear=True)
    
    # Create IK handle
    ik_handle = mc.ikHandle(solver="ikRPsolver", startJoint= hip_joint, endEffector = ankle_joint, name="leg_ikHandle")[0]
    
    mc.select(clear=True)
 

#endregion