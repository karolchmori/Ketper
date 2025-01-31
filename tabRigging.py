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


spineLocators = []
spineJoints = []

neckLocators = []
neckJoints = []

footLocators = []
footIKLocators = []
footJoints = []


def page(mainWidth, mainHeight):

    child = mc.columnLayout()
    mc.frameLayout(label='Structure', collapsable=True, collapse=False, marginWidth=5, marginHeight=5, w=mainWidth-10)
    mc.button(l='Generate Structure', w=mainWidth-40, c= lambda _: util.rigging.createStructureClass())

    elUI.separatorTitleUI('Create group CTL',5,20,mainWidth-40)
    mc.rowLayout(nc=4)
    mc.textField('structureTXT', w=mainWidth/2+20, tx='GRP;ANM;OFFSET')
    mc.text(l='')
    mc.button(l='GO', c= lambda _: createCTLStructure())
    mc.textField('structureNameTXT', w=120, placeholderText='Controller name')
    mc.setParent('..') # End rowLayout

    
    limbSectionWidth = mainWidth/3-10
    mc.setParent('..') # End frameLayout
    # ----------------------------------------------------------------------
    # ------------------------------- SPINE --------------------------------
    # ----------------------------------------------------------------------

    mc.frameLayout(label='Spine', collapsable=True, collapse=False, marginWidth=5, marginHeight=5, w=mainWidth-10)

    mc.rowLayout(nc=2)
    mc.text(l='Create Locators: ')
    mc.button('spineLocButton', l='GO', c=lambda _: createStructureSpine())
    mc.setParent('..') # End rowLayout
    mc.rowColumnLayout(nc=2, cal=([1,'left'],[2,'center']), cw=[(1, limbSectionWidth), (2, limbSectionWidth/2)])
    mc.text(l='Create Joints: ')
    mc.button('spineCreateButton', l='GO', c=lambda _: createSpineJoints(), en=False)
    mc.text(l='Create Controllers: ')
    mc.button('spineControlsButton', l='GO', c=lambda _: createSpineControllers(spineJoints))
    mc.setParent('..') # End rowColumnLayout

    mc.setParent('..') # End frameLayout


        # ----------------------------------------------------------------------
    # ------------------------------- NECK --------------------------------
    # ----------------------------------------------------------------------

    mc.frameLayout(label='Neck', collapsable=True, collapse=False, marginWidth=5, marginHeight=5, w=mainWidth-10)

    mc.rowLayout(nc=2)
    mc.text(l='Create Locators: ')
    mc.button('neckLocButton', l='GO', c=lambda _: createStructureNeck())
    mc.setParent('..') # End rowLayout
    mc.rowColumnLayout(nc=2, cal=([1,'left'],[2,'center']), cw=[(1, limbSectionWidth), (2, limbSectionWidth/2)])
    mc.text(l='Create Joints: ')
    mc.button('neckCreateButton', l='GO', c=lambda _: createNeckJoints(), en=False)
    mc.text(l='Create Controllers: ')
    mc.button('neckControlsButton', l='GO', c=lambda _: createNeckControllers(neckJoints))
    mc.setParent('..') # End rowColumnLayout

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
    mc.text(l='Create Controllers: ')
    mc.button('limbControlsButton', l='GO', c=lambda _: createLimbControls(limbsRadioButtons), en=False)
    mc.setParent('..') # End rowColumnLayout
    mc.button('limbResetButton', l='Restart', c=lambda _: restartLimbChain(), en=False)
    
    mc.setParent('..') # End frameLayout

    # ----------------------------------------------------------------------
    # ------------------------------- DIGITS --------------------------------
    # ----------------------------------------------------------------------
    mc.frameLayout(label='Digits', collapsable=False, collapse=False, marginWidth=5, marginHeight=5)
    mc.rowLayout(nc=4)
    mc.text(l='Digits: ')
    mc.textField('numDigitsTXT', tx='5', w= 40)
    mc.text(l=' Joints: ')
    mc.textField('numJointsTXT', tx='4', w= 40)
    mc.setParent('..') # End rowLayout

    mc.rowLayout(nc=2, cal=([1,'left'],[2,'center']), cw=[(1, limbSectionWidth), (2, limbSectionWidth/2)])
    mc.text(l='Create Curves: ')
    mc.button('digitsCurveButton', l='GO', c=lambda _: createStructureDigits())
    mc.setParent('..') # End rowLayout

    mc.rowColumnLayout(nc=2, cal=([1,'left'],[2,'center']), cw=[(1, limbSectionWidth), (2, limbSectionWidth/2)])
    mc.text(l='Create Joints: ')
    mc.button('digitsCreateButton', l='GO', c=lambda _: createDigitsJoints(digitsStructures), en=False)
    mc.setParent('..') # End rowColumnLayout

    mc.rowColumnLayout(nc=2, cal=([1,'left'],[2,'center']), cw=[(1, limbSectionWidth), (2, limbSectionWidth/2)])
    mc.text(l='Create Controllers: ')
    mc.button('digitsControlsButton', l='GO', c=lambda _: createDigitsControls(digitsJoints), en=False)
    mc.setParent('..') # End rowColumnLayout

    mc.rowColumnLayout(nc=2, cal=([1,'left'],[2,'center']), cw=[(1, limbSectionWidth), (2, limbSectionWidth/2)])
    mc.text(l='Connect: ')
    mc.button('digitsConnectButton', l='GO', c=lambda _:createDigitsConnection(digitsLocator, digitsJoints, mainParentCTL), en=False)
    mc.setParent('..') # End rowColumnLayout
    
    mc.button('digitsResetButton', l='Restart', c=lambda _: restartDigitsChain(), en=False)
    mc.setParent('..') # End frameLayout
    mc.setParent('..') # End rowLayout

    # ----------------------------------------------------------------------
    # -------------------------- REVERSE FOOT ------------------------------
    # ----------------------------------------------------------------------
    mc.frameLayout(label='Reverse Foot', collapsable=False, collapse=False, marginWidth=5, marginHeight=5)
    mc.rowLayout(nc=2)
    mc.text(l='Create Locators: ')
    mc.button('footLocButton', l='GO', c= lambda _: createStructureFoot())
    mc.setParent('..') # End rowLayout
    mc.rowColumnLayout(nc=2, cal=([1,'left'],[2,'center']), cw=[(1, limbSectionWidth), (2, limbSectionWidth/3)])
    mc.text(l='Create Joints: ')
    mc.button('footCreateButton', l='GO', c= lambda _: createFootJoints())
    mc.text(l='Create Locators Reverse Foot: ')
    mc.button('footIKLocButton', l='GO', c= lambda _: createStructureRevFoot())
    mc.text(l='Create Controllers: ')
    mc.button('footControlsButton', l='GO', c= lambda _: createFootControllers())
    mc.setParent('..') # End rowColumnLayout

    mc.setParent('..') # End frameLayout




    '''    # ----------------------------------------------------------------------
    # -------------------------- DRIVEN KEYS -------------------------------
    # ----------------------------------------------------------------------
    mc.frameLayout(label='Driven keys', collapsable=False, collapse=False, marginWidth=5, marginHeight=5)
    mc.rowColumnLayout(nc=2)
    mc.textField()
    mc.button(l='Load Driver')
    mc.textField()
    mc.button(l='GO')
    mc.setParent('..') # End rowColumnLayout

    mc.rowColumnLayout(nc=3)
    mc.text(l='Min')
    mc.text(l='Max')
    mc.text(l='Default')
    mc.floatField()
    mc.floatField()
    mc.floatField()
    mc.setParent('..') # End rowColumnLayout
    mc.button(l='Load Driven')
    elUI.dropdownUI('test', 'label', ['yellow','white','black'],'yellow')
    mc.setParent('..') # End frameLayout '''

    
    mc.setParent( '..' ) # End columnLayout  
    return child

