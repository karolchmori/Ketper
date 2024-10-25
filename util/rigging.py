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

def getPositionList(objectList):
    positionList = []
    for item in objectList:
        #position = mc.xform(item, q=True, ws=True, t=True)
        position = getPosition(item)
        positionList.append(position)

    return positionList

def getPosition(obj):
    return mc.xform(obj, query=True, worldSpace=True, translation=True)

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
    positionList = getPositionList(newLocatorList)

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

def generateIKSoftNodes(listJoints, listControls, ikHandle, tempConstraint, IKarmStrCON):

    IKupperLenFLM = mc.createNode('floatMath', n='IK_upperLenFLM')
    IKlowerLenFLM = mc.createNode('floatMath', n='IK_lowerLenFLM')
    IKarmFullLenFLM = mc.createNode('floatMath', n='IK_armFullLenFLM')
    mc.setAttr(IKupperLenFLM + '.operation', 2) #MULTIPLY
    mc.setAttr(IKlowerLenFLM + '.operation', 2) #MULTIPLY
    mc.setAttr(IKarmFullLenFLM + '.operation', 0) #ADD
    mc.connectAttr(listControls[0] + '.upperLenMult', IKupperLenFLM + '.floatA')
    mc.connectAttr(listControls[0] + '.lowerLenMult', IKlowerLenFLM + '.floatA')

    translateA = mc.getAttr(f"{listJoints[1][1]}.translateX")
    translateB = mc.getAttr(f"{listJoints[1][2]}.translateX")
    mc.setAttr(IKupperLenFLM + '.floatB', translateA)
    mc.setAttr(IKlowerLenFLM + '.floatB', translateB)
    mc.connectAttr(IKupperLenFLM + '.outFloat', IKarmFullLenFLM + '.floatA')
    mc.connectAttr(IKlowerLenFLM + '.outFloat', IKarmFullLenFLM + '.floatB')
  
    IKarmDisToCTLDBT = mc.createNode('distanceBetween', n='IK_armDisToCTLDBT')
    mc.connectAttr(listControls[2] + '.worldMatrix[0]', IKarmDisToCTLDBT + '.inMatrix1')
    mc.connectAttr(listControls[0] + '.worldMatrix[0]', IKarmDisToCTLDBT + '.inMatrix2')

    IKarmDisToCTLNormalFML = floatMConnect('IK_armDisToCTLNormalFML', 3, IKarmDisToCTLDBT + '.distance', None)
    mc.setAttr(IKarmDisToCTLNormalFML + '.floatB', 1) #materwalk_CTL.globalscale
    
    #Getting the value for armSotfValueRMV.maxOutput
    valueA = mc.getAttr(IKarmFullLenFLM + '.outFloat')
    valueB = mc.getAttr(IKarmDisToCTLDBT + '.distance')


    IKarmSoftValueRMV = mc.createNode('remapValue', n='IK_armSoftValueRMV')
    mc.connectAttr(listControls[0] + '.soft', IKarmSoftValueRMV + '.inputValue')
    mc.setAttr(IKarmSoftValueRMV + '.outputMin', 0.001)
    mc.setAttr(IKarmSoftValueRMV + '.inputMax', 1.0)
    mc.setAttr(IKarmSoftValueRMV + '.outputMax', valueA - valueB)
    

    IKarmSoftDisFLM = floatMConnect('IK_armSoftDisFLM', 1, IKarmFullLenFLM + '.outFloat', IKarmSoftValueRMV + '.outValue')
    IKarmDisToCTLMinSDisFLM = floatMConnect('IK_armDisToCTLMinSDisFLM', 1, IKarmDisToCTLNormalFML + '.outFloat', IKarmSoftDisFLM + '.outFloat')
    IKarmDisToCTLMinSDisDivSoftFLM = floatMConnect('IK_armDisToCTLMinSDisDivSoftFLM', 3, IKarmDisToCTLMinSDisFLM + '.outFloat', IKarmSoftValueRMV + '.outValue')

    IKminusCalculateFLM = floatMConnect('IK_minusCalculateFLM', 2, IKarmDisToCTLMinSDisDivSoftFLM + '.outFloat', None)
    mc.setAttr(IKminusCalculateFLM + '.floatB', -1.0)

    IKarmSoftEPowerFML = floatMConnect('IK_armSoftEPowerFML', 6, None, IKminusCalculateFLM + '.outFloat')
    mc.setAttr(IKarmSoftEPowerFML + '.floatA', math.e)
    
    IKarmSoftOneMinusEPowerFML = floatMConnect('IK_armSoftOneMinusEPowerFML', 1, None, IKarmSoftEPowerFML + '.outFloat')
    mc.setAttr(IKarmSoftOneMinusEPowerFML + '.floatA', 1)
    
    IKarmCalculateSoftValueMultFML = floatMConnect('IK_armCalculateSoftValueMultFML', 2, IKarmSoftValueRMV + '.outValue', IKarmSoftOneMinusEPowerFML + '.outFloat')

    # --------------------- RESULT OF THE FIRST FORMULA ------------------------------
    IKarmSoftConstantFML = floatMConnect('IK_armSoftConstantFML', 0, IKarmCalculateSoftValueMultFML + '.outFloat', IKarmSoftDisFLM + '.outFloat')
    
    # --------------------- RESULT OF THE SECOND FORMULA ------------------------------
    IKarmSoftRatioFML = floatMConnect('IK_armSoftRatioFML', 3, IKarmSoftConstantFML + '.outFloat', IKarmFullLenFLM + '.outFloat')
    
    # --------------------- RESULT OF THE THIRD FORMULA ------------------------------
    IKarmLenRatioFML = floatMConnect('IK_armLenRatioFML', 3, IKarmDisToCTLNormalFML + '.outFloat', IKarmFullLenFLM + '.outFloat')

    # --------------------- RESULT OF THE FOURTH FORMULA ------------------------------
    IKarmDisToCTLDivLenRatioFML = floatMConnect('IK_armDisToCTLDivLenRatioFML', 3, IKarmDisToCTLNormalFML + '.outFloat', IKarmLenRatioFML + '.outFloat')
    IKarmSoftEffectorDisFML = floatMConnect('IK_armSoftEffectorDisFML', 2, IKarmSoftRatioFML + '.outFloat', IKarmDisToCTLDivLenRatioFML + '.outFloat')

    
    IKarmSoftCON = mc.createNode('condition', n='IK_armSoftCON')
    mc.setAttr(IKarmSoftCON + '.operation', 2) #GREATER THAN
    mc.connectAttr(IKarmDisToCTLNormalFML + '.outFloat', IKarmSoftCON + '.firstTerm')
    mc.connectAttr(IKarmSoftDisFLM + '.outFloat', IKarmSoftCON + '.secondTerm')
    mc.connectAttr(IKarmSoftEffectorDisFML + '.outFloat', IKarmSoftCON + '.colorIfTrueR')
    mc.connectAttr(IKarmDisToCTLNormalFML + '.outFloat', IKarmSoftCON + '.colorIfFalseR')

    
    lastGroup = create.createGroupStructure('OFF;TRN','IK_armSoft', None)
    mainGroup = 'IK_armSoft_OFF'
    mc.matchTransform(mainGroup, listJoints[1][0])
    
    mc.aimConstraint(listControls[0], mainGroup, o=[0,0,0], aim=[1,0,0], wut="none")
    
    mc.connectAttr(IKarmSoftCON + '.outColorR', lastGroup + '.translateX')

    mc.cycleCheck(e=False)
    mc.delete(tempConstraint) #Will create another parent later
    mc.cycleCheck(e=True)

    mc.parentConstraint(lastGroup, ikHandle, mo=True, sr=["x","z","y"], w=1) #Only translate
    
    #VERIFIED
    mc.pointConstraint(listControls[2], mainGroup)

    #Modify the effector
    ikSolver = mc.listConnections(ikHandle, type='ikRPsolver')[0]
    mc.setAttr(ikSolver + ".tolerance", 0.0000001)


    # -------------- SOFT TOLERANCE ---------------------------- DEPENDS FROM STRETCH
    IKarmDisToCTLDivSEffectorFML = floatMConnect('IK_armDisToCTLDivSEffectorFML', 3, IKarmDisToCTLNormalFML + '.outFloat', IKarmSoftEffectorDisFML + '.outFloat')
    IKarmDisToCTLDivSEffectorMinusFML = floatMConnect('IK_armDisToCTLDivSEffectorMinusFML', 1, IKarmDisToCTLDivSEffectorFML + '.outFloat', None)
    mc.setAttr(IKarmDisToCTLDivSEffectorMinusFML + '.floatB', 1.0)

    IKarmDisToCTLDivSEffectorMultipliedFML = floatMConnect('IK_armDisToCTLDivSEffectorMultipliedFML', 2, IKarmDisToCTLDivSEffectorMinusFML + '.outFloat', listControls[0] + '.stretch')
    stretchFactorFML = floatMConnect('IK_armDisToCTLDivSEffectorMultipliedFML', 0, IKarmDisToCTLDivSEffectorMultipliedFML + '.outFloat', None)
    mc.setAttr(stretchFactorFML + '.floatB', 1.0)

    IKarmSoftEffStretchDisFML = floatMConnect('IK_armSoftEffStretchDisFML', 2, IKarmSoftEffectorDisFML + '.outFloat', stretchFactorFML + '.outFloat')

    IKarmUpperLenStretchFLM = floatMConnect('IK_armUpperLenStretchFLM', 2, IKupperLenFLM + '.outFloat', stretchFactorFML + '.outFloat')
    IKarmLowerLenStretchFLM = floatMConnect('IK_armLowerLenStretchFLM', 2, IKlowerLenFLM + '.outFloat', stretchFactorFML + '.outFloat')

    mc.disconnectAttr(IKarmSoftEffectorDisFML + '.outFloat', IKarmSoftCON + '.colorIfTrueR')
    mc.connectAttr(IKarmSoftEffStretchDisFML + '.outFloat', IKarmSoftCON + '.colorIfTrueR')
    mc.connectAttr(IKarmUpperLenStretchFLM + '.outFloat', IKarmSoftCON + '.colorIfTrueG')
    mc.connectAttr(IKarmLowerLenStretchFLM + '.outFloat', IKarmSoftCON + '.colorIfTrueB')

    mc.connectAttr(IKupperLenFLM + '.outFloat', IKarmSoftCON + '.colorIfFalseG')
    mc.connectAttr(IKlowerLenFLM + '.outFloat', IKarmSoftCON + '.colorIfFalseB')

    mc.disconnectAttr(IKarmStrCON + '.outColorR', listJoints[1][1] + '.translateX')
    mc.disconnectAttr(IKarmStrCON + '.outColorG', listJoints[1][2] + '.translateX')

    mc.connectAttr(IKarmSoftCON + '.outColorG', listJoints[1][1] + '.translateX')
    mc.connectAttr(IKarmSoftCON + '.outColorB', listJoints[1][2] + '.translateX')


