import maya.cmds as mc
import maya.mel as mel
import ElementsUI as elUI
import util
import math

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

    stretch = False
    soft = False
    pvPin = False
    curvature = True

    #Create arms and duplicate to IK and FK
    armJoints.append(util.rigging.createArmChain(armLocators))

    # ----------------------------------------------------------------------
    # --------------------------- CREATE IK ARM ----------------------------
    # ----------------------------------------------------------------------
    
    armJoints.append(util.rigging.copyJoints(armJoints[0],'IK'))
    ikHandle = mc.ikHandle(n='IK_Arm_HDL', sj=armJoints[1][0], ee=armJoints[1][2], sol='ikRPsolver')[0] 
    listControlsIK = util.rigging.createIkCTLJointList(ikHandle, armJoints[1][1] ,groupStructure)
    
    tempConstraint = mc.parentConstraint(listControlsIK[0], ikHandle, mo=True, w=1)
    mc.poleVectorConstraint(listControlsIK[1], ikHandle)
    mc.orientConstraint( listControlsIK[0], armJoints[1][2], mo=True)

    #Create groups and parent it. ALSO move PV Control to a position inside the plane
    lastGroup = util.create.createGroupStructure(groupStructure,'IK_Arm_Controls',None)
    util.rigging.movePVControl(armJoints[1], 'IK_Arm_PV_' + firstGroup, 4)
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

        listControlsIK.append(util.rigging.createCTLJointList([armJoints[1][0]],groupStructure)[0])
        tempName = util.naming.modifyName('replace',armJoints[1][0],'_JNT','')
        tempRoot = tempName + '_' + firstGroup
        mc.parent(tempRoot, lastGroup)
        mc.parentConstraint(listControlsIK[2], armJoints[1][0], sr=["x","z","y"], w=1)

        # ------------------------------ NODES ----------------------------------
        IKarmStrCON = util.rigging.generateIKStretchNodes(armJoints, listControlsIK)

        if soft:
            # ----------------------------------------------------------------------
            # ----------------------------- SOFT IK -------------------------------- # DEPENDS FROM STRETCH IK 
            # ----------------------------------------------------------------------
            mc.select(listControlsIK[0]) 
            mc.addAttr(longName='soft', niceName= 'Soft' , attributeType="float", dv=0, min=0, max=1, h=False, k=True)
            
            # ------------------------------ NODES ----------------------------------
            
            IKarmSoftCON, lastGroup = util.rigging.generateIKSoftNodes(armJoints, listControlsIK, ikHandle, tempConstraint, IKarmStrCON)
        
            # ----------------------------------------------------------------------
            # ----------------------------- PV PIN -------------------------------- # DEPENDS FROM SOFT IK
            # ----------------------------------------------------------------------
            if pvPin:
                mc.select(listControlsIK[1])
                mc.addAttr(longName='pin', niceName= 'Pin', attributeType="float", dv=0, min=0, max=1, h=False, k=True)

                util.rigging.generateIKPVPinNodes(armJoints, listControlsIK, lastGroup, IKarmSoftCON)
    

    # ----------------------------------------------------------------------
    # --------------------------- CREATE FK ARM ----------------------------
    # ----------------------------------------------------------------------

    #Create FK ARM Chain with all Groups
    armJoints.append(util.rigging.copyJoints(armJoints[0],'FK'))
    listControlsFK = util.rigging.createCTLJointList(armJoints[2],groupStructure)
    util.rigging.parentControlJoints(listControlsFK,armJoints[2])
    tempName = util.naming.modifyName('replace',armJoints[2][0],'_JNT','')
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
        distanceA = mc.getAttr(f"{armJoints[2][1]}.translateX")
        distanceB = mc.getAttr(f"{armJoints[2][2]}.translateX")
        mc.setAttr(FKupperLenMultMDL + '.input2', distanceA)
        mc.setAttr(FKlowerLenMultMDL + '.input2', distanceB)

        fkShoulderGroup = util.naming.modifyName('replace',armJoints[2][1], '_JNT','')
        fkElbowGroup = util.naming.modifyName('replace',armJoints[2][2], '_JNT','')

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
    mc.matchTransform(tempGroup, armJoints[0][0], pos=True)
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
    for i in range(len(armJoints[0])):
        pbNode = util.rigging.createPB(armJoints[0][i], armJoints[1][i], armJoints[2][i], True, True)
        mc.connectAttr(f"{controlName}.switchIKFK", f"{pbNode}.weight", force=True)

    
    # ----------------------------------------------------------------------
    # ---------------------------- CURVATURE ------------------------------- 
    # ----------------------------------------------------------------------
    if curvature:
        mc.select(controlName)
        mc.addAttr(longName='curvature', niceName= 'Curvature' , attributeType="float", dv=0, max=1, min=0, h=False, k=True)
        curve2Degree = util.rigging.generateCurvatureNodes(armJoints, controlName)

    # ----------------------------------------------------------------------
    # ------------------------------ TWIST --------------------------------- 
    # ----------------------------------------------------------------------
    detachCurve = mc.detachCurve(curve2Degree, p=0.5, rpo=False, ch=True) #Important to keep the ch
    armUpperSegCRV = detachCurve[0]
    armLowerSegCRV = detachCurve[1]
    armUpperSegCRV = mc.rename(armUpperSegCRV, 'armUpperSeg_CRV')
    armLowerSegCRV = mc.rename(armLowerSegCRV, 'armLowerSeg_CRV')
    armUpperSegCRVShape = mc.listRelatives(armUpperSegCRV, shapes=True)[0]
    armLowerSegCRVShape = mc.listRelatives(armLowerSegCRV, shapes=True)[0]
    rangeTwist = 5
    
    nodeFCList = util.rigging.createFloatConstant([0.001, 0.25, 0.5, 0.75, 0.999])
    
    #TODO add a parent to NonRoll01 --> driver is joint01 Original


    armUpperMPANodes = util.rigging.createMPACurveJNT(rangeTwist, 'armUpperTwist0', armUpperSegCRVShape, nodeFCList)
    armUpperNonRollJoints, armUpperRollJoints = util.rigging.createTwistStructure(armJoints[0], 'armUpper', 'end')

    for i in range(len(armUpperMPANodes)):
        mc.setAttr(armUpperMPANodes[i] + ".worldUpType", 2)
        mc.connectAttr(armUpperNonRollJoints[0]+'.worldMatrix[0]', armUpperMPANodes[i] + ".worldUpMatrix")

        node = util.rigging.floatMConnect(f'armUpper{i+1}FLM', 2, nodeFCList[i] + '.outFloat', armUpperRollJoints[0] +'.rotateX')
        mc.connectAttr(node + ".outFloat", armUpperMPANodes[i] + '.frontTwist')



    # ----------------------------------------------------------------------
    # ------------------------------- FINAL -------------------------------- 
    # ----------------------------------------------------------------------

    #Disable button
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