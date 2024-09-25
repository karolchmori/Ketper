import maya.cmds as mc


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

def setfocusMaya():
    mc.setFocus("MayaWindow")

#region Massive GET

def getTypeMapsTitle():
    return list(type_mappings.keys())

#getAttributeObject('TEST_001')
def getDefaultAttributes():
    return standardAttributes

#endregion

#region Modify List

def modifyCheckBoxList(elements, value, enabled):
    for el in elements:
        mc.checkBox(el, e=True, v=value, en=enabled)


def modifyButtonList(elements, enabled):
    for el in elements:
        mc.button(el, e=True, en=enabled)

#endregion


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

#region Attribute

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



#endregion


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

#region Filter

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


def filterObjectsTransform(typeTransform, value):
    selectedObjects = mc.ls(selection=True, type='transform')
    filteredObjects = []

    for obj in selectedObjects:
        # Query the rotation values
        valueX = mc.getAttr(obj + "." + typeTransform +"X")
        valueY = mc.getAttr(obj + "." + typeTransform +"Y")
        valueZ = mc.getAttr(obj + "." + typeTransform +"Z")

        # Check if any of the rotation values are not one
        if valueX != value or valueY != value or valueZ != value:
            filteredObjects.append(obj)

    # Print the filtered objects
    #print("Objects with non-zero rotation:", filteredObjects)
    return filteredObjects   


#endregion