#region REVERSE FEET

def createStructureFoot():
    global footLocators

    footLocators = util.rigging.createLocStructure(3)

def createFootJoints():
    global footJoints

    footJoints.append(util.rigging.createFootChain(footLocators))
    util.select.setfocusMaya()

def createStructureRevFoot():
    global footIKLocators
    footIKLocators = util.rigging.createLocStructure(7)


def createFootControllers():
    global footIKLocators
    groupStructure = 'GRP;ANIM;OFFSET'
    firstGroup = groupStructure.split(';')[0]

    
    # ----------------------------------------------------------------------
    # ----------------------------- CREATE IK ------------------------------
    # ----------------------------------------------------------------------
    
    footJoints.append(util.rigging.copyJoints(footJoints[0],'IK'))
    footIKLoc = mc.duplicate(footIKLocators[0])
    footIKLoc = mc.rename(footIKLoc, 'foot_IK_LOC')

    footIKLocators.append(footIKLoc)

    for loc in footIKLocators:
        groupName = util.naming.replaceText(loc, '_LOC', '_loc')
        lastGroup = util.create.createGroupStructure(groupStructure, groupName, None)
        mc.matchTransform(groupName + '_' + firstGroup, loc, pos=True)
        mc.parent(loc, lastGroup)
        mc.setAttr(loc + '.translateX', 0)
        mc.setAttr(loc + '.translateY', 0)
        mc.setAttr(loc + '.translateZ', 0)
    
    mc.parent('heel_loc_GRP', 'foot_IK_LOC')
    mc.parent('out_bank_loc_GRP', 'heel_LOC')
    mc.parent('in_bank_loc_GRP', 'out_bank_LOC')
    mc.parent('toe_tip_loc_GRP', 'in_bank_LOC')
    mc.parent('toe_loc_GRP', 'toe_tip_LOC')
    mc.parent('ball_loc_GRP', 'toe_tip_LOC')
    mc.parent('ankle_loc_GRP', 'ball_LOC')

       
    footIKLocatorsRev = list(reversed(footIKLocators))
    listControlsIK = util.rigging.createCTLJointList(footIKLocatorsRev[1:7],groupStructure)
    mc.parent('toe_tip_GRP','in_bank_CTL')
    mc.parent('ball_GRP','toe_tip_CTL')

    
    mc.parentConstraint('ankle_LOC',footJoints[1][0], mo=True)
    mc.parentConstraint('toe_LOC',footJoints[1][1], mo=True)

    #Parent CTLs and LOC
    for ctl in listControlsIK:
        mc.parentConstraint(ctl, util.naming.replaceText(ctl,'_CTL','_LOC'))
    
    
    # ----------------------------------------------------------------------
    # ----------------------------- CREATE FK ------------------------------
    # ----------------------------------------------------------------------

    footJoints.append(util.rigging.copyJoints(footJoints[0],'FK'))
    listControlsFK = util.rigging.createCTLJointList(footJoints[2][1:],groupStructure)
    util.rigging.parentControlJoints(listControlsFK,footJoints[2][1:])
    tempName = util.naming.modifyName('replace',footJoints[2][1],'_JNT','')
    tempRoot = tempName + '_' + firstGroup
    lastGroup = util.create.createGroupStructure(groupStructure,'FK_foot_Controls', None)
    mc.parent(tempRoot, lastGroup)

    '''#Add attribute and visibility with controls
    mc.select(controlName)
    mc.addAttr( longName='switchIKFK', niceName= 'Switch IK / FK' , attributeType="float", dv=0, max=1, min=0, h=False, k=True)
    mc.connectAttr(f"{controlName}.switchIKFK", f"FK_{limbName}_Controls_" + firstGroup + ".visibility", force=True)
    reverseNode = mc.createNode('reverse', name=f'{limbName}_switchIKFK_REVERSE') 
    mc.connectAttr(f"{controlName}.switchIKFK", f"{reverseNode}.inputX", force=True)
    mc.connectAttr(f"{reverseNode}.outputX", f"IK_{limbName}_Controls_" + firstGroup + ".visibility", force=True) '''

    # ----------------------------------------------------------------------
    # --------------------------- PAIR BLENDS ------------------------------
    # ----------------------------------------------------------------------
    for i in range(len(footJoints[0])):
        pbNode = util.rigging.createPB(footJoints[0][i], footJoints[1][i], footJoints[2][i], True, True)
        #mc.connectAttr(f"{controlName}.switchIKFK", f"{pbNode}.weight", force=True) 