def generateIKStretchNodes(listJoints, listControls):
    armLenDBT = mc.createNode('distanceBetween', n='IK_armLenDBT')
    mc.connectAttr(listControls[2] + '.worldMatrix[0]', armLenDBT + '.inMatrix1')
    mc.connectAttr(listControls[0] + '.worldMatrix[0]', armLenDBT + '.inMatrix2')

    armRelDistanceFLM = mc.createNode('floatMath', n='IK_armRelDistanceFLM')
    mc.setAttr(armRelDistanceFLM + '.operation', 3)
    mc.connectAttr(armLenDBT + '.distance', armRelDistanceFLM + '.floatA')

    upperLenMultMDL = mc.createNode('multDoubleLinear', n='IK_upperLenMultMDL')
    lowerLenMultMDL = mc.createNode('multDoubleLinear', n='IK_lowerLenMultMDL')
    mc.connectAttr(listControls[0] + '.upperLenMult', upperLenMultMDL + '.input1')
    mc.connectAttr(listControls[0] + '.lowerLenMult', lowerLenMultMDL + '.input1')
    distanceA = mc.getAttr(f"{listJoints[1][1]}.translateX")
    distanceB = mc.getAttr(f"{listJoints[1][2]}.translateX")
    mc.setAttr(upperLenMultMDL + '.input2', distanceA)
    mc.setAttr(lowerLenMultMDL + '.input2', distanceB)

    armDistanceRatioFLM = mc.createNode('floatMath', n='IK_armDistanceRatioFLM')
    mc.setAttr(armDistanceRatioFLM + '.operation', 3)
    mc.connectAttr(armRelDistanceFLM + '.outFloat', armDistanceRatioFLM + '.floatA')

    armFullLenADL = mc.createNode('addDoubleLinear', n='IK_armFullLenADL')
    mc.connectAttr(upperLenMultMDL + '.output', armFullLenADL + '.input1')
    mc.connectAttr(lowerLenMultMDL + '.output', armFullLenADL + '.input2')
    mc.connectAttr(armFullLenADL + '.output', armDistanceRatioFLM + '.floatB')

    upperLenMultStrMDL = mc.createNode('multDoubleLinear', n='IK_upperLenMultStrMDL')
    lowerLenMultStrMDL = mc.createNode('multDoubleLinear', n='IK_lowerLenMultStrMDL')
    mc.connectAttr(upperLenMultMDL + '.output', upperLenMultStrMDL + '.input1')
    mc.connectAttr(armDistanceRatioFLM + '.outFloat', upperLenMultStrMDL + '.input2')
    mc.connectAttr(lowerLenMultMDL + '.output', lowerLenMultStrMDL + '.input1')
    mc.connectAttr(armDistanceRatioFLM + '.outFloat', lowerLenMultStrMDL + '.input2')


    upperLenStrBTA = mc.createNode('blendTwoAttr', n='IK_upperLenStrBTA')
    lowerLenStrBTA = mc.createNode('blendTwoAttr', n='IK_lowerLenStrBTA')
    mc.connectAttr(listControls[0] + '.stretch', upperLenStrBTA + '.attributesBlender')
    mc.connectAttr(upperLenMultMDL + '.output', upperLenStrBTA + '.input[0]')
    mc.connectAttr(upperLenMultStrMDL + '.output', upperLenStrBTA + '.input[1]')
    mc.connectAttr(listControls[0] + '.stretch', lowerLenStrBTA + '.attributesBlender')
    mc.connectAttr(lowerLenMultMDL + '.output', lowerLenStrBTA + '.input[0]')
    mc.connectAttr(lowerLenMultStrMDL + '.output', lowerLenStrBTA + '.input[1]')

    armStrCON = mc.createNode('condition', n='IK_armStrCON')
    mc.setAttr(armStrCON + '.operation', 2)
    mc.connectAttr(armRelDistanceFLM + '.outFloat', armStrCON + '.firstTerm')
    mc.setAttr(armStrCON + '.secondTerm', 1.0)

    mc.connectAttr(upperLenMultMDL + '.output', armStrCON + '.colorIfFalseR')
    mc.connectAttr(lowerLenMultMDL + '.output', armStrCON + '.colorIfFalseG')
    mc.connectAttr(upperLenStrBTA + '.output', armStrCON + '.colorIfTrueR')
    mc.connectAttr(lowerLenStrBTA + '.output', armStrCON + '.colorIfTrueG')

    mc.connectAttr(armStrCON + '.outColorR', listJoints[1][1] + '.translateX')
    mc.connectAttr(armStrCON + '.outColorG', listJoints[1][2] + '.translateX')

    return armStrCON

