import bpy
import bmesh
import numpy as np
import mathutils

def GetVertexGroup_EDIT_Vertex(bm, index, threshold, bool=True):

    vertexgroup_list = []

    deform = bm.verts.layers.deform.active

    for v in bm.verts:
        vGroup = v[deform]
        if bool:
            if index in vGroup:

                if vGroup[index] >= threshold:
                    vertexgroup_list.append(v)
        else:
            if index in vGroup:
                pass
            else:
                if vGroup[index] >= threshold:
                    vertexgroup_list.append(v)

    return vertexgroup_list


def GetLinkedFace_EDIT_Vertex(bm, vertices):

    linked_faces_set = set()

    for v in vertices:
        for link_face in v.link_faces:
            linked_faces_set.add(link_face)

    return linked_faces_set


def GetFaceFromVerts_EDIT_Vertex(vertices, linkfaces):

    face_set = set()

    for linkface in linkfaces:
        check_counter = 0

        for vert in vertices:
            for link_vert in linkface.verts:
                if vert == link_vert:
                    check_counter += 1

            if len(linkface.verts) == check_counter:
                face_set.add(linkface)

    return face_set



def round_vertex_weight(object, threshold, round_up=1, round_down=0):
    
    bm = bmesh.new()
    bm.from_mesh(object.data)

    bm.verts.layers.deform.verify()
    deform = bm.verts.layers.deform.active


    for v in bm.verts:
        g = v[deform]
        for index, vertex_group in enumerate(object.vertex_groups):
            try:
                weight = g[index]

                if mode == "BOTH":
  
                    if weight > roundup_threshold:
                        g[index] = round_up
                    elif weight < roundown_threshold:
                        g[index] = round_down

            except:
                pass

    bm.to_mesh(object.data)
    bm.free()
    bpy.context.view_layer.update()


def find_center_point(obj):

    pts = [(obj.matrix_world @ v.co) for v in obj.data.vertices]
    center_pt = np.average(pts, 0)

    return center_pt


def moveOrigin(obj, location):

    currentMode = bpy.context.mode

    if currentMode == "EDIT_MESH":
        bpy.ops.object.mode_set(mode='OBJECT')


    location = mathutils.Vector(location)

    ob = obj
    cursor_world_loc = location
    cursor_local_loc = ob.matrix_world.inverted() @ cursor_world_loc

    mat = mathutils.Matrix.Translation(-cursor_local_loc)

    me = ob.data

    me.transform(mat)
    me.update()

    ob.matrix_world.translation = cursor_world_loc

    if currentMode == "EDIT_MESH":
        bpy.ops.object.mode_set(mode='EDIT')

def Unassign_Zero_Weight_From_Group(object):

    currentMode = bpy.context.mode


    object_vertices= object.data.vertices


    object_data = object.data


    selected_vertices = set()

    for object_vertex_group in object.vertex_groups:

        for vertex in object_vertices:

            for G in vertex.groups:
                if G.group == object_vertex_group.index:
                    if G.weight == 0:
                        selected_vertices.add(vertex.index)


        object_vertex_group.remove(list(selected_vertices))


    return len(selected_vertices)
    #self.report({"INFO"}, "Removed %s vertices from vetex group" %(len(selected_vertices)))
















def Seperate_From_VertexGroup(object, threshold):
    
    collection = bpy.data.collections.get(object.name + "_Sliced")

    if not collection:

        collection = bpy.data.collections.new(object.name + "_Sliced")

        for user_collection in object.users_collection:
            user_collection.children.link(collection)



    for mod in object.modifiers:

        if mod.type == "ARMATURE":

            armature_object = mod.object

            if armature_object:
            
                for bone in armature_object.data.bones:

                    if bone.use_deform == True:

                        vg = object.vertex_groups.get(bone.name)

                        if vg:

                            duplicate_obj = object.copy()
                            duplicate_obj.data = duplicate_obj.data.copy()
                            collection.objects.link(duplicate_obj)
                            # normalize_weight(duplicate_obj)

                            duplicate_obj.update_from_editmode()
                            duplicate_obj.name = vg.name

                            bm = bmesh.new()
                            bm.from_mesh(duplicate_obj.data)
                            

                            VG_Vertices = GetVertexGroup_EDIT_Vertex(bm, vg.index, threshold=threshold)

                            if VG_Vertices:
                                VG_LinkedFaces = GetLinkedFace_EDIT_Vertex(bm, VG_Vertices)

                                if VG_LinkedFaces:
                                    VG_Faces = GetFaceFromVerts_EDIT_Vertex(VG_Vertices, VG_LinkedFaces)
                                else:
                                    VG_Faces = set()




                                bm.verts.layers.deform.verify()
                                deform = bm.verts.layers.deform.active

                                newgeometry = bmesh.ops.split(bm, geom=list(VG_Faces))
                                newgeometryface = newgeometry["geom"]

                                VertexGroup_Non=[f for f in bm.faces]
                                VertexGroup_Non = [f for f in VertexGroup_Non if f not in newgeometryface]

                                bmesh.ops.delete(bm, geom=VertexGroup_Non, context="FACES")

                                #Done with the Master Object
                                bm.to_mesh(duplicate_obj.data)
                                bm.free()
                                
                                duplicate_obj.modifiers.clear()
                                
                                origin = find_center_point(duplicate_obj)

                                
                                
                                bpy.context.view_layer.update()
                                mw = duplicate_obj.matrix_world.copy()
                                duplicate_obj.parent = armature_object
                                duplicate_obj.parent_type = "BONE"
                                duplicate_obj.parent_bone = vg.name
                                duplicate_obj.matrix_world = mw
                                if np.isnan(origin).any():
                                    pass
                                else:
                                    moveOrigin(duplicate_obj, origin)

                                    mw = duplicate_obj.matrix_world.copy()
                                    duplicate_obj.parent = armature_object
                                    duplicate_obj.parent_type = "BONE"
                                    duplicate_obj.parent_bone = vg.name













class JTR_OT_Split_Vertex_Group_Into_Objects(bpy.types.Operator):
    bl_idname = "jtr.split_vertex_group_into_objects"
    bl_label = "Split Vertex Group into Objects"
    bl_description = "Split Vertex Group into Objects"
    bl_options = {"REGISTER", "UNDO"}


    threshold: bpy.props.FloatProperty(default=0.5, min=0, max=1)

    def execute(self, context):

        for obj in context.selected_objects:
            Seperate_From_VertexGroup(obj, self.threshold)
            obj.hide_viewport = True

        return {"FINISHED"}

def Menu_Item(self, context):
    self.layout.operator(
        JTR_OT_Split_Vertex_Group_Into_Objects.bl_idname,
        text="Split Vertex Group Into Objects",
        icon='SCULPTMODE_HLT')



classes = [JTR_OT_Split_Vertex_Group_Into_Objects]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_object.append(Menu_Item)

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)


    bpy.types.VIEW3D_MT_object.append(Menu_Item)

if __name__ == "__main__":
    register()
