import bpy
from mathutils import Quaternion

class VIEW3D_PT_CustomPanel(bpy.types.Panel):
    bl_label = "Custom View Align"
    bl_idname = "VIEW3D_PT_custom_view_align"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Nylonheart'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.operator("view3d.pick_object", text="Pick Object (Click)", icon="EYEDROPPER")
        layout.label(text=f"Picked Target: {scene.view_align_target if scene.view_align_target else 'None'}")

        row = layout.row()
        row.operator("view3d.align_view", text="-Y").axis = '-Y'
        row.operator("view3d.align_view", text="+Y").axis = 'Y'

        row = layout.row()
        row.operator("view3d.align_view", text="X").axis = 'X'
        row.operator("view3d.align_view", text="-X").axis = '-X'

        row = layout.row()
        row.operator("view3d.align_view", text="Z").axis = 'Z'
        row.operator("view3d.align_view", text="-Z").axis = '-Z'

        layout.separator()
        layout.operator("view3d.create_transform_orientation", text="Create / Switch Transform Orientation", icon="OBJECT_ORIGIN")

class VIEW3D_OT_PickObject(bpy.types.Operator):
    bl_idname = "view3d.pick_object"
    bl_label = "Pick Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if obj:
            context.scene.view_align_target = obj.name
            self.report({'INFO'}, f"Picked Target: {obj.name}")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "No object is selected.")
            return {'CANCELLED'}

class VIEW3D_OT_AlignView(bpy.types.Operator):
    bl_idname = "view3d.align_view"
    bl_label = "Align View"
    bl_options = {'REGISTER', 'UNDO'}
    axis: bpy.props.StringProperty()

    def execute(self, context):
        obj_name = context.scene.view_align_target
        if not obj_name or obj_name not in bpy.data.objects:
            self.report({'WARNING'}, "No object is selected.")
            return {'CANCELLED'}

        obj = bpy.data.objects[obj_name]
        region_3d = context.space_data.region_3d

        if self.axis == '-Y':
            region_3d.view_rotation = obj.matrix_world.to_quaternion() @ Quaternion((0.7071, 0.7071, 0, 0))
        elif self.axis == 'Y':
            region_3d.view_rotation = obj.matrix_world.to_quaternion() @ Quaternion((0, 0, -0.7071, -0.7071))
        elif self.axis == 'X':
            region_3d.view_rotation = obj.matrix_world.to_quaternion() @ Quaternion((0.5, 0.5, 0.5, 0.5))
        elif self.axis == '-X':
            region_3d.view_rotation = obj.matrix_world.to_quaternion() @ Quaternion((-0.5, -0.5, 0.5, 0.5))
        elif self.axis == 'Z':
            region_3d.view_rotation = obj.matrix_world.to_quaternion() @ Quaternion((1, 0, 0, 0))
        elif self.axis == '-Z':
            region_3d.view_rotation = obj.matrix_world.to_quaternion() @ Quaternion((0, 1, 0, 0))

        return {'FINISHED'}

class VIEW3D_OT_CreateTransformOrientation(bpy.types.Operator):
    bl_idname = "view3d.create_transform_orientation"
    bl_label = "Create or Switch Transform Orientation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj_name = context.scene.view_align_target
        if not obj_name or obj_name not in bpy.data.objects:
            self.report({'WARNING'}, "No object is selected.")
            return {'CANCELLED'}

        obj = bpy.data.objects[obj_name]

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        bpy.ops.transform.create_orientation(name=obj_name, use=True, overwrite=True)

        return {'FINISHED'}

def register_properties():
    bpy.types.Scene.view_align_target = bpy.props.StringProperty(name="View Align Target")

def unregister_properties():
    del bpy.types.Scene.view_align_target

def register():
    register_properties()
    bpy.utils.register_class(VIEW3D_PT_CustomPanel)
    bpy.utils.register_class(VIEW3D_OT_PickObject)
    bpy.utils.register_class(VIEW3D_OT_AlignView)
    bpy.utils.register_class(VIEW3D_OT_CreateTransformOrientation)

def unregister():
    unregister_properties()
    bpy.utils.unregister_class(VIEW3D_PT_CustomPanel)
    bpy.utils.unregister_class(VIEW3D_OT_PickObject)
    bpy.utils.unregister_class(VIEW3D_OT_AlignView)
    bpy.utils.unregister_class(VIEW3D_OT_CreateTransformOrientation)

if __name__ == "__main__":
    register()