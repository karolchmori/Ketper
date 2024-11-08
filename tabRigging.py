import maya.cmds as mc
import maya.mel as mel
import ElementsUI as elUI
import util
import math

limbLocators = []
limbJoints = []
limbDict = ['arm','leg']


digitsStructures = []
digitsJoints = []
digitsLocator = None
listControlsDigits = []
mainParentCTL = []



def page(mainWidth, mainHeight):

    child = mc.columnLayout()
    mc.frameLayout(label='Structure', collapsable=True, collapse=False, marginWidth=5, marginHeight=5)
    mc.button(l='Generate Structure', c= lambda _: util.rigging.createStructureClass())

    mc.rowLayout(nc=3)
    mc.textField('structureTXT', w=mainWidth/2, tx='GRP;ANM;OFFSET')
    mc.button(l='Create Groups', w=90, c= lambda _: createCTLStructure())
    mc.setParent('..') # End rowLayout

    mc.textField('structureNameTXT', w=mainWidth/2, placeholderText='Leave empty to use first selection name')
    limbSectionWidth = mainWidth/3-10
    mc.setParent('..') # End frameLayout

    mc.rowLayout(nc=2)
    # ----------------------------------------------------------------------
    # ------------------------------- LIMBS --------------------------------
    # ----------------------------------------------------------------------
    mc.frameLayout(label='Limbs', collapsable=False, collapse=False, marginWidth=5, marginHeight=5)
    mc.rowLayout(nc=2, cal=([1,'left'],[2,'center']), cw=[(1, limbSectionWidth), (2, limbSectionWidth/2)])
    mc.text(l='Create Locators: ')
    mc.button('limbLocButton', l='GO', c=lambda _: createStructureLimb())
    mc.setParent('..') # End rowLayout

    elUI.separatorTitleUI('Features',5,20,mainWidth/2-20)
    mc.rowLayout(nc=2)
    mc.rowColumnLayout(nc=2, cal=([1,'left'],[2,'right']), cw=[(1, limbSectionWidth/1.5), (2, limbSectionWidth/2.5)])
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
    limbsCol, limbsRadioButtons = elUI.radioCollectionUI('', limbDict, limbDict[0])
    mc.setParent('..') # End rowLayout

    mc.rowColumnLayout(nc=2, cal=([1,'left'],[2,'center']), cw=[(1, limbSectionWidth), (2, limbSectionWidth/2)])
    mc.text(l='Create Joints: ')
    mc.button('limbCreateButton', l='GO', c=lambda _: createLimbJoints(limbsRadioButtons), en=False)
    mc.setParent('..') # End rowColumnLayout
    mc.button('limbResetButton', l='Restart', c=lambda _: restartLimbChain(), en=False)
    
    mc.setParent('..') # End frameLayout

    # ----------------------------------------------------------------------
    # ------------------------------- DIGITS --------------------------------
    # ----------------------------------------------------------------------
    mc.frameLayout(label='Digits', collapsable=False, collapse=False, marginWidth=5, marginHeight=5)
    mc.rowLayout(nc=4)
    mc.text(l='Digits: ')
    mc.textField('numDigitsTXT', tx='2', w= 40)
    mc.text(l=' Joints: ')
    mc.textField('numJointsTXT', tx='3', w= 40)
    mc.setParent('..') # End rowLayout
    mc.rowLayout(nc=2, cal=([1,'left'],[2,'center']), cw=[(1, limbSectionWidth), (2, limbSectionWidth/2)])
    mc.text(l='Create curves: ')
    mc.button('digitsCurveButton', l='GO', c=lambda _: createStructureDigits())
    mc.setParent('..') # End rowLayout

    mc.rowColumnLayout(nc=2, cal=([1,'left'],[2,'center']), cw=[(1, limbSectionWidth), (2, limbSectionWidth/2)])
    mc.text(l='Create Joints: ')
    mc.button('digitsCreateButton', l='GO', c=lambda _: createDigitsJoints(digitsStructures), en=False)
    mc.setParent('..') # End rowColumnLayout

    mc.rowColumnLayout(nc=2, cal=([1,'left'],[2,'center']), cw=[(1, limbSectionWidth), (2, limbSectionWidth/2)])
    mc.text(l='Connect: ')
    mc.button('digitsConnectButton', l='GO', c=lambda _:createDigitsConnection(digitsLocator, digitsJoints, mainParentCTL), en=False)
    mc.setParent('..') # End rowColumnLayout
    
    mc.button('digitsResetButton', l='Restart', c=lambda _: restartDigitsChain(), en=False)
    mc.setParent('..') # End frameLayout


    mc.setParent('..') # End rowLayout
    mc.setParent( '..' ) # End columnLayout  
    return child