#endregion

#region SPINE

def createStructureSpine():
    global spineLocators

    spineLocators = util.rigging.createLocStructure(2)
    util.select.modifyButtonList(['spineCreateButton'], True)
    util.select.modifyButtonList(['spineLocButton'], False)
    util.select.setfocusMaya()

def createSpineJoints():
    global spineJoints

    spineJoints.append(util.rigging.createSpineChain(spineLocators, 5))
    util.select.setfocusMaya()

def createSpineControllers(spineJoints):
    ''' ----------------------------------- SPINE ----------------------------------- 
        1. Create two locators, root and end. Goes from bottom to top
        2. Calculate the distance between two point and input X amounts of joints evenly. 
        3. Create IK handle between root and end. Number spans 2, deactivate auto parent curve
        4. DONT DO ----- Create clusters in each cv of the curve , create it on each cv
        5. Create groups and controllers on each cluster, make the size bigger
        6. Parent the groups. Check the video because is not ordered by number
        7. DONT DO ----- Delete clusters
    '''
    groupStructure = 'GRP;ANIM;OFFSET'
    firstGroup = groupStructure.split(';')[0]
    controllersList = []
    stretch = True

    ikHandle = mc.ikHandle(n='spine_HDL', sj=spineJoints[0][0], ee=spineJoints[0][len(spineJoints[0])-1], sol='ikSplineSolver', ns=2, pcv=False, ccv=True)[0] 
    spineCRV = mc.listConnections(ikHandle + ".inCurve", type="nurbsCurve")[0]
    spineCRV = mc.rename(spineCRV, 'spine_CRV')

    numCvs = mc.getAttr(f"{spineCRV}.degree") + mc.getAttr(f"{spineCRV}.spans")
    for i in range(numCvs):
        # Get the position of each CV
        cvPos = mc.pointPosition(f"{spineCRV}.cv[{i}]", world=True)
        controller = util.create.createShape('circle')[0]
        controller = mc.rename(controller, f'spine_0{i+1}_CTL')
        lastGroup = util.create.createGroupStructure(groupStructure,f'spine_0{i+1}_Controls', None)
        mc.parent(controller, lastGroup)
        mc.xform(f'spine_0{i+1}_Controls_' + firstGroup, translation=cvPos)
        controllersList.append(controller)

    #Parent like video
    mc.parent('spine_02_Controls_' + firstGroup, 'spine_01_CTL')
    mc.parent('spine_03_Controls_' + firstGroup, 'spine_01_CTL')
    mc.parent('spine_04_Controls_' + firstGroup, 'spine_05_CTL')
    mc.parent('spine_05_Controls_' + firstGroup, 'spine_03_CTL')

    '''
        8. Select the curve shape
        9. DecomposeMatrix --> InputMatrix   (C_spine01_CTL)  DecomposeMatrix.OutputTranslate to shape.ControlPoints[0]  
        10. Do the same for all the controllers
    '''

    spineCRVShape = mc.listRelatives(spineCRV, shapes=True)[0]
    firstDCMNode = None
    for i in range(len(controllersList)):
        node = mc.createNode('decomposeMatrix', name= f'spine_0{i+1}_CVDCM')
        if i == 0:
            firstDCMNode = node
        mc.connectAttr(controllersList[i] + '.worldMatrix[0]', node + '.inputMatrix')
        mc.connectAttr(node + '.outputTranslate', spineCRVShape + f'.controlPoints[{i}]')

    #TODO: create a locator with hip end?? 
    ''' ----------------------------------- HIP ----------------------------------- 
        1. Create a controller, position it on the root spine, modify the controller form
        2. Modify the first DecomposeMatrix, it won't be connected to spine_01 anymore, but to the controller of the HIP
        3. Create two joints, one with the same position to the spine root, and the other one below (from top to bottom)
        4. Parent the controller to the hip joint root
    '''
    rootPos = util.rigging.getPosition(spineJoints[0][0])


    hipCTL = util.create.createShape('cube')
    hipCTL = mc.rename(hipCTL, 'spineHip_CTL')
    util.create.changeSizeCurve(hipCTL,0.75)

    lastGroup = util.create.createGroupStructure(groupStructure,'spineHip_Controls', None)
    mc.parent(hipCTL, lastGroup)
    mc.xform('spineHip_Controls_' + firstGroup, translation=rootPos)

    mc.disconnectAttr(controllersList[0] + '.worldMatrix[0]', firstDCMNode + '.inputMatrix')
    mc.connectAttr(hipCTL + '.worldMatrix[0]', firstDCMNode + '.inputMatrix')

    hipRootJNT = mc.duplicate(spineJoints[0][0], rr=True, po=True)
    hipRootJNT = mc.rename(hipRootJNT, "localHipRoot_JNT")
    mc.select(hipRootJNT)

    hipEndJNT = mc.duplicate(hipRootJNT, rr=True)
    hipEndJNT = mc.rename(hipEndJNT, "localHipEnd_JNT")
    mc.parent(hipEndJNT,hipRootJNT)

    spineJoints.append([hipRootJNT,hipEndJNT])
    
    for i in range(len(spineJoints[1])-1):
        locatorTemp = mc.spaceLocator()[0]
        mc.matchTransform(locatorTemp, spineJoints[1][i], scl=False, rot=False, pos=True)
        mc.move(0, 0, 5, locatorTemp, relative=True)
        mc.aimConstraint(spineJoints[1][i+1],spineJoints[1][i], wut='object', wuo=locatorTemp, aim=(1,0,0), u=(0,0,1))
        mc.delete( f"{spineJoints[1][i]}_aimConstraint1", locatorTemp)

    util.rigging.nullJointOrients(spineJoints[1][len(spineJoints[1])-1])

    mc.move(0, -5, 0, hipEndJNT, relative=True)

    mc.parentConstraint(hipCTL, hipRootJNT)
    controllersList.append(hipCTL)

    ''' ----------------------------------- BODY MAIN ----------------------------------- 
        1. Create a controller positioned on the root joint (controller + group)
        2. body_CTL parentConstraint spine_Hip_Controls_GRP only rotate (if I move it doesn't affect, but when I rotate everything rotates)
        3. spine01Controls_GRP parent normal on body_CTL 
    '''

    bodyCTL = util.create.createShape('cube')
    bodyCTL = mc.rename(bodyCTL, 'body_CTL')

    lastGroup = util.create.createGroupStructure(groupStructure,'body_Controls', None)
    mc.parent(bodyCTL, lastGroup)
    mc.xform('body_Controls_' + firstGroup, translation=rootPos)

    mc.parentConstraint(bodyCTL, 'spineHip_Controls_' + firstGroup, st=["x","z","y"], mo=True)
    mc.parent('spine_01_Controls_GRP', bodyCTL)
    controllersList.append(bodyCTL)

    '''
        ----------------------------------- IK HANDLE TWIST ----------------------------------- 
        1. Activate Advanced Twist Controls on IKHandle (check)
        2. World Up type = Object Rotation Up (Start/End)
        3. Forward Axis = Positive Y
        4. Up Axis = Positive X
        5. Up vector (1,0,0) ---- Up Vector 2 (1,0,0)
        6. World Up Object = spineHip_CTL
        7. World Up Object = spine_05_CTL
    '''


    mc.setAttr(f'{ikHandle}.dTwistControlEnable', 1)
    mc.setAttr(f'{ikHandle}.dWorldUpType', 4) # 4 = "Object Rotation Up (Start/End)"
    mc.setAttr(f'{ikHandle}.dForwardAxis', 2)  # 2 = Positive Y
    mc.setAttr(f'{ikHandle}.dWorldUpAxis', 6)  # 6 = Positive X
    mc.setAttr(f'{ikHandle}.dWorldUpVectorX', 1)
    mc.setAttr(f'{ikHandle}.dWorldUpVectorY', 0)
    mc.setAttr(f'{ikHandle}.dWorldUpVectorZ', 0)
    mc.setAttr(f'{ikHandle}.dWorldUpVectorEndX', 1)
    mc.setAttr(f'{ikHandle}.dWorldUpVectorEndY', 0)
    mc.setAttr(f'{ikHandle}.dWorldUpVectorEndZ', 0)

    mc.connectAttr('spineHip_CTL' + '.worldMatrix[0]', ikHandle + ".dWorldUpMatrix")
    mc.connectAttr('spine_05_CTL' + '.worldMatrix[0]', ikHandle + ".dWorldUpMatrixEnd")


    '''
        0. Disconnect current 01 CDM and connect like the first time
        1. spine_01_CTL point constraint on spineHip_CTL
    
    '''
    
    mc.disconnectAttr(hipCTL + '.worldMatrix[0]', firstDCMNode + '.inputMatrix')
    mc.connectAttr(controllersList[0] + '.worldMatrix[0]', firstDCMNode + '.inputMatrix')
    mc.pointConstraint(controllersList[0], 'spineHip_Controls_' + firstGroup)

    # ----------------------------------------------------------------------
    # --------------------------- PREFERENCES ------------------------------
    # ----------------------------------------------------------------------
    controlName = 'spine_Preferences_CTL'
    lastGroup = util.create.createGroupStructure(groupStructure,'spine_Preferences_Controls',None)
    controller = util.create.createTextCurves('S')
    controller = mc.rename(controller, controlName)

    mc.parent(controller, lastGroup)
    
    tempGroup = 'spine_Preferences_Controls_' + firstGroup
    mc.matchTransform(tempGroup, spineJoints[0][0], pos=True)
    mc.move(0, 0, -20, tempGroup, relative=True)

    controllersList.append(controlName)
    #print(controllersList)

    # ----------------------------------------------------------------------
    # ------------------------------ STRETCH -------------------------------
    # ----------------------------------------------------------------------
    if stretch:
        mc.select(controllersList[-1])
        mc.addAttr(longName='stretch', niceName= 'Stretch', attributeType="float", dv=0, min=0, max=1, h=False, k=True)
        mc.addAttr(longName='stretchMin', niceName= 'Stretch Min', attributeType="float", dv=0.8, min=0.001, max=1, h=False, k=True)
        mc.addAttr(longName='stretchMax', niceName= 'Stretch Max', attributeType="float", dv=1.2, min=1, h=False, k=True)
        mc.addAttr(longName='offset', niceName= 'Offset', attributeType="float", dv=0, min=0, max=1, h=False, k=True)

        # Create a curveInfo node
        spineCRVInfo = mc.createNode('curveInfo', name=f"{spineCRVShape}_curveInfo")
        # Connect the curve's worldSpace attribute to the curveInfo node's inputCurve attribute
        mc.connectAttr(f"{spineCRVShape}.worldSpace[0]", f"{spineCRVInfo}.inputCurve")

        spineInitialLenFLM = util.rigging.floatMConnect('spineScaleFLM',2, None, None)
        mc.setAttr(spineInitialLenFLM + '.floatA', mc.getAttr(f"{spineCRVInfo}.arcLength"))
        mc.setAttr(spineInitialLenFLM + '.floatB', 1) #TODO C_masterWalk_CTL.globalscale
        
        spineStretchFactorFLM = util.rigging.floatMConnect('spineCRVFLM',3,f"{spineCRVInfo}.arcLength", spineInitialLenFLM + '.outFloat')
        
        # Create the clamp node
        spineStretchFactorCLM = mc.createNode('clamp', name='spineStretchFactorCLM')
        mc.connectAttr( f'{spineStretchFactorFLM}.outFloat', f"{spineStretchFactorCLM}.inputR", force=True)
        mc.connectAttr(controllersList[-1] + '.stretchMin', f"{spineStretchFactorCLM}.minR") # Minimum clamp value
        mc.connectAttr(controllersList[-1] + '.stretchMax', f"{spineStretchFactorCLM}.maxR")  # Maximum clamp value

        # 1. Create a floatConstant node
        spineBaseStretchFLC = mc.createNode('floatConstant', name='spineBaseStretchFLC')

        # 2. Create a blendTwoAttr node
        spineStretchBTA = mc.createNode('blendTwoAttr', name='spineStretchBTA')
        # Connect input1 and input2 to blendTwoAttr
        mc.connectAttr(f"{spineBaseStretchFLC}.outFloat" , f"{spineStretchBTA}.input[0]")
        mc.connectAttr(f"{spineStretchFactorCLM}.outputR" , f"{spineStretchBTA}.input[1]")
        mc.connectAttr(controllersList[-1] + '.stretch', f"{spineStretchBTA}.attributesBlender")

        spineStretchValueFLM = util.rigging.floatMConnect('spineStretchValueFLM', 2, f"{spineStretchBTA}.output", None)
        mc.setAttr(spineStretchValueFLM + '.floatB', mc.getAttr(spineJoints[0][3] + ".translateY"))

        for i in range(1, len(spineJoints[0])):
            mc.connectAttr(f"{spineStretchValueFLM}.outFloat" , f"{spineJoints[0][i]}.translateY")

        # ----------------------------------------------------------------------
        # ------------------------------- OFFSET -------------------------------
        # ----------------------------------------------------------------------
        '''
            1. Do reverse curve of spineCRV (keep original)
            2. Rename spineReverseChain_CRV
            3. Duplicate spine JNT and rename??  spine --> spineReversed
            4. Unparent them
            5. Parent them reversed 5 to 1 and rename it 1 to 5 -- DONE IN 3
            6. Save on the joint lists (NOT BEFORE. After reversing to keep the new order)
            7. Create ikHandle spineReversed_HDL, uncheck auto parent curve, uncheck auto create curve. Root to end (selecting the new curve??? he didn't do it but pointed at it)
            8. spineStretchValue
        '''
        spineReversedCRV = mc.reverseCurve(spineCRV, n= 'spineReversed_CRV' , ch=True, rpo=False)[0]
        revJointsTemp = util.rigging.copyJoints(spineJoints[0],'rev')
        for i in range(len(revJointsTemp)):
            revJointsTemp[i] = mc.rename(revJointsTemp[i],f'spineRev_0{len(revJointsTemp)-i}_JNT')

        #unparent --> parent to world
        for i in range(1,len(revJointsTemp)):
            mc.parent(revJointsTemp[i], world=True)

        #parent them by order
        for i in range(len(revJointsTemp)-1):
            mc.parent(revJointsTemp[i], revJointsTemp[i+1])

        #get new list 
        spineJoints.append(list(reversed(revJointsTemp)))
        #print(spineJoints)

        revikHandle = mc.ikHandle(n='spineReversed_HDL', sj=spineJoints[2][0], ee=spineJoints[2][len(spineJoints[2])-1], sol='ikSplineSolver', pcv=False, ccv=False, curve=spineReversedCRV)[0]
        
        
        spineNegStretchValueFLM = util.rigging.floatMConnect('spineNegStretchValueFLM', 2, f"{spineStretchValueFLM}.outFloat", None)
        mc.setAttr(spineNegStretchValueFLM + '.floatB', -1)
        for i in range(1, len(spineJoints[2])):
            mc.connectAttr(f"{spineNegStretchValueFLM}.outFloat" , f"{spineJoints[2][i]}.translateY")
        

        '''
            1. Bring spineReversed05_JNT and spineCRVShape
            2. Create nearestPointOnCurve
        '''

        # Create the nearestPointOnCurve node
        spineOffsetNPC = mc.createNode('nearestPointOnCurve', name='spineOffsetNPC')
        mc.connectAttr(f"{spineCRVShape}.worldSpace[0]", f"{spineOffsetNPC}.inputCurve")

        # Optionally set attributes like parameter
        mc.setAttr(f"{spineOffsetNPC}.parameter", 0.5)  # Set to a specific parameter on the curve
        spineRevDCM = mc.createNode('decomposeMatrix', name='spineRevDCM')
        mc.connectAttr(f'{spineJoints[2][len(spineJoints[2])-1]}.worldMatrix[0]', f"{spineRevDCM}.inputMatrix")
        mc.connectAttr(f"{spineRevDCM}.outputTranslate", f"{spineOffsetNPC}.inPosition")

        spineOffsetInitialValueFLC = mc.createNode('floatConstant', name='spineOffsetInitialValueFLC')
        mc.setAttr(f"{spineOffsetInitialValueFLC}.inFloat", 0.0)

        spineOffsetBTA = mc.createNode('blendTwoAttr', name='spineOffsetBTA')
        # Connect input1 and input2 to blendTwoAttr
        mc.connectAttr(f"{spineOffsetInitialValueFLC}.outFloat" , f"{spineOffsetBTA}.input[0]")
        mc.connectAttr(f"{spineOffsetNPC}.parameter" , f"{spineOffsetBTA}.input[1]")
        mc.connectAttr(controllersList[-1] + '.offset', f"{spineOffsetBTA}.attributesBlender")

        mc.connectAttr(f"{spineOffsetBTA}.output", f"{ikHandle}.offset")

        # ----------------------------------------------------------------------
        # -------------------- ADDITIONAL CONSIDERATIONS -----------------------
        # ----------------------------------------------------------------------
        #43:03

        '''
            1. delete parent constraint on the localHipRoot_JNT
            2. pointConstraint(spine01_JNT, localHip_JNT)
        
        '''

        hipRootConstraint = mc.listConnections(spineJoints[1][0], type='parentConstraint')
        mc.delete(hipRootConstraint)
        mc.pointConstraint(spineJoints[0][0], spineJoints[1][0])
        mc.orientConstraint(hipCTL, spineJoints[1][0])

        hipCTLConstraint = mc.listConnections('spineHip_Controls_' + firstGroup, type='pointConstraint')
        #print(hipCTLConstraint)
        #mc.delete(hipCTLConstraint)

        #mc.pointConstraint(controllersList[0], 'spineHip_Controls_' + firstGroup)

    # VOLUME PRESERVATION 47:16  --- 2024-10-15 09-47-05
    #Change size of all controllers:
    for ctl in controllersList:
        util.create.changeSizeCurve(ctl, 4)

    mc.select(cl=True)
    util.select.setfocusMaya()

