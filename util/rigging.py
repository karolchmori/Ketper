import maya.cmds as mc
import maya.mel as mel
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
    #Select original Limb Locators
    selectedObjects = mc.ls(dag=True, type='transform')
    mc.select(selectedObjects)

    #Get InternalNames
    for obj in selectedObjects:
        originalName = getInternalName(obj)
        if originalName and originalName == internalName:
            newObject = obj
            return newObject
        


#region Digits Related
def createCurveDigits(nameCurve, numCvs):
    start_pos=(0, 0, 0)
    length = 6
    segmentLength = length / (numCvs - 1)
    cvPositions = [(start_pos[0] + i * segmentLength, start_pos[1] , start_pos[2]) for i in range(numCvs)]

    curve = mc.curve(name=nameCurve, degree=1, point=cvPositions)
    addInternalName(curve, nameCurve)

    return curve

def createDigitsChain(obj):

    originalObj = getObjByInternalName(obj)
    mainName = naming.modifyName('replace',originalObj,'_CRV', '')

    numCvs = mc.getAttr(f"{originalObj}.degree") + mc.getAttr(f"{originalObj}.spans")

    # Create a chain of joints based on the CV positions
    jointChain = []
    
    for i in range(numCvs):
        # Get the position of each CV
        cvPos = mc.pointPosition(f"{originalObj}.cv[{i}]", world=True)

        mc.select(cl=True)
        # Create a joint at that position
        joint = mc.joint(name=f"{mainName}_0{i+1}_JNT", p=cvPos)
        mc.select(cl=True)
        jointChain.append(joint)

    mc.delete(originalObj)
    
    #Orientation
    for i in range(1, len(jointChain)):
        if i != len(jointChain) and (i+1) <= (len(jointChain))-1:
            mc.aimConstraint(jointChain[i],jointChain[i-1], wut='object', wuo=jointChain[i+1], aim=(1,0,0), u=(0,0,1))
        else:
            mc.aimConstraint(jointChain[i],jointChain[i-1], wut='object', wuo=jointChain[0], aim=(1,0,0), u=(0,0,1))
        mc.delete( f"{jointChain[i-1]}_aimConstraint1")


    #Freeze transformation in rotation
    mc.select(jointChain)
    mc.makeIdentity(apply=True, rotate=True )
    mc.select(cl=True)


    for i in reversed(range(1, len(jointChain))):
        mc.parent(jointChain[i],jointChain[i-1])

    
    #Clear JointOrients of last joint (Important to do it at the end)
    nullJointOrients(jointChain[len(jointChain)-1])
    
    return jointChain
    

    
    

#endregion

#region Limb Related



def createLocatorLimb():
    locatorNames = ['root_LOC','mid_LOC', 'end_LOC']

    mc.spaceLocator(n=locatorNames[0])
    addInternalName(locatorNames[0], locatorNames[0])
    mc.spaceLocator(n=locatorNames[1])
    addInternalName(locatorNames[1], locatorNames[1])
    mc.spaceLocator(n=locatorNames[2])
    addInternalName(locatorNames[2], locatorNames[2])

    return locatorNames

def createLimbChain(locatorList):
    
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

    # Create OLD NAMES -- TODO: REVIEW, what if we want to use this name later?? if the character has 4 limb, the name is going to be the same for everything, but is good to have the name so you know where the connection starts??? 
    #TODO: what if we always return the limb that we create and save it in a global list??? LETS THINK LATER
    internalJointNames = naming.modifyNameList('replace', locatorList, '_LOC', '_JNT')

    #Delete Limb locators
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

