import maya.cmds as mc
import maya.mel as mel
import ElementsUI as elUI
import util
import math

limbLocators = []
limbJoints = []


def page(mainWidth, mainHeight):

    child = mc.columnLayout()
    mc.frameLayout(label='Structure', collapsable=True, collapse=False, marginWidth=5, marginHeight=5)
    mc.button(l='Generate Structure', c= lambda _: util.rigging.createStructureClass())

    mc.rowLayout(nc=3)
    mc.textField('structureTXT', w=mainWidth/2, tx='GRP;ANM;OFFSET')
    mc.button(l='Create Groups', w=90, c= lambda _: createCTLStructure())
    mc.setParent('..') # End rowLayout

    mc.textField('structureNameTXT', w=mainWidth/2, placeholderText='Leave empty to use first selection name')
    armSectionWidth = mainWidth/4
    mc.setParent('..') # End frameLayout
    mc.frameLayout(label='Limbs', collapsable=False, collapse=False, marginWidth=5, marginHeight=5)
    mc.rowLayout(nc=2, cal=([1,'left'],[2,'center']), cw=[(1, armSectionWidth), (2, armSectionWidth/2)])
    mc.text(l='Create Locators: ')
    mc.button('limbLocButton', l='GO', c=lambda _: createLocatorLimb())
    mc.setParent('..') # End rowLayout

    elUI.separatorTitleUI('Features',5,20,mainWidth/2-50)

    mc.rowColumnLayout(nc=2, cal=([1,'left'],[2,'center']), cw=[(1, armSectionWidth), (2, armSectionWidth/2)])
    mc.text(l='IK/FK')
    mc.checkBox('featLimbIKFK', l='', en=False, cc=limbFeatIKFKChanged)
    mc.text(l='Stretch')
    mc.checkBox('featLimbStretch', l='', en=False, cc=limbFeatStretchChanged)
    mc.text(l='Soft')
    mc.checkBox('featLimbSoft', l='', en=False, cc=limbFeatSoftChanged)
    mc.text(l='PV Pin')
    mc.checkBox('featLimbPVPin', l='', en=False)
    mc.text(l='Curvature')
    mc.checkBox('featLimbCurv', l='', en=False)
    mc.setParent('..') # End rowColumnLayout

    mc.rowColumnLayout(nc=2, cal=([1,'left'],[2,'center']), cw=[(1, armSectionWidth), (2, armSectionWidth/2)])
    mc.text(l='Create Joints: ')
    mc.button('limbCreateButton', l='GO', c=lambda _: createLimbJoints(), en=False)
    mc.setParent('..') # End rowColumnLayout
    mc.button('limbResetButton', l='Restart', c=lambda _: restartLimbChain(), en=False)
    
    mc.setParent('..') # End frameLayout
    mc.setParent( '..' ) # End columnLayout  
    return child

def limbFeatIKFKChanged(*args):
    if mc.checkBox('featArmIKFK', query=True, value=True):
        util.select.modifyCheckBoxList(['featLimbStretch', 'featLimbCurv'], False, True)
    else:
        util.select.modifyCheckBoxList(['featLimbStretch', 'featLimbSoft', 'featLimbPVPin', 'featLimbCurv'], False, False)

def limbFeatStretchChanged(*args):
    if mc.checkBox('featLimbStretch', query=True, value=True):
        util.select.modifyCheckBoxList(['featLimbSoft'], False, True)
    else:
        util.select.modifyCheckBoxList(['featLimbSoft', 'featLimbPVPin'], False, False)

def limbFeatSoftChanged(*args):
    if mc.checkBox('featLimbSoft', query=True, value=True):
        util.select.modifyCheckBoxList(['featLimbPVPin'], False, True)
    else:
        util.select.modifyCheckBoxList(['featLimbPVPin'], False, False)