#region DIGITS
def createStructureDigits():
    global digitsStructures
    digits = int(mc.textField('numDigitsTXT', q=True, tx=True))
    numJoints = int(mc.textField('numJointsTXT', q=True, tx=True))

    for i in range(digits):
        digitsStructures.append(util.rigging.createCurveDigits(f'digit{i+1}_CRV', numJoints))

    util.select.modifyButtonList(['digitsCreateButton','digitsResetButton'], True)
    util.select.modifyButtonList(['digitsCurveButton'], False)
    util.select.setfocusMaya()


def createDigitsJoints(digitsStructures):
    global digitsJoints
    global digitsLocator
    global listControlsDigits
    groupStructure = 'GRP;ANIM;OFFSET'

    global mainParentCTL


    for i in range(len(digitsStructures)):
        digitsJoints.append(util.rigging.createDigitsChain(digitsStructures[i]))
        listControlsDigits.append(util.rigging.createCTLJointList(digitsJoints[i],groupStructure))
        mainParentCTL.append(util.naming.modifyName('replace', listControlsDigits[i][0], '_CTL','_GRP'))

    #Parent controllers and joints
    for i in range(len(digitsJoints)):
        for j in range(len(digitsJoints[i])):
            mc.parentConstraint(listControlsDigits[i][j],digitsJoints[i][j],  mo=True, w=1)
    
    
    digitsLocator = mc.spaceLocator(n='connect_LOC')[0]
    util.rigging.addInternalName(digitsLocator, digitsLocator)

    util.select.modifyButtonList(['digitsConnectButton'], True)
    util.select.modifyButtonList(['digitsCreateButton'], False)

    util.select.setfocusMaya()

def createDigitsConnection(digitsLocator, digitsJoints, mainParentCTL):

    locatorPos = util.rigging.getPosition(digitsLocator)
    originalObj = util.rigging.getObjByInternalName(digitsLocator)

    newName = util.naming.modifyName('replace', originalObj, '_LOC','_JNT')

    mc.select(cl=True)
    connectionJoint = mc.joint(p=locatorPos, name = newName)
    mc.select(cl=True)

    #main controller
    mainController = util.rigging.createCTLJointList([connectionJoint],'GRP;ANIM;OFFSET')[0]


    print(digitsJoints)

    for i in range(len(digitsJoints)):
        mc.parent(digitsJoints[i][0], connectionJoint)
        mc.parent(mainParentCTL[i], mainController)

    

    mc.delete(digitsLocator)

    mc.parentConstraint(mainController, connectionJoint,  mo=True, w=1)
    mc.select(cl=True)
    util.select.modifyButtonList(['digitsConnectButton'], False)
    util.select.setfocusMaya()


def restartDigitsChain():
    global digitsStructures
    global digitsJoints
    global digitsLocator
    global listControlsDigits
    global mainParentCTL

    digitsStructures = []
    digitsJoints = []
    digitsLocator = None
    listControlsDigits = []
    mainParentCTL = []

    util.select.modifyButtonList(['digitsCreateButton','digitsConnectButton','digitsResetButton'], False)
    util.select.modifyButtonList(['digitsCurveButton'], True)
    util.select.setfocusMaya()