#endRegion

#region NECK

def createStructureNeck():
    global neckLocators

    neckLocators = util.rigging.createLocStructure(2)
    util.select.modifyButtonList(['neckCreateButton'], True)
    util.select.modifyButtonList(['neckLocButton'], False)
    util.select.setfocusMaya()

def createNeckJoints():
    global neckJoints

    neckJoints.append(util.rigging.createSpineChain(neckLocators, 5))
    util.select.setfocusMaya()

def createNeckControllers(spineJoints):
    ''' ----------------------------------- SPINE ----------------------------------- 
        1. Create two locators, root and end. Goes from bottom to top
        2. Calculate the distance between two point and input X amounts of joints evenly. 
        3. Create IK handle between root and end. Number spans 2, deactivate auto parent curve
        4. DONT DO ----- Create clusters in each cv of the curve , create it on each cv
        5. Create groups and controllers on each cluster, make the size bigger
        6. Parent the groups. Check the video because is not ordered by number
        7. DONT DO ----- Delete clusters
    '''
    groupStructure = 'GRP;ANIM;OFFSET'
    firstGroup = groupStructure.split(';')[0]
    controllersList = []

    ikHandle = mc.ikHandle(n='neck_HDL', sj=spineJoints[0][0], ee=spineJoints[0][len(spineJoints[0])-1], sol='ikSplineSolver', ns=2, pcv=False, ccv=True)[0] 
    spineCRV = mc.listConnections(ikHandle + ".inCurve", type="nurbsCurve")[0]
    spineCRV = mc.rename(spineCRV, 'neck_CRV')

    numCvs = mc.getAttr(f"{spineCRV}.degree") + mc.getAttr(f"{spineCRV}.spans")
    for i in range(numCvs):
        # Get the position of each CV
        cvPos = mc.pointPosition(f"{spineCRV}.cv[{i}]", world=True)
        controller = util.create.createShape('circle')[0]
        controller = mc.rename(controller, f'neck_0{i+1}_CTL')
        lastGroup = util.create.createGroupStructure(groupStructure,f'neck_0{i+1}_Controls', None)
        mc.parent(controller, lastGroup)
        mc.xform(f'neck_0{i+1}_Controls_' + firstGroup, translation=cvPos)
        controllersList.append(controller)

    #Parent like video
    mc.parent('neck_02_Controls_' + firstGroup, 'neck_01_CTL')
    mc.parent('neck_03_Controls_' + firstGroup, 'neck_02_CTL')
    mc.parent('neck_04_Controls_' + firstGroup, 'neck_03_CTL')
    mc.parent('neck_05_Controls_' + firstGroup, 'neck_04_CTL')

    '''
        8. Select the curve shape
        9. DecomposeMatrix --> InputMatrix   (C_spine01_CTL)  DecomposeMatrix.OutputTranslate to shape.ControlPoints[0]  
        10. Do the same for all the controllers
    '''

    spineCRVShape = mc.listRelatives(spineCRV, shapes=True)[0]
    firstDCMNode = None
    for i in range(len(controllersList)):
        node = mc.createNode('decomposeMatrix', name= f'neck_0{i+1}_CVDCM')
        if i == 0:
            firstDCMNode = node
        mc.connectAttr(controllersList[i] + '.worldMatrix[0]', node + '.inputMatrix')
        mc.connectAttr(node + '.outputTranslate', spineCRVShape + f'.controlPoints[{i}]')


    '''
        ----------------------------------- IK HANDLE TWIST ----------------------------------- 
        1. Activate Advanced Twist Controls on IKHandle (check)
        2. World Up type = Object Rotation Up (Start/End)
        3. Forward Axis = Positive Y
        4. Up Axis = Positive X
        5. Up vector (1,0,0) ---- Up Vector 2 (1,0,0)
        6. World Up Object = spineHip_CTL
        7. World Up Object = spine_05_CTL
    '''


    mc.setAttr(f'{ikHandle}.dTwistControlEnable', 1)
    mc.setAttr(f'{ikHandle}.dWorldUpType', 4) # 4 = "Object Rotation Up (Start/End)"
    mc.setAttr(f'{ikHandle}.dForwardAxis', 2)  # 2 = Positive Y
    mc.setAttr(f'{ikHandle}.dWorldUpAxis', 6)  # 6 = Positive X
    mc.setAttr(f'{ikHandle}.dWorldUpVectorX', 1)
    mc.setAttr(f'{ikHandle}.dWorldUpVectorY', 0)
    mc.setAttr(f'{ikHandle}.dWorldUpVectorZ', 0)
    mc.setAttr(f'{ikHandle}.dWorldUpVectorEndX', 1)
    mc.setAttr(f'{ikHandle}.dWorldUpVectorEndY', 0)
    mc.setAttr(f'{ikHandle}.dWorldUpVectorEndZ', 0)

    mc.connectAttr('neck_01_CTL' + '.worldMatrix[0]', ikHandle + ".dWorldUpMatrix")
    mc.connectAttr('neck_05_CTL' + '.worldMatrix[0]', ikHandle + ".dWorldUpMatrixEnd")


    mc.select(cl=True)
    util.select.setfocusMaya()