def createLocatorLimb():
    global limbLocators
    limbLocators = util.rigging.createLocatorLimb()
    mc.button('limbLocButton', e=True, en=False)
    util.select.modifyCheckBoxList(['featLimbIKFK'], True, True)
    util.select.modifyCheckBoxList(['featLimbStretch', 'featLimbCurv'], False, True)
    util.select.modifyButtonList(['limbCreateButton','limbResetButton'], True)

    util.select.setfocusMaya()


def createLimbJoints():
    global limbJoints
    groupStructure = 'GRP;ANIM;OFFSET'
    firstGroup = groupStructure.split(';')[0]

    stretch = mc.checkBox('featLimbStretch', q=True, v=True)
    soft =  mc.checkBox('featLimbSoft', q=True, v=True)
    pvPin = mc.checkBox('featLimbPVPin', q=True, v=True)
    curvature = mc.checkBox('featLimbCurv', q=True, v=True)
    twist = False

    limbName = 'test'

    #Create arms and duplicate to IK and FK
    limbJoints.append(util.rigging.createLimbChain(limbLocators))

    # ----------------------------------------------------------------------
    # --------------------------- CREATE IK ARM ----------------------------
    # ----------------------------------------------------------------------
    
    limbJoints.append(util.rigging.copyJoints(limbJoints[0],'IK'))
    ikHandle = mc.ikHandle(n='IK_Arm_HDL', sj=limbJoints[1][0], ee=limbJoints[1][2], sol='ikRPsolver')[0] 
    listControlsIK = util.rigging.createIkCTLJointList(ikHandle, limbJoints[1][1] ,groupStructure)
    
    tempConstraint = mc.parentConstraint(listControlsIK[0], ikHandle, mo=True, w=1)
    mc.poleVectorConstraint(listControlsIK[1], ikHandle)
    mc.orientConstraint( listControlsIK[0], limbJoints[1][2], mo=True)

    #Create groups and parent it. ALSO move PV Control to a position inside the plane
    lastGroup = util.create.createGroupStructure(groupStructure,'IK_Arm_Controls',None)
    util.rigging.movePVControl(limbJoints[1], 'IK_Arm_PV_' + firstGroup, 4)
    mc.parent('IK_Arm_' + firstGroup, lastGroup)
    mc.parent('IK_Arm_PV_' + firstGroup, lastGroup)

    # ----------------------------------------------------------------------
    # --------------------------- STRETCH IK -------------------------------
    # ----------------------------------------------------------------------

    if stretch:
        mc.select(listControlsIK[0])
        mc.addAttr(longName='upperLenMult', niceName= 'Upper Length Mult', attributeType="float", dv=1, min=0.001, h=False, k=True)
        mc.addAttr(longName='lowerLenMult', niceName= 'Lower Length Mult', attributeType="float", dv=1, min=0.001, h=False, k=True)
        mc.addAttr(longName='stretch', niceName= 'Stretch', attributeType="float", dv=0, min=0, max=1, h=False, k=True)

        listControlsIK.append(util.rigging.createCTLJointList([limbJoints[1][0]],groupStructure)[0])
        tempName = util.naming.modifyName('replace',limbJoints[1][0],'_JNT','')
        tempRoot = tempName + '_' + firstGroup
        mc.parent(tempRoot, lastGroup)
        mc.parentConstraint(listControlsIK[2], limbJoints[1][0], sr=["x","z","y"], w=1)

        # ------------------------------ NODES ----------------------------------
        IKlimbStrCON = util.rigging.generateIKStretchNodes(limbJoints, listControlsIK)

        if soft:
            # ----------------------------------------------------------------------
            # ----------------------------- SOFT IK -------------------------------- # DEPENDS FROM STRETCH IK 
            # ----------------------------------------------------------------------
            mc.select(listControlsIK[0]) 
            mc.addAttr(longName='soft', niceName= 'Soft' , attributeType="float", dv=0, min=0, max=1, h=False, k=True)
            
            # ------------------------------ NODES ----------------------------------
            
            IKarmSoftCON, lastGroup = util.rigging.generateIKSoftNodes(limbJoints, listControlsIK, ikHandle, tempConstraint, IKlimbStrCON)
        
            # ----------------------------------------------------------------------
            # ----------------------------- PV PIN -------------------------------- # DEPENDS FROM SOFT IK
            # ----------------------------------------------------------------------
            if pvPin:
                mc.select(listControlsIK[1])
                mc.addAttr(longName='pin', niceName= 'Pin', attributeType="float", dv=0, min=0, max=1, h=False, k=True)

                util.rigging.generateIKPVPinNodes(limbJoints, listControlsIK, lastGroup, IKarmSoftCON, limbName)
    

    # ----------------------------------------------------------------------
    # --------------------------- CREATE FK ARM ----------------------------
    # ----------------------------------------------------------------------

    #Create FK ARM Chain with all Groups
    limbJoints.append(util.rigging.copyJoints(limbJoints[0],'FK'))
    listControlsFK = util.rigging.createCTLJointList(limbJoints[2],groupStructure)
    util.rigging.parentControlJoints(listControlsFK,limbJoints[2])
    tempName = util.naming.modifyName('replace',limbJoints[2][0],'_JNT','')
    tempRoot = tempName + '_' + firstGroup
    lastGroup = util.create.createGroupStructure(groupStructure,'FK_Arm_Controls',None)
    mc.parent(tempRoot, lastGroup)

    # ----------------------------------------------------------------------
    # --------------------------- STRETCH FK -------------------------------
    # ----------------------------------------------------------------------
    if stretch:
        mc.select(listControlsFK[0])
        mc.addAttr(longName='stretch', niceName= 'Stretch' , attributeType="float", dv=1, min=0.001, h=False, k=True)
        mc.select(listControlsFK[1])
        mc.addAttr(longName='stretch', niceName= 'Stretch' , attributeType="float", dv=1, min=0.001, h=False, k=True)

        FKupperLenMultMDL = mc.createNode('multDoubleLinear', n='FK_upperLenMultMDL')
        FKlowerLenMultMDL = mc.createNode('multDoubleLinear', n='FK_lowerLenMultMDL')
        mc.connectAttr(listControlsFK[0] + '.stretch', FKupperLenMultMDL + '.input1')
        mc.connectAttr(listControlsFK[1] + '.stretch', FKlowerLenMultMDL + '.input1')
        distanceA = mc.getAttr(f"{limbJoints[2][1]}.translateX")
        distanceB = mc.getAttr(f"{limbJoints[2][2]}.translateX")
        mc.setAttr(FKupperLenMultMDL + '.input2', distanceA)
        mc.setAttr(FKlowerLenMultMDL + '.input2', distanceB)

        fkShoulderGroup = util.naming.modifyName('replace',limbJoints[2][1], '_JNT','')
        fkElbowGroup = util.naming.modifyName('replace',limbJoints[2][2], '_JNT','')

        mc.connectAttr(FKupperLenMultMDL + '.output', fkShoulderGroup + '_' + firstGroup + '.translateX')
        mc.connectAttr(FKlowerLenMultMDL + '.output', fkElbowGroup + '_' + firstGroup + '.translateX')

    # ----------------------------------------------------------------------
    # --------------------------- PREFERENCES ------------------------------
    # ----------------------------------------------------------------------
    controlName = 'Arm_Preferences_CTL'
    lastGroup = util.create.createGroupStructure(groupStructure,'Arm_Preferences_Controls',None)
    util.create.createTextCurves('Switch')
    selection = mc.ls(sl=True)[0]
    mc.parent(selection, lastGroup)
    mc.rename(selection, controlName)
    
    tempGroup = 'Arm_Preferences_Controls_' + firstGroup
    mc.matchTransform(tempGroup, limbJoints[0][0], pos=True)
    mc.move(0, 4, 0, tempGroup, relative=True)

    #Add attribute and visibility with controls
    mc.select(controlName)
    mc.addAttr( longName='switchIKFK', niceName= 'Switch IK / FK' , attributeType="float", dv=0, max=1, min=0, h=False, k=True)
    mc.connectAttr(f"{controlName}.switchIKFK", "FK_Arm_Controls_" + firstGroup + ".visibility", force=True)
    reverseNode = mc.createNode('reverse', name="Arm_switchIKFK_REVERSE") 
    mc.connectAttr(f"{controlName}.switchIKFK", f"{reverseNode}.inputX", force=True)
    mc.connectAttr(f"{reverseNode}.outputX", "IK_Arm_Controls_" + firstGroup + ".visibility", force=True)

    # ----------------------------------------------------------------------
    # --------------------------- PAIR BLENDS ------------------------------
    # ----------------------------------------------------------------------
    for i in range(len(limbJoints[0])):
        pbNode = util.rigging.createPB(limbJoints[0][i], limbJoints[1][i], limbJoints[2][i], True, True)
        mc.connectAttr(f"{controlName}.switchIKFK", f"{pbNode}.weight", force=True)

    
    # ----------------------------------------------------------------------
    # ---------------------------- CURVATURE ------------------------------- 
    # ----------------------------------------------------------------------
    if curvature:
        mc.select(controlName)
        mc.addAttr(longName='curvature', niceName= 'Curvature' , attributeType="float", dv=0, max=1, min=0, h=False, k=True)
        curve2Degree = util.rigging.generateCurvatureNodes(limbJoints, controlName, limbName)

    # ----------------------------------------------------------------------
    # ------------------------------ TWIST --------------------------------- 
    # ----------------------------------------------------------------------
    if twist:
        detachCurve = mc.detachCurve(curve2Degree, p=0.5, rpo=False, ch=True) #Important to keep the ch
        armUpperSegCRV = detachCurve[0]
        armLowerSegCRV = detachCurve[1]
        armUpperSegCRV = mc.rename(armUpperSegCRV, 'armUpperSeg_CRV')
        armLowerSegCRV = mc.rename(armLowerSegCRV, 'armLowerSeg_CRV')
        armUpperSegCRVShape = mc.listRelatives(armUpperSegCRV, shapes=True)[0]
        rangeTwist = 5
        
        nodeFCList = util.rigging.createFloatConstant([0.001, 0.25, 0.5, 0.75, 0.999])
        
        #TODO add a parent to NonRoll01 --> driver is joint01 Original

        armUpperMPANodes = util.rigging.createMPACurveJNT(rangeTwist, 'armUpperTwist0', armUpperSegCRVShape, nodeFCList)
        armUpperNonRollJoints, armUpperRollJoints = util.rigging.createTwistStructure(limbJoints[0], 'armUpper', 'end')

        for i in range(len(armUpperMPANodes)):
            mc.setAttr(armUpperMPANodes[i] + ".worldUpType", 2)
            mc.connectAttr(armUpperNonRollJoints[0]+'.worldMatrix[0]', armUpperMPANodes[i] + ".worldUpMatrix")

            node = util.rigging.floatMConnect(f'armUpper{i+1}FLM', 2, nodeFCList[i] + '.outFloat', armUpperRollJoints[0] +'.rotateX')
            mc.connectAttr(node + ".outFloat", armUpperMPANodes[i] + '.frontTwist')



    # ----------------------------------------------------------------------
    # ------------------------------- FINAL -------------------------------- 
    # ----------------------------------------------------------------------

    #Disable button
    mc.button('limbCreateButton', e=True, en=False)
    print(limbJoints)
    util.select.setfocusMaya()


def restartLimbChain():
    global limbLocators
    global limbJoints
    limbLocators = []
    limbJoints = []
    mc.button('limbLocButton', e=True, en=True)
    util.select.modifyButtonList(['limbCreateButton','limbResetButton'], False)
    util.select.modifyCheckBoxList(['featLimbIKFK', 'featLimbStretch', 'featLimbSoft', 'featLimbPVPin', 'featLimbCurv'], False, False)

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