import maya.cmds as mc
from . import create
from . import naming
from . import select
import re
import maya.api.OpenMaya as om2
import maya.OpenMaya as om1
import math

orientAttr = ['jointOrientX','jointOrientY','jointOrientZ']



def createStructureClass():

    groupStructure = 'GRP;ANM'

    # Create the main asset group
    mc.group(em=True, name='assetName')
    mc.group(em=True, name='controls_GRP', parent='assetName')

    create.createGroupStructure(groupStructure,'C_characterNode','controls_GRP')

    char_node_ctl = create.createShape('compass')
    mc.xform(char_node_ctl,s=(5,5,5))
    mc.FreezeTransformations()
    selection = mc.ls(sl=True)[0]
    mc.parent(selection, 'C_characterNode_ANM')
    mc.rename(selection,'C_characterNode_CTL')

    create.createGroupStructure(groupStructure,'C_masterWalk','C_characterNode_CTL')

    master_walk_ctl = create.createShape('compass')
    mc.xform(master_walk_ctl,s=(4,4,4))
    mc.FreezeTransformations()
    selection = mc.ls(sl=True)[0]
    mc.parent(selection, 'C_masterWalk_ANM')
    mc.rename(selection,'C_masterWalk_CTL')

    create.createGroupStructure(groupStructure,'C_preferences','C_masterWalk_CTL')

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

def getPositionObjects(objectList):
    positionList = []
    for item in objectList:
        position = mc.xform(item, q=True, ws=True, t=True)
        positionList.append(position)

    return positionList

def addInternalName(item, name):
    mc.addAttr(item, longName="internalName", dataType="string")
    mc.setAttr(item + ".internalName", name, type="string", cb=True, l=True, k=False)

def getInternalName(item):
    if mc.attributeQuery('internalName', node=item, exists=True):
        internalName = mc.getAttr(item + ".internalName")
        return internalName
    
def delInternalName(item):
    if mc.attributeQuery('internalName', node=item, exists=True):
        mc.deleteAttr(item + '.' + ".internalName")

def delInternalNameByList(itemsList):
    for item in itemsList:
        delInternalName(item)

    
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

def createLocatorArm():
    locatorNames = ['shoulder_LOC','elbow_LOC', 'wrist_LOC']

    mc.spaceLocator(n=locatorNames[0])
    addInternalName(locatorNames[0], locatorNames[0])
    mc.spaceLocator(n=locatorNames[1])
    addInternalName(locatorNames[1], locatorNames[1])
    mc.spaceLocator(n=locatorNames[2])
    addInternalName(locatorNames[2], locatorNames[2])

    return locatorNames

def createArmChain(locatorList):
    
    #We get original internal names ex houlder_LOC and we need to look for the new names ex joint_01_JNT
    newLocatorList = [] #Equals to joint_01_JNT ------- NEW NAME
    mainName = [] #Equals to joint_01 ------- NEW NAME
    internalJointNames = [] #Equals to shoulder_JNT  --------- OLD NAME

    # Select only locators with OLD NAMES but saving in the same order with NEW NAME
    for loc in locatorList:
        newLoc = getObjByInternalName(loc)
        if newLoc: 
            newLocatorList.append(newLoc)
 
    
    # Get position using NEW NAMES
    positionList = getPositionObjects(newLocatorList)

    # Create NEW NAMES
    mainName = naming.modifyNameList('replace',newLocatorList,'_LOC', '')
    jointNames = naming.modifyNameList('suffix',mainName,'_JNT', '')

    # Create OLD NAMES -- TODO: REVIEW, what if we want to use this name later?? if the character has 4 arms, the name is going to be the same for everything, but is good to have the name so you know where the connection starts??? 
    #TODO: what if we always return the arm that we create and save it in a global list??? LETS THINK LATER
    internalJointNames = naming.modifyNameList('replace', locatorList, '_LOC', '_JNT')


    #Delete Arm locators
    mc.delete(newLocatorList)
    
    
    # When creating a joint without parenting we are also saving the OLD NAME in an attribute
    mc.select(cl=True)

    shoulder = mc.joint(p=positionList[0], name = jointNames[0])
    mc.select(cl=True)

    elbow = mc.joint(p=positionList[1],  name = jointNames[1])
    mc.select(cl=True)

    wrist = mc.joint(p=positionList[2], name = jointNames[2])
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

    return jointNames


def copyJoints(listJoints, newPrefix):
    newJoints = []
    newNames = []

    duplicatedJoints = mc.duplicate(listJoints, rr=True)

    newJoints = mc.listRelatives(duplicatedJoints[0], allDescendents=True, type='joint', fullPath = True)
    newJoints.append(duplicatedJoints[0])
    mc.select(newJoints)

    selectedObjects = mc.ls(selection=True, type='transform') #we select only transform to change names

    for obj in selectedObjects:
        shortName = obj.split('|')[-1]
        cleanName = re.sub(r'\d+$', '', shortName)

        newName = newPrefix + '_' + cleanName
        mc.rename(obj, newName)
        newNames.append(newName)

    newNames.reverse()
    newList = newNames

    return newList