#endregion

#region Controls

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


def parentControlJoints(listControls, listJoints):

    for i in range(0,len(listControls)):
        mc.parentConstraint(listControls[i], listJoints[i], mo=True, w=1)

def movePVControl(listJoints, control, distance):
    #Only translation
    poleV = getVectorPos(listJoints[0], listJoints[1], listJoints[2], distance)
    mc.cycleCheck(e=False)
    tempConstraint = mc.parentConstraint(listJoints[1], control, st=["x","z","y"])

    mc.delete(tempConstraint)
    mc.cycleCheck(e=True)
    
    # Move the control to the new position (rotation outside with a parent)
    mc.xform(control, worldSpace=True, translation=(poleV.x, poleV.y, poleV.z))


#endregion


#region Utils

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


def getVectorPos(rootPos, midPos, endPos, distance):

    # Get the position of the triangle
    startV = om2.MVector(getPosition(rootPos))
    midV = om2.MVector(getPosition(midPos))
    endV = om2.MVector(getPosition(endPos))

    # Calculate the arrow vector (perpendicular) to positionate in the plane
    line = endV - startV
    point = midV - startV

    scaleValue = (line * point) / (line * line)
    projV = line * scaleValue + startV

    poleV = (midV - projV).normal() * distance + midV

    return poleV