#endregion



#region LIMB

def limbFeatIKFKChanged(*args):
    if mc.checkBox('featLimbIKFK', query=True, value=True):
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

def createStructureLimb():
    global limbLocators
    limbLocators = util.rigging.createLocatorLimb()
    mc.button('limbLocButton', e=True, en=False)
    util.select.modifyCheckBoxList(['featLimbIKFK'], True, True)
    util.select.modifyCheckBoxList(['featLimbStretch', 'featLimbCurv'], False, True)
    util.select.modifyButtonList(['limbCreateButton','limbResetButton'], True)

    util.select.setfocusMaya()


def createLimbJoints(limbsRadio):
    global limbJoints
    groupStructure = 'GRP;ANIM;OFFSET'
    firstGroup = groupStructure.split(';')[0]

    stretch = mc.checkBox('featLimbStretch', q=True, v=True)
    soft =  mc.checkBox('featLimbSoft', q=True, v=True)
    pvPin = mc.checkBox('featLimbPVPin', q=True, v=True)
    curvature = mc.checkBox('featLimbCurv', q=True, v=True)
    twist = False

    #GET SCOPE
    limbName = None
    for button in limbsRadio:
        if mc.radioButton(button, query=True, select=True):
            limbName = mc.radioButton(button, query=True, label=True)
            break

    #Create limb and duplicate to IK and FK
    limbJoints.append(util.rigging.createLimbChain(limbLocators))

    # ----------------------------------------------------------------------
    # ----------------------------- CREATE IK ------------------------------
    # ----------------------------------------------------------------------
    
    limbJoints.append(util.rigging.copyJoints(limbJoints[0],'IK'))
    ikHandle = mc.ikHandle(n=f'IK_{limbName}_HDL', sj=limbJoints[1][0], ee=limbJoints[1][2], sol='ikRPsolver')[0] 
    listControlsIK = util.rigging.createIkCTLJointList(ikHandle, limbJoints[1][1] ,groupStructure)
    
    tempConstraint = mc.parentConstraint(listControlsIK[0], ikHandle, mo=True, w=1)
    mc.poleVectorConstraint(listControlsIK[1], ikHandle)
    mc.orientConstraint( listControlsIK[0], limbJoints[1][2], mo=True)

    #Create groups and parent it. ALSO move PV Control to a position inside the plane
    lastGroup = util.create.createGroupStructure(groupStructure,f'IK_{limbName}_Controls',None)
    util.rigging.movePVControl(limbJoints[1], f'IK_{limbName}_PV_' + firstGroup, 4)
    mc.parent(f'IK_{limbName}_' + firstGroup, lastGroup)
    mc.parent(f'IK_{limbName}_PV_' + firstGroup, lastGroup)

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
        IKlimbStrCON = util.rigging.generateIKStretchNodes(limbJoints, listControlsIK, limbName)

        if soft:
            # ----------------------------------------------------------------------
            # ----------------------------- SOFT IK -------------------------------- # DEPENDS FROM STRETCH IK 
            # ----------------------------------------------------------------------
            mc.select(listControlsIK[0]) 
            mc.addAttr(longName='soft', niceName= 'Soft' , attributeType="float", dv=0, min=0, max=1, h=False, k=True)
            
            # ------------------------------ NODES ----------------------------------
            
            IKlimbSoftCON, lastGroup = util.rigging.generateIKSoftNodes(limbJoints, listControlsIK, ikHandle, tempConstraint, IKlimbStrCON, limbName)
        
            # ----------------------------------------------------------------------
            # ----------------------------- PV PIN -------------------------------- # DEPENDS FROM SOFT IK
            # ----------------------------------------------------------------------
            if pvPin:
                mc.select(listControlsIK[1])
                mc.addAttr(longName='pin', niceName= 'Pin', attributeType="float", dv=0, min=0, max=1, h=False, k=True)

                util.rigging.generateIKPVPinNodes(limbJoints, listControlsIK, lastGroup, IKlimbSoftCON, limbName)
    

    # ----------------------------------------------------------------------
    # ----------------------------- CREATE FK ------------------------------
    # ----------------------------------------------------------------------

    #Create FK LIMB Chain with all Groups
    limbJoints.append(util.rigging.copyJoints(limbJoints[0],'FK'))
    listControlsFK = util.rigging.createCTLJointList(limbJoints[2],groupStructure)
    util.rigging.parentControlJoints(listControlsFK,limbJoints[2])
    tempName = util.naming.modifyName('replace',limbJoints[2][0],'_JNT','')
    tempRoot = tempName + '_' + firstGroup
    lastGroup = util.create.createGroupStructure(groupStructure,f'FK_{limbName}_Controls',None)
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
    controlName = f'{limbName}_Preferences_CTL'
    lastGroup = util.create.createGroupStructure(groupStructure,f'{limbName}_Preferences_Controls',None)
    util.create.createTextCurves('Switch')
    selection = mc.ls(sl=True)[0]
    mc.parent(selection, lastGroup)
    mc.rename(selection, controlName)
    
    tempGroup = f'{limbName}_Preferences_Controls_' + firstGroup
    mc.matchTransform(tempGroup, limbJoints[0][0], pos=True)
    mc.move(0, 4, -10, tempGroup, relative=True)

    #Add attribute and visibility with controls
    mc.select(controlName)
    mc.addAttr( longName='switchIKFK', niceName= 'Switch IK / FK' , attributeType="float", dv=0, max=1, min=0, h=False, k=True)
    mc.connectAttr(f"{controlName}.switchIKFK", f"FK_{limbName}_Controls_" + firstGroup + ".visibility", force=True)
    reverseNode = mc.createNode('reverse', name=f'{limbName}_switchIKFK_REVERSE') 
    mc.connectAttr(f"{controlName}.switchIKFK", f"{reverseNode}.inputX", force=True)
    mc.connectAttr(f"{reverseNode}.outputX", f"IK_{limbName}_Controls_" + firstGroup + ".visibility", force=True)

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
        limbUpperSegCRV = detachCurve[0]
        limbLowerSegCRV = detachCurve[1]
        limbUpperSegCRV = mc.rename(limbUpperSegCRV, f'{limbName}UpperSeg_CRV')
        limbLowerSegCRV = mc.rename(limbLowerSegCRV, f'{limbName}LowerSeg_CRV')
        limbUpperSegCRVShape = mc.listRelatives(limbUpperSegCRV, shapes=True)[0]
        rangeTwist = 5
        
        nodeFCList = util.rigging.createFloatConstant([0.001, 0.25, 0.5, 0.75, 0.999])
        
        #TODO add a parent to NonRoll01 --> driver is joint01 Original

        limbUpperMPANodes = util.rigging.createMPACurveJNT(rangeTwist, f'{limbName}UpperTwist0', limbUpperSegCRVShape, nodeFCList)
        limbUpperNonRollJoints, limbUpperRollJoints = util.rigging.createTwistStructure(limbJoints[0], f'{limbName}Upper', 'end')

        for i in range(len(limbUpperMPANodes)):
            mc.setAttr(limbUpperMPANodes[i] + ".worldUpType", 2)
            mc.connectAttr(limbUpperNonRollJoints[0]+'.worldMatrix[0]', limbUpperMPANodes[i] + ".worldUpMatrix")

            node = util.rigging.floatMConnect(f'{limbName}Upper{i+1}FLM', 2, nodeFCList[i] + '.outFloat', limbUpperRollJoints[0] +'.rotateX')
            mc.connectAttr(node + ".outFloat", limbUpperMPANodes[i] + '.frontTwist')



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
    util.select.setfocusMaya()

#endregion

#region OTHER

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

    util.select.setfocusMaya()

#endregion