def createCTLJointList(listJoints, groupStructure):
    firstRoot = groupStructure.split(';')[0]
    lastRoot = ""
    listControls = []
    newName = ""

    #Create groups and CTL
    for joint in listJoints:
        newName = joint
        if joint[-3:] == 'HDL':
            newName = naming.modifyName('replace',joint, '_HDL','')
        elif joint[-3:] == 'JNT':
            newName = naming.modifyName('replace',joint, '_JNT','')

        nameCTL = newName + '_CTL'
        lastRoot = create.createGroupStructure(groupStructure,newName, lastRoot)

        #Create Controller and Parent / Rename
        create.createShape('circle')
        selection = mc.ls(sl=True)[0]

        mc.parent(selection, lastRoot)
        mc.rename(selection, nameCTL)
        mc.select(cl=True)

        #Save lastRoot to parent the next group
        lastRoot = nameCTL
        listControls.append(nameCTL)

    #Modifying orientation and position
    for joint in listJoints:
        
        newName = joint
        if joint[-3:] == 'HDL':
            newName = naming.modifyName('replace',joint, '_HDL','')
        elif joint[-3:] == 'JNT':
            newName = naming.modifyName('replace',joint, '_JNT','')
        

        #Create the groupRoot and snap it to the joint
        groupRoot = newName + '_' + firstRoot
        mc.matchTransform(groupRoot, joint, pos=True)
        
        if joint[-3:] == 'JNT':
            # Get the joint orientation
            jointOrientation = mc.getAttr(joint + '.jointOrient')[0]
            
            # Set the groupRoot's rotation to match the joint's orientation
            mc.xform(groupRoot, rotation=jointOrientation)
    
    return listControls

def createIkCTLJointList(IKHandle,poleVectorPos,groupStructure):
    firstRoot = groupStructure.split(';')[0]
    poleVectorName = naming.modifyName('replace',IKHandle,'_HDL','_PV')
    listControls = []

    #We will send the joints that need normal controls -- Only the wrist??
    listControls.append(createCTLJointList([IKHandle], groupStructure)[0])

    #Create a loc with the poleVectorPos but correct name
    poleVector = mc.spaceLocator(n=poleVectorName)

    #We will send the poleVJoint that need pole V controls
    listControls.append(createCTLJointList(poleVector, groupStructure)[0])

    #Modify position of PoleVector GRP
    groupRoot = poleVectorName + '_' + firstRoot
    mc.matchTransform(groupRoot, poleVectorPos, pos=True)
    mc.delete(poleVector)

    return listControls

def movePVControl(listJoints, control, distance):
    
    poleV = getVectorPos(listJoints[0], listJoints[1], listJoints[2], distance)
    mc.cycleCheck(e=False)
    tempConstraint = mc.parentConstraint(listJoints[1], control)

    mc.delete(tempConstraint)
    mc.cycleCheck(e=True)
    
    # Move the control to the new position and new rotation
    mc.xform(control, worldSpace=True, translation=(poleV.x, poleV.y, poleV.z))
    #mc.xform(control, worldSpace=True, rotation=((rot.x/math.pi*180.0), (rot.y/math.pi*180.0), (rot.z/math.pi*180.0)))

def getVectorPos(rootPos, midPos, endPos, distance):

    # Get the position of the triangle
    startV = om2.MVector(getWorldPos(rootPos))
    midV = om2.MVector(getWorldPos(midPos))
    endV = om2.MVector(getWorldPos(endPos))

    # Calculate the arrow vector (perpendicular) to positionate in the plane
    line = endV - startV
    point = midV - startV

    scaleValue = (line * point) / (line * line)
    projV = line * scaleValue + startV

    poleV = (midV - projV).normal() * distance + midV

    return poleV


def getWorldPos(obj):
    return mc.xform(obj, query=True, worldSpace=True, translation=True)


def parentControlJoints(listControls, listJoints):

    for i in range(0,len(listControls)):
        mc.parentConstraint(listControls[i], listJoints[i], mo=True, w=1)
    


#endregion

#TODO CHECK --------------------------------------------------------------------------------------------------------------------
def mirrorJointChain():
    selected_joints = mc.ls(selection=True, type='joint')

    if len(selected_joints) > 1 or len(selected_joints) == 0:
        print("Please select a joint chain")
        return
    for joint in selected_joints:
        mirrored_joint = mc.mirrorJoint(joint, mirrorYZ=True, searchReplace=('_L', '_R'))


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