def generateCurvatureNodes(listJoints, controlName, limbName):
    positionsJoints = []
    
    # Get world position of each joint
    for joint in listJoints[0]:
        pos = mc.xform(joint, query=True, worldSpace=True, translation=True)
        positionsJoints.append(pos)

    # Create the EP Curve through these positions
    curve1Linear = mc.curve(n=f'{limbName}Linear_CRV', d=1, ep=positionsJoints) 
    
    #Duplicate and create a Bezier curve
    curveBezier = mc.duplicate(curve1Linear, renameChildren=True)[0]
    mel.eval("nurbsCurveToBezier");
    
    curveBezier = mc.rename(curveBezier, f'{limbName}Bezier_CRV')
    mc.select(curveBezier+ ".cv[0]", curveBezier+ ".cv[6]")
    mc.bezierAnchorPreset(p=2)
    mc.select(curveBezier+ ".cv[3]")
    mc.bezierAnchorPreset(p=0)
    
    curve2Degree = mc.duplicate(curve1Linear, renameChildren=True)[0]
    curve2Degree = mc.rename(curve2Degree, f'{limbName}Degree2_CRV')
       
    mc.rebuildCurve(curve2Degree, s=2, d=2, kr=0, kep=True, kt=False, kcp=False)
    curve2DegreeShape = mc.listRelatives(curve2Degree, shapes=True)[0]
     
    curvatureUpperLOC = mc.spaceLocator(n=f'{limbName}curvatureUpper_LOC')[0]
    cv_positionA = mc.xform(curveBezier + ".cv[2]", query=True, worldSpace=True, translation=True)
    mc.xform(curvatureUpperLOC, worldSpace=True, translation=cv_positionA)
    curvatureLowerLOC = mc.spaceLocator(n=f'{limbName}curvatureLower_LOC')[0]
    cv_positionB = mc.xform(curveBezier + ".cv[4]", query=True, worldSpace=True, translation=True)
    mc.xform(curvatureLowerLOC, worldSpace=True, translation=cv_positionB)
    curvatureMidLOC = mc.spaceLocator(n=f'{limbName}curvatureMid_LOC')[0]
    cv_positionC = mc.xform(curveBezier + ".cv[3]", query=True, worldSpace=True, translation=True)
    mc.xform(curvatureMidLOC, worldSpace=True, translation=cv_positionC)
    
    curvatureUpperCVLOC = mc.duplicate(curvatureUpperLOC)
    curvatureUpperCVLOC = mc.rename(curvatureUpperCVLOC, f'{limbName}curvatureUpperCV_LOC')
    curvatureLowerCVLOC = mc.duplicate(curvatureLowerLOC)
    curvatureLowerCVLOC = mc.rename(curvatureLowerCVLOC, f'{limbName}curvatureLowerCV_LOC')

    #Important to parent before connecting curvature 
    mc.parent(curvatureUpperLOC, curvatureMidLOC)
    mc.parent(curvatureLowerLOC, curvatureMidLOC)
    
    mc.pointConstraint(curvatureUpperLOC,curvatureUpperCVLOC, o=[0,0,0], mo=False)
    mc.pointConstraint(curvatureLowerLOC,curvatureLowerCVLOC, o=[0,0,0], mo=False)
    
    mc.connectAttr(controlName + '.curvature', curvatureMidLOC + '.scaleX')
    mc.connectAttr(controlName + '.curvature', curvatureMidLOC + '.scaleY')
    mc.connectAttr(controlName + '.curvature', curvatureMidLOC + '.scaleZ')

    limbCurvatureCV01DCM = mc.createNode('decomposeMatrix', name=f'{limbName}CurvatureCV01DCM')
    mc.connectAttr(listJoints[0][0] + '.worldMatrix[0]', limbCurvatureCV01DCM + '.inputMatrix')
    mc.connectAttr(limbCurvatureCV01DCM + '.outputTranslate', curve2DegreeShape + '.controlPoints[0]')

    limbCurvatureCV02DCM = mc.createNode('decomposeMatrix', name=f'{limbName}CurvatureCV02DCM')
    mc.connectAttr(curvatureUpperCVLOC + '.worldMatrix[0]', limbCurvatureCV02DCM + '.inputMatrix')
    mc.connectAttr(limbCurvatureCV02DCM + '.outputTranslate', curve2DegreeShape + '.controlPoints[1]')

    limbCurvatureCV03DCM = mc.createNode('decomposeMatrix', name=f'{limbName}CurvatureCV03DCM')
    mc.connectAttr(curvatureLowerCVLOC + '.worldMatrix[0]', limbCurvatureCV03DCM + '.inputMatrix')
    mc.connectAttr(limbCurvatureCV03DCM + '.outputTranslate', curve2DegreeShape + '.controlPoints[2]')

    limbCurvatureCV04DCM = mc.createNode('decomposeMatrix', name=f'{limbName}CurvatureCV04DCM')
    mc.connectAttr(listJoints[0][2] + '.worldMatrix[0]', limbCurvatureCV04DCM + '.inputMatrix')
    mc.connectAttr(limbCurvatureCV04DCM + '.outputTranslate', curve2DegreeShape + '.controlPoints[3]')
    
    mc.pointConstraint(listJoints[0][1],curvatureMidLOC, o=[0,0,0], mo=False)
    #VERIFIED
    mc.parent(curvatureUpperLOC, world=True)
    mc.parent(curvatureLowerLOC, world=True)

    tempConstraint = mc.orientConstraint(listJoints[0][0], listJoints[0][1], curvatureMidLOC)[0]
    mc.setAttr(tempConstraint + '.interpType', 2)

    mc.matchTransform(curvatureUpperLOC, curvatureMidLOC, pos=False, rot=True, scl=False)
    mc.matchTransform(curvatureLowerLOC, curvatureMidLOC, pos=False, rot=True, scl=False)

    mc.parent(curvatureUpperLOC, curvatureMidLOC)
    mc.parent(curvatureLowerLOC, curvatureMidLOC)

    mc.delete(curve1Linear,curveBezier)
    mc.group(curve2Degree, curvatureMidLOC, curvatureUpperCVLOC, curvatureLowerCVLOC, n= f'{limbName}Curvature_GRP')

    return curve2Degree


