import maya.cmds as mc
import importlib
import re
import json
import ElementsUI as elUI
import maya.api.OpenMaya as om2

importlib.reload(elUI)

# Initialize a single list to collect results
type_mappings = {
    'Camera': 'camera',
    'Curve': 'nurbsCurve',
    # Deformers
    'Deformers': ['deformer', 'blendShape', 'lattice', 'cluster', 'skinCluster'],
    # Rigid and Soft Bodies
    'Dynamics': ['rigidBody', 'softBody', 'particle', 'fluid', 'emitter', 'field'],
    'Hair and Fur': ['hairSystem', 'fur'],
    # IK and Constraints
    'IK and Constraints': ['ikHandle', 'ikSplineHandle', 'constraint'],
    'Joint': 'joint',
    # Maya Light Types
    'Lights Maya': ['light', 'pointLight', 'directionalLight', 'spotLight', 'ambientLight'],
    # Arnold Light Types
    'Lights Arnold': ['aiLight', 'aiAreaLight', 'aiSkyDomeLight', 'aiSpotLight', 'aiPointLight'],
    'Locator': 'locator',
    # Meshes and Surfaces
    'Meshes': ['mesh', 'subdiv', 'poly'],
    'Surface': 'nurbsSurface'
}


standardAttributes = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']

attributeMapping = {
    'tx': 'translateX',
    'ty': 'translateY',
    'tz': 'translateZ',
    'rx': 'rotateX',
    'ry': 'rotateY',
    'rz': 'rotateZ',
    'sx': 'scaleX',
    'sy': 'scaleY',
    'sz': 'scaleZ',
    'v': 'visibility'
}


#region Files

def createFile(filename, information):
    # Convert the selection list to JSON format for easy storage
    with open(filename, 'w') as file:
        json.dump(information, file)

