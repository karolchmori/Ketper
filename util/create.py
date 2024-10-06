import maya.cmds as mc


#region Creation

#Ends selecting the last group
def createGroupStructure(text, mainName, firstParent):
    splitText = text.split(';')
    lastName = mainName+'_'+splitText[0]
    if firstParent:
        mc.group(em=True, name= lastName, parent=firstParent)
    else:
        mc.group(em=True, name=lastName)

    for i in range(1,len(splitText)):
        item = splitText[i].strip()
        #print(item)
        mc.group(em=True, name= mainName+'_'+item, parent=lastName)
        lastName = mainName+'_'+item

    return lastName    

def createTextCurves(text):
    textObject = mc.textCurves(f = 'Arial', t = text)
    # Initialize a list to hold the curves
    curves = []
    parents = []
    groups = mc.listRelatives(textObject)
    for group in groups:
        shape = mc.listRelatives(group)
        parent = mc.listRelatives(shape, parent=True)
        parents.extend(parent)
        mc.parent(shape, world=True)
        mc.FreezeTransformations()
        mc.delete(ch=1)
        curves.extend(shape)

    mc.select(curves)        
    result = combineObjects()

    mainParent = mc.listRelatives(parent[0], parent=True)
    mc.delete(mainParent)

#createTextCurves('TEST')

def createShape(shape):
    result = None

    if shape == 'arrow':
        result = mc.curve(d=1, p=[(0,0,-1),(3,0,-1),(3,0,-2),(5,0,0),(3,0,2),(3,0,1),(0,0,1),(0,0,-1)])
    elif shape == 'square':
        result = mc.curve(d=1, p=[(-1, 0, -1), (-1, 0, 1), (1, 0, 1), (1, 0, -1), (-1, 0, -1)])
    elif shape == 'triangle':
        result = mc.curve(d=1, p=[(1,0,-1),(-1,0,-1),(0,0,1),(1,0,-1)])
    elif shape == 'rhombus':
        result = mc.curve(d=1, p=[(0,0,1),(0.75,0,0),(0,0,-1),(-0.75,0,0),(0,0,1)])
    elif shape == 'circle':
        result = mc.circle(nr=(0,1,0))
    elif shape == 'compass':
        result = mc.circle(nr=(0,1,0), d=1, s=18)
        mc.move(0, 0, 1.5, result[0]+'.cv[9]', absolute=True)
    elif shape == 'cube': #Create first the points
        myCube = mc.curve(d=1,p=[(0,0,0),(1,0,0),(1,0,1),(0,0,1),(0,0,0),
                                   (0,1,0),(1,1,0),(1,0,0),(1,1,0),
                                   (1,1,1),(1,0,1),(1,1,1),
                                   (0,1,1),(0,0,1),(0,1,1),(0,1,0)])
 
        mc.CenterPivot()
        mc.xform(myCube,t=(-.5,-.5,-.5))
        mc.select(myCube)
        mc.FreezeTransformations()
        mc.rename("curve")
        mc.delete(ch=1)
        result = myCube

    elif shape == 'sphere':

        firstCircle = mc.circle(nr=(0,1,0))
        secondCircle = mc.circle(nr=(1,0,0))
        thirdCircle = mc.circle(nr=(0,0,1))

        mc.select(firstCircle, secondCircle, thirdCircle)
        
        result = combineObjects()

    else:
        print("Unknown control shape.")
        
    return result[0]
    

# Combine different shapes into one (has different shapes)
def combineObjects():
    # get shape node of selected curves
    selectedObjects = mc.ls(selection=True)
    objShapes = mc.listRelatives(selectedObjects, s=True)
    # freeze transforms of selected curves
    mc.makeIdentity(selectedObjects, apply=True, t=True, r=True, s=True)
    # create null transform to parent shapes to
    holder = mc.group(em=True, name="newObject")
    # parent shapes to null
    mc.parent(objShapes, holder, s=True, r=True)
    # remove old transforms
    mc.delete(selectedObjects)

    mc.makeIdentity(holder, apply=True, t=True, r=True, s=True)
    
    mc.select(holder)
    movePivot('neutral','neutral','neutral')

    return holder


def changeColorShape(slider):
    color = mc.colorIndexSliderGrp(slider, q=True, value=True)
    sel = mc.ls(selection=True, long=True)

    for obj in sel:
        mc.setAttr(obj + '.overrideEnabled', 1)
        mc.setAttr(obj + '.overrideColor', color - 1)


def movePivot(choiceX, choiceY, choiceZ):

    sel = mc.ls(selection=True)

    for obj in sel:
        objBoundaries = mc.exactWorldBoundingBox(obj)
        # min_x, min_y, min_z, max_x, max_y, max_z = bbox

        valueX = getMinMax(objBoundaries[0],objBoundaries[3],choiceX)
        valueY = getMinMax(objBoundaries[1],objBoundaries[4],choiceY)
        valueZ = getMinMax(objBoundaries[2],objBoundaries[5],choiceZ)

        #print(valueX,valueY,valueZ)
        mc.xform(obj, pivots=[valueX, valueY, valueZ], ws=True)

def getMinMax(minimun,maximun,choice):
    value = 0
    if choice == 'negative':
        value = minimun
    elif choice == 'neutral':
        value = (minimun + maximun) / 2
    elif choice == 'positive':
        value = maximun

    return value