#endRegion




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

    for i in range(len(digitsStructures)):
        digitsJoints.append(util.rigging.createDigitsChain(digitsStructures[i]))


    util.select.modifyButtonList(['digitsConnectButton'], True)
    util.select.modifyButtonList(['digitsControlsButton'], True)
    util.select.modifyButtonList(['digitsCreateButton'], False)

    util.select.setfocusMaya()


def createDigitsControls(digitsJoints):
    global digitsLocator
    global listControlsDigits
    global mainParentCTL
    groupStructure = 'GRP;ANIM;SDK;OFFSET'

    for i in range(len(digitsStructures)):
        listControlsDigits.append(util.rigging.createCTLJointList(digitsJoints[i],groupStructure))
        mainParentCTL.append(util.naming.modifyName('replace', listControlsDigits[i][0], '_CTL','_GRP'))

    #Parent controllers and joints
    for i in range(len(digitsJoints)):
        for j in range(len(digitsJoints[i])):
            mc.parentConstraint(listControlsDigits[i][j],digitsJoints[i][j],  mo=True, w=1)
    
    
    #digitsLocator = mc.spaceLocator(n='connect_LOC')[0]
    #util.rigging.addInternalName(digitsLocator, digitsLocator)

    util.select.modifyButtonList(['digitsConnectButton'], True)
    util.select.modifyButtonList(['digitsControlsButton'], False)

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

    util.select.modifyButtonList(['digitsCreateButton','digitsControlsButton','digitsConnectButton','digitsResetButton'], False)
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

    #GET SCOPE
    limbName = None
    for button in limbsRadio:
        if mc.radioButton(button, query=True, select=True):
            limbName = mc.radioButton(button, query=True, label=True)
            break


    #Create limb and duplicate to IK and FK
    limbJoints.append(util.rigging.createLimbChain(limbLocators, limbName))

    util.select.modifyButtonList(['limbCreateButton'], True)
    util.select.modifyButtonList(['limbControlsButton'], True)


def createLimbControls(limbsRadio):
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
    util.select.modifyButtonList(['limbControlsButton'], False)
    print(limbJoints)
    util.select.setfocusMaya()


def restartLimbChain():
    global limbLocators
    global limbJoints
    limbLocators = []
    limbJoints = []
    mc.button('limbLocButton', e=True, en=True)
    util.select.modifyButtonList(['limbCreateButton','limbControlsButton','limbResetButton'], False)
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