def createPB(jointMain, jointA, jointB, trBool, rotBool):
    node = mc.createNode('pairBlend')

    if trBool:
        mc.connectAttr(jointA + '.translate', node + '.inTranslate1')
        mc.connectAttr(jointB + '.translate', node + '.inTranslate2')
        mc.connectAttr(node + '.outTranslate', jointMain + '.translate')

    if rotBool:
        mc.connectAttr(jointA + '.rotate', node + '.inRotate1')
        mc.connectAttr(jointB + '.rotate', node + '.inRotate2')
        mc.connectAttr(node + '.outRotate', jointMain + '.rotate')

    return node

def displayLabelJoint(itemsList):
    #Display Label
    for item in itemsList:
        mc.setAttr(f"{item}.type", 18) 
        mc.setAttr(f"{item}.drawLabel", 1)
        mc.setAttr(f"{item}.otherType", item, type='string')

#Show orientation of selected joints
def showJointOrientation():
    selected_joints = mc.ls(selection = True, type = 'joint')

    for joint in selected_joints:
        mc.setAttr(f"{joint}.displayLocalAxis", 1)


def floatMConnect(name, operation, floatA, floatB):
    node = mc.createNode('floatMath', n=name)
    mc.setAttr(node + '.operation', operation)

    if floatA:
        mc.connectAttr(floatA, node + '.floatA')
    
    if floatB:
        mc.connectAttr(floatB, node + '.floatB')
    return node
#endregion


#TODO CHECK --------------------------------------------------------------------------------------------------------------------
def mirrorJointChain():
    selected_joints = mc.ls(selection=True, type='joint')

    if len(selected_joints) > 1 or len(selected_joints) == 0:
        print("Please select a joint chain")
        return
    for joint in selected_joints:
        mirrored_joint = mc.mirrorJoint(joint, mirrorYZ=True, searchReplace=('_L', '_R'))


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