def generateIKPVPinNodes(listJoints, listControls,lastGroup, IKSoftCON, limbName):
    IKlimbUpperPinDBT = mc.createNode('distanceBetween', n=f'IK_{limbName}UpperPinDBT')
    mc.connectAttr(listControls[2] + '.worldMatrix[0]', IKlimbUpperPinDBT + '.inMatrix1')
    mc.connectAttr(listControls[1] + '.worldMatrix[0]', IKlimbUpperPinDBT + '.inMatrix2')

    IKlimbLowerPinDBT = mc.createNode('distanceBetween', n=f'IK_{limbName}LowerPinDBT')
    mc.connectAttr(listControls[1] + '.worldMatrix[0]', IKlimbLowerPinDBT + '.inMatrix1')
    mc.connectAttr(lastGroup + '.worldMatrix[0]', IKlimbLowerPinDBT + '.inMatrix2')

    IKlimbUpperPinBTA = mc.createNode('blendTwoAttr', n=f'IK_{limbName}UpperPinBTA')
    mc.connectAttr(listControls[1] + '.pin', IKlimbUpperPinBTA + '.attributesBlender')
    mc.connectAttr(IKSoftCON + '.outColorG', IKlimbUpperPinBTA + '.input[0]')
    mc.connectAttr(IKlimbUpperPinDBT + '.distance', IKlimbUpperPinBTA + '.input[1]')

    IKlimbLowerPinBTA = mc.createNode('blendTwoAttr', n=f'IK_{limbName}UpperPinBTA')
    mc.connectAttr(listControls[1] + '.pin', IKlimbLowerPinBTA + '.attributesBlender')
    mc.connectAttr(IKSoftCON + '.outColorB', IKlimbLowerPinBTA + '.input[0]')
    mc.connectAttr(IKlimbLowerPinDBT + '.distance', IKlimbLowerPinBTA + '.input[1]')

    mc.disconnectAttr(IKSoftCON + '.outColorG', listJoints[1][1] + '.translateX')
    mc.disconnectAttr(IKSoftCON + '.outColorB', listJoints[1][2] + '.translateX')

    mc.connectAttr(IKlimbUpperPinBTA + '.output', listJoints[1][1] + '.translateX')
    mc.connectAttr(IKlimbLowerPinBTA + '.output', listJoints[1][2] + '.translateX')

    

