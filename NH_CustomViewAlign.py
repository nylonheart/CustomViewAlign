import bpy
from mathutils import Quaternion, Vector
from contextlib import contextmanager

# -----------------------------------------------------------------------------
# Helper Utilities
# -----------------------------------------------------------------------------

_builtin_orientations = {"GLOBAL", "LOCAL", "NORMAL", "GIMBAL", "VIEW", "CURSOR", "PARENT"}


def _axis_quaternion(axis: str) -> Quaternion:
    """Return empirically tuned quaternions per axis."""
    const = {
        "X": Quaternion((0.5, 0.5, 0.5, 0.5)),
        "-X": Quaternion((-0.5, -0.5, 0.5, 0.5)),
        "Y": Quaternion((0.7071, 0.7071, 0, 0)),
        "-Y": Quaternion((0, 0, -0.7071, -0.7071)),
        "Z": Quaternion((1, 0, 0, 0)),
        "-Z": Quaternion((0, 1, 0, 0)),
    }
    return const[axis]


def _unique_orientation_name(base: str) -> str:
    builtin = {"GLOBAL", "LOCAL", "NORMAL", "GIMBAL", "VIEW", "CURSOR", "PARENT"}
    enum_items = bpy.types.TransformOrientationSlot.bl_rna.properties['type'].enum_items
    names = {item.name for item in enum_items if item.identifier not in builtin}

    if base not in names:
        return base
    idx = 1
    while True:
        name = f"{base}_{idx:03}"
        if name not in names:
            return name
        idx += 1



# -----------------------------------------------------------------------------
# Operators
# -----------------------------------------------------------------------------

class VIEW3D_OT_PickTarget(bpy.types.Operator):
    bl_idname = "view3d.pick_target"
    bl_label = "Pick Target"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if obj:
            context.scene.view_align_target = obj
            if obj.type == 'ARMATURE' and obj.mode == 'POSE' and context.active_pose_bone:
                context.scene.view_align_bone = context.active_pose_bone.name
            else:
                context.scene.view_align_bone = ""
            self.report({'INFO'}, f"Picked: {obj.name}")
            return {'FINISHED'}
        self.report({'WARNING'}, "No active object.")
        return {'CANCELLED'}


class VIEW3D_OT_AlignView(bpy.types.Operator):
    bl_idname = "view3d.align_view"
    bl_label = "Align View"
    bl_options = {'REGISTER', 'UNDO'}

    axis: bpy.props.StringProperty()

    def execute(self, context):
        scene = context.scene
        target = scene.view_align_target
        bone_name = scene.view_align_bone

        if not target:
            self.report({'WARNING'}, "No target picked.")
            return {'CANCELLED'}

        if context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "Not in 3D Viewport.")
            return {'CANCELLED'}

        region_3d = context.region_data

        if bone_name and target.type == 'ARMATURE' and target.mode == 'POSE':
            bone = target.pose.bones.get(bone_name)
            if bone:
                mat = target.matrix_world @ bone.matrix
            else:
                mat = target.matrix_world
        else:
            mat = target.matrix_world

        region_3d.view_rotation = mat.to_quaternion() @ _axis_quaternion(self.axis)
        region_3d.view_location = mat.translation
        region_3d.view_distance = max(target.dimensions) * 2

        return {'FINISHED'}


class VIEW3D_OT_CreateTransformOrientation(bpy.types.Operator):
    bl_idname = "view3d.create_orient_custom"
    bl_label = "Create Transform Orientation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        target = scene.view_align_target
        bone_name = scene.view_align_bone

        if not target:
            self.report({'WARNING'}, "No target picked.")
            return {'CANCELLED'}

        name = bone_name if bone_name else target.name
        name = _unique_orientation_name(name)

        prev_mode = target.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        target.select_set(True)
        context.view_layer.objects.active = target
        bpy.ops.transform.create_orientation(name=name, use=True, overwrite=False)
        bpy.ops.object.mode_set(mode=prev_mode)

        self.report({'INFO'}, f"Created orientation: {name}")
        return {'FINISHED'}


# ------------------------------------------------------------------
# Clear all custom Transform Orientations
# ------------------------------------------------------------------
class VIEW3D_OT_ClearCustomOrientations(bpy.types.Operator):
    bl_idname = "view3d.clear_custom_orientations"
    bl_label  = "Clear Custom Orientations"
    bl_options = {'REGISTER', 'UNDO'}

    def _collect_custom_names(self, slot):
        """エラー文を利用してシーン内のカスタム TO 名をリストアップ"""
        try:
            slot.type = ""                       # わざと存在しない値を入れる
        except TypeError as err:
            names = str(err).split("('", 1)[-1].rsplit("')", 1)[0].split("', '")
            return [n for n in names if n not in _builtin_orientations]
        return []

    def execute(self, context):
        slot = context.scene.transform_orientation_slots[0]
        custom_names = self._collect_custom_names(slot)

        if not custom_names:
            self.report({'INFO'}, "No custom orientations found.")
            return {'CANCELLED'}

        removed = 0
        for name in custom_names:
            slot.type = name
            try:
                bpy.ops.transform.delete_orientation()   # 引数なしで OK
                removed += 1
            except RuntimeError:
                pass                                     # 失敗は無視

        slot.type = 'GLOBAL'                             # 後始末
        self.report({'INFO'}, f"Removed {removed} custom orientations.")
        return {'FINISHED'}




# -----------------------------------------------------------------------------
# Panel
# -----------------------------------------------------------------------------

class VIEW3D_PT_CustomViewAlign(bpy.types.Panel):
    bl_label = "Custom View Align"
    bl_idname = "VIEW3D_PT_custom_view_align"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Nylonheart'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.operator("view3d.pick_target", text="Pick Target", icon='EYEDROPPER')

        target_label = scene.view_align_bone if scene.view_align_bone else (scene.view_align_target.name if scene.view_align_target else "None")
        layout.label(text=f"Picked: {target_label}")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("view3d.align_view", text="-Y").axis = '-Y'
        row.operator("view3d.align_view", text="+Y").axis = 'Y'
        row = col.row(align=True)
        row.operator("view3d.align_view", text="X").axis = 'X'
        row.operator("view3d.align_view", text="-X").axis = '-X'
        row = col.row(align=True)
        row.operator("view3d.align_view", text="Z").axis = 'Z'
        row.operator("view3d.align_view", text="-Z").axis = '-Z'

        box = layout.box()
        box.label(text="Custom Transform Orientation")
        row = box.row(align=True)
        row.operator("view3d.create_orient_custom", text="Create", icon='PLUS')
        row.operator("view3d.clear_custom_orientations", text="Clear", icon='TRASH')

# -----------------------------------------------------------------------------
# Registration
# -----------------------------------------------------------------------------

classes = (
    VIEW3D_OT_PickTarget,
    VIEW3D_OT_AlignView,
    VIEW3D_OT_CreateTransformOrientation,
    VIEW3D_OT_ClearCustomOrientations,
    VIEW3D_PT_CustomViewAlign,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.view_align_target = bpy.props.PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.view_align_bone = bpy.props.StringProperty()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.view_align_target
    del bpy.types.Scene.view_align_bone

if __name__ == "__main__":
    register()
