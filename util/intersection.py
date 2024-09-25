import maya.cmds as mc
import maya.api.OpenMaya as om2

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