def generateIKSoftNodes(listJoints, listControls, ikHandle, tempConstraint, IKStrCON, limbName):

    IKupperLenFLM = mc.createNode('floatMath', n=f'IK_{limbName}upperLenFLM')
    IKlowerLenFLM = mc.createNode('floatMath', n=f'IK_{limbName}lowerLenFLM')
    IKlimbFullLenFLM = mc.createNode('floatMath', n=f'IK_{limbName}FullLenFLM')
    mc.setAttr(IKupperLenFLM + '.operation', 2) #MULTIPLY
    mc.setAttr(IKlowerLenFLM + '.operation', 2) #MULTIPLY
    mc.setAttr(IKlimbFullLenFLM + '.operation', 0) #ADD
    mc.connectAttr(listControls[0] + '.upperLenMult', IKupperLenFLM + '.floatA')
    mc.connectAttr(listControls[0] + '.lowerLenMult', IKlowerLenFLM + '.floatA')

    translateA = mc.getAttr(f"{listJoints[1][1]}.translateX")
    translateB = mc.getAttr(f"{listJoints[1][2]}.translateX")
    mc.setAttr(IKupperLenFLM + '.floatB', translateA)
    mc.setAttr(IKlowerLenFLM + '.floatB', translateB)
    mc.connectAttr(IKupperLenFLM + '.outFloat', IKlimbFullLenFLM + '.floatA')
    mc.connectAttr(IKlowerLenFLM + '.outFloat', IKlimbFullLenFLM + '.floatB')
  
    IKlimbDisToCTLDBT = mc.createNode('distanceBetween', n=f'IK_{limbName}DisToCTLDBT')
    mc.connectAttr(listControls[2] + '.worldMatrix[0]', IKlimbDisToCTLDBT + '.inMatrix1')
    mc.connectAttr(listControls[0] + '.worldMatrix[0]', IKlimbDisToCTLDBT + '.inMatrix2')

    IKlimbDisToCTLNormalFML = floatMConnect(f'IK_{limbName}DisToCTLNormalFML', 3, IKlimbDisToCTLDBT + '.distance', None)
    mc.setAttr(IKlimbDisToCTLNormalFML + '.floatB', 1) #materwalk_CTL.globalscale
    
    #Getting the value for limbSotfValueRMV.maxOutput
    valueA = mc.getAttr(IKlimbFullLenFLM + '.outFloat')
    valueB = mc.getAttr(IKlimbDisToCTLDBT + '.distance')


    IKlimbSoftValueRMV = mc.createNode('remapValue', n=f'IK_{limbName}SoftValueRMV')
    mc.connectAttr(listControls[0] + '.soft', IKlimbSoftValueRMV + '.inputValue')
    mc.setAttr(IKlimbSoftValueRMV + '.outputMin', 0.001)
    mc.setAttr(IKlimbSoftValueRMV + '.inputMax', 1.0)
    mc.setAttr(IKlimbSoftValueRMV + '.outputMax', valueA - valueB)
    

    IKlimbSoftDisFLM = floatMConnect(f'IK_{limbName}SoftDisFLM', 1, IKlimbFullLenFLM + '.outFloat', IKlimbSoftValueRMV + '.outValue')
    IKlimbDisToCTLMinSDisFLM = floatMConnect(f'IK_{limbName}DisToCTLMinSDisFLM', 1, IKlimbDisToCTLNormalFML + '.outFloat', IKlimbSoftDisFLM + '.outFloat')
    IKlimbDisToCTLMinSDisDivSoftFLM = floatMConnect(f'IK_{limbName}DisToCTLMinSDisDivSoftFLM', 3, IKlimbDisToCTLMinSDisFLM + '.outFloat', IKlimbSoftValueRMV + '.outValue')

    IKminusCalculateFLM = floatMConnect(f'IK_{limbName}minusCalculateFLM', 2, IKlimbDisToCTLMinSDisDivSoftFLM + '.outFloat', None)
    mc.setAttr(IKminusCalculateFLM + '.floatB', -1.0)

    IKlimbSoftEPowerFML = floatMConnect(f'IK_{limbName}SoftEPowerFML', 6, None, IKminusCalculateFLM + '.outFloat')
    mc.setAttr(IKlimbSoftEPowerFML + '.floatA', math.e)
    
    IKlimbSoftOneMinusEPowerFML = floatMConnect(f'IK_{limbName}SoftOneMinusEPowerFML', 1, None, IKlimbSoftEPowerFML + '.outFloat')
    mc.setAttr(IKlimbSoftOneMinusEPowerFML + '.floatA', 1)
    
    IKlimbCalculateSoftValueMultFML = floatMConnect(f'IK_{limbName}CalculateSoftValueMultFML', 2, IKlimbSoftValueRMV + '.outValue', IKlimbSoftOneMinusEPowerFML + '.outFloat')

    # --------------------- RESULT OF THE FIRST FORMULA ------------------------------
    IKlimbSoftConstantFML = floatMConnect(f'IK_{limbName}SoftConstantFML', 0, IKlimbCalculateSoftValueMultFML + '.outFloat', IKlimbSoftDisFLM + '.outFloat')
    
    # --------------------- RESULT OF THE SECOND FORMULA ------------------------------
    IKlimbSoftRatioFML = floatMConnect(f'IK_{limbName}SoftRatioFML', 3, IKlimbSoftConstantFML + '.outFloat', IKlimbFullLenFLM + '.outFloat')
    
    # --------------------- RESULT OF THE THIRD FORMULA ------------------------------
    IKlimbLenRatioFML = floatMConnect(f'IK_{limbName}LenRatioFML', 3, IKlimbDisToCTLNormalFML + '.outFloat', IKlimbFullLenFLM + '.outFloat')

    # --------------------- RESULT OF THE FOURTH FORMULA ------------------------------
    IKlimbDisToCTLDivLenRatioFML = floatMConnect(f'IK_{limbName}DisToCTLDivLenRatioFML', 3, IKlimbDisToCTLNormalFML + '.outFloat', IKlimbLenRatioFML + '.outFloat')
    IKlimbSoftEffectorDisFML = floatMConnect(f'IK_{limbName}SoftEffectorDisFML', 2, IKlimbSoftRatioFML + '.outFloat', IKlimbDisToCTLDivLenRatioFML + '.outFloat')

    
    IKlimbSoftCON = mc.createNode('condition', n=f'IK_{limbName}SoftCON')
    mc.setAttr(IKlimbSoftCON + '.operation', 2) #GREATER THAN
    mc.connectAttr(IKlimbDisToCTLNormalFML + '.outFloat', IKlimbSoftCON + '.firstTerm')
    mc.connectAttr(IKlimbSoftDisFLM + '.outFloat', IKlimbSoftCON + '.secondTerm')
    mc.connectAttr(IKlimbSoftEffectorDisFML + '.outFloat', IKlimbSoftCON + '.colorIfTrueR')
    mc.connectAttr(IKlimbDisToCTLNormalFML + '.outFloat', IKlimbSoftCON + '.colorIfFalseR')

    
    lastGroup = create.createGroupStructure('OFF;TRN',f'IK_{limbName}Soft', None)
    mainGroup = f'IK_{limbName}Soft_OFF'
    mc.matchTransform(mainGroup, listJoints[1][0])
    
    mc.aimConstraint(listControls[0], mainGroup, o=[0,0,0], aim=[1,0,0], wut="none")
    
    mc.connectAttr(IKlimbSoftCON + '.outColorR', lastGroup + '.translateX')

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
    IKlimbDisToCTLDivSEffectorFML = floatMConnect(f'IK_{limbName}DisToCTLDivSEffectorFML', 3, IKlimbDisToCTLNormalFML + '.outFloat', IKlimbSoftEffectorDisFML + '.outFloat')
    IKlimbDisToCTLDivSEffectorMinusFML = floatMConnect(f'IK_{limbName}DisToCTLDivSEffectorMinusFML', 1, IKlimbDisToCTLDivSEffectorFML + '.outFloat', None)
    mc.setAttr(IKlimbDisToCTLDivSEffectorMinusFML + '.floatB', 1.0)

    IKlimbDisToCTLDivSEffectorMultipliedFML = floatMConnect(f'IK_{limbName}DisToCTLDivSEffectorMultipliedFML', 2, IKlimbDisToCTLDivSEffectorMinusFML + '.outFloat', listControls[0] + '.stretch')
    stretchFactorFML = floatMConnect(f'IK_{limbName}DisToCTLDivSEffectorMultipliedFML', 0, IKlimbDisToCTLDivSEffectorMinusFML + '.outFloat', None)
    mc.setAttr(stretchFactorFML + '.floatB', 1.0)

    IKlimbSoftEffStretchDisFML = floatMConnect(f'IK_{limbName}SoftEffStretchDisFML', 2, IKlimbSoftEffectorDisFML + '.outFloat', stretchFactorFML + '.outFloat')

    IKlimbUpperLenStretchFLM = floatMConnect(f'IK_{limbName}UpperLenStretchFLM', 2, IKupperLenFLM + '.outFloat', stretchFactorFML + '.outFloat')
    IKlimbLowerLenStretchFLM = floatMConnect(f'IK_{limbName}LowerLenStretchFLM', 2, IKlowerLenFLM + '.outFloat', stretchFactorFML + '.outFloat')

    mc.disconnectAttr(IKlimbSoftEffectorDisFML + '.outFloat', IKlimbSoftCON + '.colorIfTrueR')
    mc.connectAttr(IKlimbSoftEffStretchDisFML + '.outFloat', IKlimbSoftCON + '.colorIfTrueR')
    mc.connectAttr(IKlimbUpperLenStretchFLM + '.outFloat', IKlimbSoftCON + '.colorIfTrueG')
    mc.connectAttr(IKlimbLowerLenStretchFLM + '.outFloat', IKlimbSoftCON + '.colorIfTrueB')

    mc.connectAttr(IKupperLenFLM + '.outFloat', IKlimbSoftCON + '.colorIfFalseG')
    mc.connectAttr(IKlowerLenFLM + '.outFloat', IKlimbSoftCON + '.colorIfFalseB')

    mc.disconnectAttr(IKStrCON + '.outColorR', listJoints[1][1] + '.translateX')
    mc.disconnectAttr(IKStrCON + '.outColorG', listJoints[1][2] + '.translateX')

    mc.connectAttr(IKlimbSoftCON + '.outColorG', listJoints[1][1] + '.translateX')
    mc.connectAttr(IKlimbSoftCON + '.outColorB', listJoints[1][2] + '.translateX')

    return IKlimbSoftCON, lastGroup