def readFile(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    # Select the objects listed in the file
    return data
#endregion


#region Naming

def notNumber(text):
    pattern = r'\d'
    return not re.search(pattern, text)

#notNumber('123A')

def addPrefix(text, addition):
    modifiedText = addition + text
    return modifiedText

def addSuffix(text, addition):
    modifiedText = text + addition
    return modifiedText

def replaceText(textOriginal, textOld, textNew):
    modifiedText = textOriginal.replace(textOld, textNew)
    return modifiedText

#print(replaceText('Hello_oldWorld','old','new'))


def fillNumber(number, fillchar, totalLen, side):
    if side == 'R':
        modifiedText = str(number).rjust(totalLen, fillchar)
    elif side == 'L':
        modifiedText = str(number).ljust(totalLen, fillchar)
    return modifiedText

#print(fillNumber(5,'*',4,'L'))

def generateLetterByNumber(arrayNumber):
    modifiedText = ''
    for number in arrayNumber:
        word = chr(65 + number - 1)
        modifiedText = modifiedText + word
    return modifiedText
#print(generateLetterByNumber([1, 2, 3]))

def generateArrayColumns(value, columnNumber):
    finalArray = []

    for i in range(columnNumber):
        finalArray.append(value)

    return finalArray

#enerateArrayColumns(1,5)

def getArrayColumnsByPosition(array, position, valueStart, valueLimit):

    for i in range(position - 1):
        array = getNextNumArray(array, valueStart, valueLimit)
        #print('Position: ', i )
        #print('Array: ', array)
    return array


#I only want to change it once, give an array,  give me back the next number
def getNextNumArray(array, valueStart, valueLimit):
    lastColumn = len(array) - 1
    limitBool = False

    for i in range(len(array)):
        currentColumn = lastColumn - i

        if array[currentColumn] + 1 > valueLimit: #If its bigger than the limit will change the left column
            #If the column exceeds the valueLimit, do nothing and check next column
            limitBool = True
            #print('Exceeds in column: ', currentColumn)
        else:
            array[currentColumn] = array[currentColumn] + 1

            if limitBool:
                for j in range(lastColumn - currentColumn):
                    j = lastColumn - j
                    array[j] = valueStart
                    #print("Will modify column: ", j)

            break
    return array




#I only want to change it once, give an array,  give me back the last number
def getLastNumArray(array, valueStart, valueLimit):
    lastColumn = len(array) - 1
    limitBool = False

    for i in range(len(array)):
        currentColumn = lastColumn - i

        if array[currentColumn] - 1 < valueLimit: #If its bigger than the limit will change the left column
            #If the column exceeds the valueLimit, do nothing and check next column
            limitBool = True
            #print('Exceeds in column: ', currentColumn)
        else:
            array[currentColumn] = array[currentColumn] - 1

            if limitBool:
                for j in range(lastColumn - currentColumn):
                    j = lastColumn - j
                    array[j] = valueStart
                    #print("Will modify column: ", j)

            break
    return array


#print(getLastNumArray([1, 1, 4, 1, 1], 4, 1))


#endregion

#region Intersection

def checkTouchingObjList(selectedObjects):
    touched = set()  # Keeps track of objects that have already been checked
    finalObjects = []

    for i in range(len(selectedObjects)):
        obj1 = selectedObjects[i]
        for j in range(i + 1, len(selectedObjects)):
            obj2 = selectedObjects[j]
            if obj2 in touched:
                break
            if checkIntersectionBBox(obj1, obj2):
                finalObjects.append((obj2))
                touched.add(obj2)
                break  # Move to the next object after finding a touching pair
    return finalObjects



def getDagPath(node_name):
    """
    Get the MDagPath for a given node name: provides a way to navigate the scene graph, accounting for transformations and hierarchy
    """
    selection_list = om2.MSelectionList()
    selection_list.add(node_name)
    try:
        dag_path = selection_list.getDagPath(0)
        return dag_path
    except:
        raise ValueError(f"Could not get MDagPath for {node_name}. Ensure it is a mesh.")

def getVertexPosition(mesh):
    dag_path = getDagPath(mesh)
    mesh_fn = om2.MFnMesh(dag_path)

    vertex_positions = []
    for i in range(mesh_fn.numVertices):
        point = mesh_fn.getPoint(i, om2.MSpace.kWorld)
        vertex_positions.append(point)
        
    return vertex_positions

def getFaceBoundaries(mesh):
    """ Get world space boundaries of faces for a given mesh """

    dag_path = getDagPath(mesh)
    mesh_fn = om2.MFnMesh(dag_path)
    
    face_boundaries = []
    for face_idx in range(mesh_fn.numPolygons):
        face_vertices = mesh_fn.getPolygonVertices(face_idx)
        world_coords = [mesh_fn.getPoint(vidx, om2.MSpace.kWorld) for vidx in face_vertices]
        
        if not world_coords:
            continue
        
        x_coords = [pt.x for pt in world_coords]
        y_coords = [pt.y for pt in world_coords]
        z_coords = [pt.z for pt in world_coords]
        
        min_x = min(x_coords)
        max_x = max(x_coords)
        min_y = min(y_coords)
        max_y = max(y_coords)
        min_z = min(z_coords)
        max_z = max(z_coords)
        
        face_boundaries.append((min_x, max_x, min_y, max_y, min_z, max_z))
    
    return face_boundaries

def checkIntersectionVertexFaceB(point, bounds):
    """ Check if a point is within the bounds of a face """
    min_x, max_x, min_y, max_y, min_z, max_z = bounds
    if (min_x <= point.x <= max_x) and (min_y <= point.y <= max_y) and (min_z <= point.z <= max_z):
        return True
    else:
        return False
    
def checkTouchingObjects(obj1, obj2):
    """ Check if any vertex of obj1 is touching any face of obj2 """
    vertices = getVertexPosition(obj1)
    faces = getFaceBoundaries(obj2)
    
    for vertex in vertices:
        for bounds in faces:
            if checkIntersectionVertexFaceB(vertex, bounds):
                #print(f"Vertex {vertex} of {obj1} is touching a face of {obj2}")
                return True
    
    #print(f"No touching detected between {obj1} and {obj2}")
    return False

 #Check if two objects Bounding Box intercept
def checkIntersectionBBox(mesh1, mesh2):
    """
    Checks if the bounding boxes of two meshes intersect.
    """
    bbox1 = mc.exactWorldBoundingBox(mesh1)
    bbox2 = mc.exactWorldBoundingBox(mesh2)

    xmin1, ymin1, zmin1, xmax1, ymax1, zmax1 = bbox1
    xmin2, ymin2, zmin2, xmax2, ymax2, zmax2 = bbox2
    
    # Check for intersection
    if (xmin1 <= xmax2 and xmax1 >= xmin2 and
        ymin1 <= ymax2 and ymax1 >= ymin2 and
        zmin1 <= zmax2 and zmax1 >= zmin2):
        return True
    else:
        return False

#print(checkIntersectionBBox('pCube1', 'pCube2'))

#endregion


#region Select

def modifyCheckBoxList(elements, value, enabled):
    for el in elements:
        mc.checkBox(el, e=True, v=value, en=enabled)


def modifyButtonList(elements, enabled):
    for el in elements:
        mc.button(el, e=True, en=enabled)



def checkIfGeometry(selectedObjects):
    # Check if the selection contains vertices or faces
    isVertex = mc.filterExpand(selectedObjects, selectionMask=31)  # Vertex
    isEdge = mc.filterExpand(selectedObjects, selectionMask=32)  # Vertex
    isFace = mc.filterExpand(selectedObjects, selectionMask=34)  # Face
    isVerticeFace = mc.filterExpand(selectedObjects, selectionMask=37)  # Face
    #35 UV
    #36 Components General

    if isVertex or isFace or isEdge or isVerticeFace:
        return False
    else:
        return True


def filterFlattenSelection(selectedObjects):
    # Check if the selection contains vertices or faces
    isVertex = mc.filterExpand(selectedObjects, selectionMask=31)  # Vertex
    isEdge = mc.filterExpand(selectedObjects, selectionMask=32)  # Vertex
    isFace = mc.filterExpand(selectedObjects, selectionMask=34)  # Face
    isVerticeFace = mc.filterExpand(selectedObjects, selectionMask=37)  # Face
    #35 UV
    #36 Components General

    if isVertex or isFace or isEdge or isVerticeFace:
        selectedObjects = mc.ls(selectedObjects, flatten=True)
    
    return selectedObjects

def getSelectedChannels(selectedObject):
    # Get the selected object
    fullNameChannels = []

    # Get the selected channels/attributes in the Channel Box
    channel_box = 'mainChannelBox'
    selected_channels = mc.channelBox(channel_box, query=True, sma=True)

    for channel in selected_channels:
        if channel in attributeMapping:
            fullNameChannels.append(attributeMapping[channel])
        else:
            fullNameChannels.append(channel)

    return fullNameChannels


def getValueField(obj, nameAtt):
    value = mc.getAttr(f'{obj}.{nameAtt}')
    return value

def getTypeField(obj, nameAtt):
    if mc.attributeQuery(nameAtt, node=obj, exists=True):
        attrType = mc.attributeQuery(nameAtt, node=obj, attributeType=True)
    
    return attrType

def getDefaultValueField(obj, nameAtt):
    defaultValue = mc.attributeQuery(nameAtt, node=obj, listDefault=True)
    if isinstance(defaultValue, list):
        # If the value is a list, extract the first element
        return defaultValue[0]
    else:
        # If it's not a list, assume it's already a float
        return defaultValue
    
def getMaxValueField(obj, nameAtt):
    maxExists = mc.attributeQuery(nameAtt, node=obj, mxe=True)
    
    if maxExists:
        maxValue = mc.attributeQuery(nameAtt, node=obj, max=True)
        if isinstance(maxValue, list):
            # If the value is a list, extract the first element
            return maxValue[0]
        else:
            # If it's not a list, assume it's already a float
            return maxValue

def getMinValueField(obj, nameAtt):
    minExists = mc.attributeQuery(nameAtt, node=obj, mne=True)
    
    if minExists:
        minValue = mc.attributeQuery(nameAtt, node=obj, min=True)
        if isinstance(minValue, list):
            # If the value is a list, extract the first element
            return minValue[0]
        else:
            # If it's not a list, assume it's already a float
            return minValue
    


def getAttributeObject(obj):
    allAttr = mc.listAnimatable(obj)

    # Extract only the attribute names
    attrNames = [attr.split('.')[-1] for attr in allAttr]
    #print(attrNames)
    
    return attrNames

#getAttributeObject('TEST_001')
def getDefaultAttributes():
    return standardAttributes


def filterObjectsScale():
    selectedObjects = mc.ls(selection=True, type='transform')
    filteredObjects = []

    for obj in selectedObjects:
        # Query the rotation values
        scaleX = mc.getAttr(obj + ".scaleX")
        scaleY = mc.getAttr(obj + ".scaleY")
        scaleZ = mc.getAttr(obj + ".scaleZ")

        # Check if any of the rotation values are not one
        if scaleX != 1 or scaleY != 1 or scaleZ != 1:
            filteredObjects.append(obj)

    # Print the filtered objects
    #print("Objects with non-zero rotation:", filteredObjects)
    return filteredObjects   



def filterObjectsTranslation():
    selectedObjects = mc.ls(selection=True, type='transform')
    filteredObjects = []

    for obj in selectedObjects:
        # Query the rotation values
        translateX = mc.getAttr(obj + ".translateX")
        translateY = mc.getAttr(obj + ".translateY")
        translateZ = mc.getAttr(obj + ".translateZ")

        # Check if any of the rotation values are not zero
        if translateX != 0 or translateY != 0 or translateZ != 0:
            filteredObjects.append(obj)

    # Print the filtered objects
    #print("Objects with non-zero rotation:", filteredObjects)
    return filteredObjects   


def filterObjectsRotation():
    selectedObjects = mc.ls(selection=True, type='transform')
    filteredObjects = []

    for obj in selectedObjects:
        # Query the rotation values
        rotateX = mc.getAttr(obj + ".rotateX")
        rotateY = mc.getAttr(obj + ".rotateY")
        rotateZ = mc.getAttr(obj + ".rotateZ")

        # Check if any of the rotation values are not zero
        if rotateX != 0 or rotateY != 0 or rotateZ != 0:
            filteredObjects.append(obj)

    # Print the filtered objects
    #print("Objects with non-zero rotation:", filteredObjects)
    return filteredObjects   


def getOutlinerOrder(selectedObjects, reverseBool):
    # Retrieve the selected objects in the Outliner order
    selectedObjects = mc.ls(selection=True, type='transform')
    
    # Retrieve the hierarchy for selected objects
    allTransforms = mc.ls(dag=True, type='transform')
    
    # Create a dictionary to map each object to its index in the Outliner order
    indexDict = {name: index for index, name in enumerate(allTransforms)}
    
    # Sort the selected objects based on their index in the Outliner order
    sortedObjects = sorted(selectedObjects, key=lambda obj: indexDict.get(obj, float('inf')), reverse=reverseBool)
    return sortedObjects


def getSelectedValuesDoubleList(selectedList):
    selectedValues = mc.textScrollList(selectedList, query=True, allItems=True)
    return selectedValues

# WE WON'T USE IT BECAUSE we usually select everything in the scene and filter the selection with selectByNameAndList
def selectByName(word):
    objects = mc.ls(['*'+word+'*', '*:*'+word+'*'], long=True, type='transform')
    #objects = mc.ls('*'+ word+'*', long=True, type='transform') #I use this one because I don't want to select the parent
    #objects = mc.ls('*'+ word+'*')
    #transform = mc.listRelatives(objects,type='transform',p=True)
    #objects.extend(transform)
    #objects = mc.listRelatives(objects, parent=True, fullPath=True)
    return objects


def selectByNameAndList(word):
    objects = mc.ls(['*'+word+'*', '*:*'+word+'*'], selection=True, long=True, type='transform')
    #objects = mc.ls('*'+ word+'*', selection=True, long=True, type='transform')
    #transform = mc.listRelatives(objects,type='transform',p=True)
    #objects.extend(transform)
    return objects



def getTypeMapsTitle():
    return list(type_mappings.keys())

def filterByType(typeList):
    selectedObjects = mc.ls(selection=True)  # Get currently selected objects
    #print("Selected Objects:", selectedObjects)
    filteredObjects = []

    for obj in selectedObjects:
        objType = mc.nodeType(obj)

        matched = False

        # Check if the object type matches any of the types in typeList
        for typeName in typeList:
            mappedTypes = type_mappings.get(typeName, [])
            # Ensure mappedTypes is a list for uniformity
            if isinstance(mappedTypes, str):
                mappedTypes = [mappedTypes]
            
            if objType in mappedTypes:
                filteredObjects.append(obj)
                matched = True
                break  # Once found, no need to check other types for this object
        
        if matched:
            continue  # Skip shape checking if the object type already matched
        
        # Then, check the shape types if the object isn't matched as a transform type
        shapes = mc.listRelatives(obj, shapes=True, fullPath=True)
        
        if shapes:
            for shape in shapes:
                objType = mc.nodeType(shape)
                #print(f"Type: {objType}")
                
                # Check if the type of the shape matches any of the types in typeList
                for typeName in typeList:
                    mappedTypes = type_mappings.get(typeName, [])
                    if isinstance(mappedTypes, str):
                        mappedTypes = [mappedTypes]

                    if objType in mappedTypes:
                        filteredObjects.append(obj)
                        break  # Once found, no need to check other types for this object
                
    #print(filteredObjects)
    return filteredObjects


def filterLocator(initialList):
    arnoldLights = ['aiAreaLight', 'aiSkyDomeLight', 'aiPointLight', 'aiSpotLight', 'aiMeshLight']
    filteredList = []

    for item in initialList:
        if mc.nodeType(item) not in arnoldLights:
            filteredList.append(item)
    return filteredList


def filterDefaultCam(initialList):
    defaultCameras = ['persp', 'top', 'front', 'side','perspShape','topShape','frontShape','sideShape']
    filteredList = []

    for item in initialList:
        cam_name = item.split('|')[-1]

        if cam_name not in defaultCameras:
            #print(cam_name)
            filteredList.append(item)
    return filteredList

#endregion


#region Creation
def createShape(shape):

    if shape == 'arrow':
        mc.curve(d=1, p=[(0,0,-1),(3,0,-1),(3,0,-2),(5,0,0),(3,0,2),(3,0,1),(0,0,1),(0,0,-1)])
    elif shape == 'square':
        mc.curve(d=1, p=[(-1, 0, -1), (-1, 0, 1), (1, 0, 1), (1, 0, -1), (-1, 0, -1)])
    elif shape == 'triangle':
        mc.curve(d=1, p=[(1,0,-1),(-1,0,-1),(0,0,1),(1,0,-1)])
    elif shape == 'rhombus':
        mc.curve(d=1, p=[(0,0,1),(0.75,0,0),(0,0,-1),(-0.75,0,0),(0,0,1)])
    elif shape == 'circle':
        mc.circle(nr=(0,1,0))
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

    elif shape == 'sphere':

        firstCircle = mc.circle(nr=(0,1,0))
        secondCircle = mc.circle(nr=(1,0,0))
        thirdCircle = mc.circle(nr=(0,0,1))

        mc.select(firstCircle, secondCircle, thirdCircle)
        
        combineObjects()

    else:
        print("Unknown control shape.")
        return
    

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

#endregion