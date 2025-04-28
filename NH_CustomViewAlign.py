import bpy
from mathutils import Quaternion

# -----------------------------------------------------------------------------
# Helper utilities
# -----------------------------------------------------------------------------

_BUILTIN_ORIENTS = {"GLOBAL", "LOCAL", "NORMAL", "GIMBAL", "VIEW", "CURSOR", "PARENT"}


def _axis_quaternion(axis: str) -> Quaternion:
    """Return the empirically‑tuned quaternions theユーザー confirmed for each axis."""
    lut = {
        "X": Quaternion((0.5, 0.5, 0.5, 0.5)),
        "-X": Quaternion((-0.5, -0.5, 0.5, 0.5)),
        "Y": Quaternion((0.7071, 0.7071, 0, 0)),
        "-Y": Quaternion((0, 0, -0.7071, -0.7071)),
        "Z": Quaternion((1, 0, 0, 0)),
        "-Z": Quaternion((0, 1, 0, 0)),
    }
    return lut[axis]


def _unique_orientation_name(base: str) -> str:
    """Return a unique orientation name not yet used in the scene."""
    names = {slot.custom_orientation.name for slot in bpy.context.scene.transform_orientation_slots if slot.custom_orientation}
    if base not in names:
        return base
    idx = 1
    while True:
        candidate = f"{base}_{idx:03}"
        if candidate not in names:
            return candidate
        idx += 1

# -----------------------------------------------------------------------------
# Operators
# -----------------------------------------------------------------------------

class VIEW3D_OT_PickTarget(bpy.types.Operator):
    bl_idname = "view3d.pick_target"
    bl_label = "Pick Target"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report({"WARNING"}, "No active object.")
            return {'CANCELLED'}

        context.scene.view_align_target = obj

        if obj.type == 'ARMATURE' and context.active_pose_bone:
            context.scene.view_align_bone = context.active_pose_bone.name
        else:
            context.scene.view_align_bone = ""

        self.report({"INFO"}, f"Picked: {obj.name}")
        return {'FINISHED'}


class VIEW3D_OT_AlignView(bpy.types.Operator):
    bl_idname = "view3d.align_view"
    bl_label = "Align View"
    bl_options = {"REGISTER", "UNDO"}

    axis: bpy.props.StringProperty()

    def execute(self, context):
        scene = context.scene
        target = scene.view_align_target
        bone_name = scene.view_align_bone

        if not target:
            self.report({"WARNING"}, "No target picked.")
            return {'CANCELLED'}

        if context.region_data is None:
            self.report({"WARNING"}, "Not in a 3D viewport region.")
            return {'CANCELLED'}

        # Determine matrix (object or bone)
        if bone_name and target.type == 'ARMATURE' and target.pose:
            bone = target.pose.bones.get(bone_name)
            mat = target.matrix_world @ bone.matrix if bone else target.matrix_world
        else:
            mat = target.matrix_world

        r3d = context.region_data
        r3d.view_rotation = mat.to_quaternion() @ _axis_quaternion(self.axis)
        r3d.view_location = mat.translation
        r3d.view_distance = max(target.dimensions) * 2
        return {'FINISHED'}


class VIEW3D_OT_CreateTransformOrientation(bpy.types.Operator):
    bl_idname = "view3d.create_orient_custom"
    bl_label = "Create Transform Orientation"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        target = scene.view_align_target
        bone_name = scene.view_align_bone

        if not target:
            self.report({"WARNING"}, "No target picked.")
            return {'CANCELLED'}

        name = _unique_orientation_name(bone_name if bone_name else target.name)

        if bone_name and target.type == 'ARMATURE':
            # Ensure pose mode
            if target.mode != 'POSE':
                bpy.ops.object.mode_set(mode='POSE')
            bone = target.pose.bones.get(bone_name)
            if not bone:
                self.report({"WARNING"}, "Bone not found.")
                return {'CANCELLED'}
            # Select only this bone
            for b in target.pose.bones:
                b.bone.select = False
            bone.bone.select = True
            target.data.bones.active = bone.bone
            bpy.ops.transform.create_orientation(name=name, use=True, overwrite=False)
            self.report({"INFO"}, f"Orientation from bone: {name}")
            return {'FINISHED'}
        else:
            # Object orientation
            prev_mode = target.mode
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            target.select_set(True)
            context.view_layer.objects.active = target
            bpy.ops.transform.create_orientation(name=name, use=True, overwrite=False)
            bpy.ops.object.mode_set(mode=prev_mode)
            self.report({"INFO"}, f"Orientation from object: {name}")
            return {'FINISHED'}


class VIEW3D_OT_ClearCustomOrientations(bpy.types.Operator):
    """Remove all custom Transform Orientations in the current Blend file"""
    bl_idname = "view3d.clear_custom_orientations"
    bl_label = "Clear Custom Orientations"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # Gather custom orientation objects referenced by the scene
        custom_orients = {
            slot.custom_orientation
            for slot in context.scene.transform_orientation_slots
            if slot.custom_orientation and slot.custom_orientation.name not in _BUILTIN_ORIENTS
        }

        if not custom_orients:
            self.report({"INFO"}, "No custom orientations found.")
            return {'CANCELLED'}

        # Find an active 3D View for the operator context
        area_3d = None
        region_win = None
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area_3d = area
                for region in area.regions:
                    if region.type == 'WINDOW':
                        region_win = region
                        break
                if region_win:
                    break
        if not area_3d or not region_win:
            self.report({"WARNING"}, "No 3D View area found to run operator.")
            return {'CANCELLED'}

        removed = 0
        for orient in list(custom_orients):
            try:
                # Activate the orientation in the temp override
                with context.temp_override(area=area_3d, region=region_win):
                    context.scene.transform_orientation_slots[0].type = orient.name
                    bpy.ops.transform.delete_orientation()
                removed += 1
            except RuntimeError:
                # If deletion fails, continue with the next one
                pass

        msg = f"Removed {removed} custom orientations." if removed else "No custom orientations removed."
        self.report({"INFO"}, msg)
        return {'FINISHED'}

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
        picked = scene.view_align_bone or (scene.view_align_target.name if scene.view_align_target else "None")
        layout.label(text=f"Picked: {picked}")

        col = layout.column(align=True)
        for axis_pair in ((('-Y', '+Y'),), (('X', '-X'),), (('Z', '-Z'),)):
            row = col.row(align=True)
            for label in axis_pair[0]:
                row.operator("view3d.align_view", text=label).axis = label

        box = layout.box()
        box.label(text="Custom Transform Orientation")
        row = box.row(align=True)
        row.operator("view3d.create_orient_custom", text="Create", icon='PLUS')
        row.operator("view3d.clear_custom_orientations", text="Clear", icon='TRASH')

# -----------------------------------------------------------------------------
# Registration helpers
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