def generateIKStretchNodes(listJoints, listControls, limbName):
    limbLenDBT = mc.createNode('distanceBetween', n=f'IK_{limbName}LenDBT')
    mc.connectAttr(listControls[2] + '.worldMatrix[0]', limbLenDBT + '.inMatrix1')
    mc.connectAttr(listControls[0] + '.worldMatrix[0]', limbLenDBT + '.inMatrix2')

    limbRelDistanceFLM = mc.createNode('floatMath', n=f'IK_{limbName}RelDistanceFLM')
    mc.setAttr(limbRelDistanceFLM + '.operation', 3)
    mc.connectAttr(limbLenDBT + '.distance', limbRelDistanceFLM + '.floatA')

    upperLenMultMDL = mc.createNode('multDoubleLinear', n='IK_upperLenMultMDL')
    lowerLenMultMDL = mc.createNode('multDoubleLinear', n='IK_lowerLenMultMDL')
    mc.connectAttr(listControls[0] + '.upperLenMult', upperLenMultMDL + '.input1')
    mc.connectAttr(listControls[0] + '.lowerLenMult', lowerLenMultMDL + '.input1')
    distanceA = mc.getAttr(f"{listJoints[1][1]}.translateX")
    distanceB = mc.getAttr(f"{listJoints[1][2]}.translateX")
    mc.setAttr(upperLenMultMDL + '.input2', distanceA)
    mc.setAttr(lowerLenMultMDL + '.input2', distanceB)

    limbDistanceRatioFLM = mc.createNode('floatMath', n=f'IK_{limbName}DistanceRatioFLM')
    mc.setAttr(limbDistanceRatioFLM + '.operation', 3)
    mc.connectAttr(limbRelDistanceFLM + '.outFloat', limbDistanceRatioFLM + '.floatA')

    limbFullLenADL = mc.createNode('addDoubleLinear', n=f'IK_{limbName}FullLenADL')
    mc.connectAttr(upperLenMultMDL + '.output', limbFullLenADL + '.input1')
    mc.connectAttr(lowerLenMultMDL + '.output', limbFullLenADL + '.input2')
    mc.connectAttr(limbFullLenADL + '.output', limbDistanceRatioFLM + '.floatB')

    upperLenMultStrMDL = mc.createNode('multDoubleLinear', n='IK_upperLenMultStrMDL')
    lowerLenMultStrMDL = mc.createNode('multDoubleLinear', n='IK_lowerLenMultStrMDL')
    mc.connectAttr(upperLenMultMDL + '.output', upperLenMultStrMDL + '.input1')
    mc.connectAttr(limbDistanceRatioFLM + '.outFloat', upperLenMultStrMDL + '.input2')
    mc.connectAttr(lowerLenMultMDL + '.output', lowerLenMultStrMDL + '.input1')
    mc.connectAttr(limbDistanceRatioFLM + '.outFloat', lowerLenMultStrMDL + '.input2')


    upperLenStrBTA = mc.createNode('blendTwoAttr', n='IK_upperLenStrBTA')
    lowerLenStrBTA = mc.createNode('blendTwoAttr', n='IK_lowerLenStrBTA')
    mc.connectAttr(listControls[0] + '.stretch', upperLenStrBTA + '.attributesBlender')
    mc.connectAttr(upperLenMultMDL + '.output', upperLenStrBTA + '.input[0]')
    mc.connectAttr(upperLenMultStrMDL + '.output', upperLenStrBTA + '.input[1]')
    mc.connectAttr(listControls[0] + '.stretch', lowerLenStrBTA + '.attributesBlender')
    mc.connectAttr(lowerLenMultMDL + '.output', lowerLenStrBTA + '.input[0]')
    mc.connectAttr(lowerLenMultStrMDL + '.output', lowerLenStrBTA + '.input[1]')

    limbStrCON = mc.createNode('condition', n=f'IK_{limbName}StrCON')
    mc.setAttr(limbStrCON + '.operation', 2)
    mc.connectAttr(limbRelDistanceFLM + '.outFloat', limbStrCON + '.firstTerm')
    mc.setAttr(limbStrCON + '.secondTerm', 1.0)

    mc.connectAttr(upperLenMultMDL + '.output', limbStrCON + '.colorIfFalseR')
    mc.connectAttr(lowerLenMultMDL + '.output', limbStrCON + '.colorIfFalseG')
    mc.connectAttr(upperLenStrBTA + '.output', limbStrCON + '.colorIfTrueR')
    mc.connectAttr(lowerLenStrBTA + '.output', limbStrCON + '.colorIfTrueG')

    mc.connectAttr(limbStrCON + '.outColorR', listJoints[1][1] + '.translateX')
    mc.connectAttr(limbStrCON + '.outColorG', listJoints[1][2] + '.translateX')

    return limbStrCON

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

