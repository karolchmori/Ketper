import maya.cmds as cmds
import random


#TODO REVIEW AND TEST
def randomize_face_extrusion(object_name, height_range):
    # Select all the faces of the object
    faces = cmds.ls(cmds.polyListComponentConversion(object_name, toFace=True), flatten=True)
    
    for face in faces:
        # Extrude the face
        cmds.polyExtrudeFacet(face, keepFacesTogether=False, localTranslateZ=random.uniform(height_range[0], height_range[1]))

# Create a plane as an example
#plane = cmds.polyPlane(name="testPlane", width=10, height=10, subdivisionsX=5, subdivisionsY=5)[0]
#sphere = cmds.polySphere(name="testSphere", subdivisionsX=20, subdivisionsY=20)[0]
# Apply the random extrusion to the plane
#randomize_face_extrusion("testPlane", (0.1, 0.5))
#randomize_face_extrusion("testSphere", (0.1, 0.5))

#Get a random position of whatever is needed
def randomPosition(multiplyValue, range, xBool, yBool, zBool):
    newValues = [0,0,0]

    if xBool:
        newValues[0] = random.uniform(range[0], range[1]) * multiplyValue
    if yBool:
        newValues[1] = random.uniform(range[0], range[1]) * multiplyValue
    if zBool:
        newValues[2] = random.uniform(range[0], range[1]) * multiplyValue

    return newValues


def randomNumber(range):
    newValue = 0
    newValue = random.uniform(range[0], range[1])
    
    return newValue

#print(randomPosition([0,0,0], 1, [-2,2], True, False, False))