def createTwistStructure(jointsList, part, typePop):
    NonRollJoints = mc.duplicate(jointsList, renameChildren=True)

    if typePop == 'end':
        popNum = len(NonRollJoints)-1
        mc.delete(NonRollJoints[popNum])
        NonRollJoints.pop(popNum)
        
    elif typePop == 'root':
        mc.parent(NonRollJoints[1], world=True)
        mc.delete(NonRollJoints[0])
        NonRollJoints.pop(0)
        
    NonRollJoints[0] = mc.rename(NonRollJoints[0], f'{part}NonRoll01_JNT')
    NonRollJoints[1] = mc.rename(NonRollJoints[1], f'{part}NonRoll02_JNT')
    mc.setAttr(NonRollJoints[1] + ".jointOrientX", 0)
    mc.setAttr(NonRollJoints[1] + ".jointOrientY", 0)
    mc.setAttr(NonRollJoints[1] + ".jointOrientZ", 0)

    RollJoints = mc.duplicate(NonRollJoints, renameChildren=True)
    RollJoints[0] = mc.rename(RollJoints[0], f'{part}Roll01_JNT')
    RollJoints[1] = mc.rename(RollJoints[1], f'{part}Roll02_JNT')

    limbUpperNonRollHDL = mc.ikHandle(name=f'{part}NonRoll_HDL', sol='ikSCsolver', sj=NonRollJoints[0], ee=NonRollJoints[1])[0]
    limbUpperRollHDL = mc.ikHandle(name=f'{part}Roll_HDL', sol='ikSCsolver', sj=RollJoints[0], ee=RollJoints[1])[0]
    

    mc.pointConstraint(jointsList[1], limbUpperNonRollHDL)
    mc.parentConstraint(jointsList[1], limbUpperRollHDL, mo=True)
    mc.parent(RollJoints[0],NonRollJoints[0])

    return NonRollJoints, RollJoints

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


def createFloatConstant(valuesList):
    nodeList = []

    for i in range(len(valuesList)):
        node = mc.createNode('floatConstant')
        nodeList.append(node)
        mc.setAttr(node + '.inFloat', valuesList[i])
    print(nodeList)
    return nodeList

def createMPACurveJNT(length, mainName, shape, floatConstant):
    nodesMPA = []
    for i in range(length):
        mainNameC = mainName + str(i+1)
        node =  mc.createNode('motionPath', n= mainNameC + "MPA")
        nodesMPA.append(node)
        mc.connectAttr(shape + '.worldSpace[0]', node + '.geometryPath')
        mc.setAttr(node + ".fractionMode", True) #parametric length opposite -- BUG
        mc.setAttr(node + ".upAxis", 1)
        mc.setAttr(node + ".frontAxis", 0)

        '''valueTwist = i/(length-1)
        
        if valueTwist == 0:
            valueTwist = 0.0001
        elif valueTwist == 1:
            valueTwist = 0.9999
            
        mc.setAttr(node + ".uValue", valueTwist)'''

        mc.connectAttr(floatConstant[i] + '.outFloat', node + '.uValue')
        
        joint = mc.joint(n= mainNameC + '_JNT')
        mc.connectAttr(node + '.allCoordinates', joint + '.translate')
        mc.connectAttr(node + '.rotate', joint + '.rotate')
    
    return nodesMPA

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