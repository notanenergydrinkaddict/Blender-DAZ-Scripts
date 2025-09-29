# SPDX-License-Identifier: Apache-2.0
# Copyright Blender-DAZ-Scripts authors.

# Usage:
# Import any mixamo rig(s)
# Select one or more armatures in the outliner
# Run this script to export each as BVH with `mixamorig:` removed.

import bpy
import re
import os

MIXAMO_RIG_PREFIX = "mixamorig:"


def clean_bone_name(name: str) -> str:
    name = name.replace(MIXAMO_RIG_PREFIX, "")
    name = re.sub(r"[^\w]", "", name)
    return name


def rename_bones(armature_obj):
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='EDIT')

    for bone in armature_obj.data.edit_bones:
        bone.name = clean_bone_name(bone.name)

    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"Renamed all bones in '{armature_obj.name}'.")


def get_armature_frame_range(armature_obj):
    action = armature_obj.animation_data.action if armature_obj.animation_data else None

    if action and action.fcurves:
        all_frames = [
            kp.co.x
            for fc in action.fcurves
            for kp in fc.keyframe_points
        ]
        if all_frames:
            frame_start = int(min(all_frames))
            frame_end = int(max(all_frames))
            print(f"Detected keyframe range: {frame_start} -> {frame_end} ({frame_end - frame_start + 1} frames)")
            return frame_start, frame_end

    frame_start = bpy.context.scene.frame_start
    frame_end = bpy.context.scene.frame_end
    print(f"No keyframes found - using scene range: {frame_start} -> {frame_end}")
    return frame_start, frame_end


def export_armature_as_bvh(armature_obj):
    blend_path = bpy.data.filepath
    export_dir = os.path.dirname(blend_path) if blend_path else os.path.expanduser("~")

    filename = f"{armature_obj.name}_edit.bvh"
    export_path = os.path.join(export_dir, filename)

    frame_start, frame_end = get_armature_frame_range(armature_obj)

    bpy.ops.object.select_all(action='DESELECT')
    armature_obj.select_set(True)
    bpy.context.view_layer.objects.active = armature_obj

    bpy.ops.export_anim.bvh(
        filepath=export_path,
        check_existing=False,
        global_scale=1.0,
        frame_start=frame_start,
        frame_end=frame_end,
        rotate_mode='NATIVE',
        root_transform_only=False,
    )

    print(f"Exported BVH to: {export_path}")
    return export_path


def duplicate_armature(original_obj):
    bpy.ops.object.select_all(action='DESELECT')
    original_obj.select_set(True)
    bpy.context.view_layer.objects.active = original_obj

    bpy.ops.object.duplicate(linked=False)
    duplicate = bpy.context.active_object
    duplicate.name = f"{original_obj.name}_rename_temp"
    duplicate.data.name = f"{original_obj.data.name}_rename_temp"
    print(f"Created duplicate: '{duplicate.name}'")
    return duplicate


def delete_object(obj):
    data = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.armatures.remove(data, do_unlink=True)
    print(f"Deleted temporary duplicate.")


def process_armature(obj):
    original_name = obj.name
    print(f"Processing armature: '{original_name}'")

    has_mixamo = any(MIXAMO_RIG_PREFIX in b.name for b in obj.data.bones)
    if not has_mixamo:
        print(f"No '{MIXAMO_RIG_PREFIX}' bones found in '{original_name}'. Skipping.")
        return None

    dup = duplicate_armature(obj)
    rename_bones(dup)
    dup.name = original_name
    obj.name = f"{original_name}_original_temp"

    export_path = export_armature_as_bvh(dup)

    obj.name = original_name
    delete_object(dup)

    return export_path


def main():
    selected_armatures = [o for o in bpy.context.selected_objects if o.type == 'ARMATURE']

    if not selected_armatures:
        print("ERROR: No armatures selected. Please select one or more armatures and run again.")
        bpy.context.window_manager.popup_menu(
            lambda self, ctx: self.layout.label(text="No armatures selected. Please select one or more armatures."),
            title="BVH Export Error",
            icon='ERROR'
        )
        return

    exported = []
    skipped = []

    for obj in selected_armatures:
        path = process_armature(obj)
        if path:
            exported.append(path)
        else:
            skipped.append(obj.name)

    if not exported:
        msg = f"No mixamo bones found in any selected armature. Skipped: {', '.join(skipped)}"
        print(msg)
        bpy.context.window_manager.popup_menu(
            lambda self, ctx: self.layout.label(text=msg),
            title="BVH Export Skipped",
            icon='ERROR'
        )
        return

    summary_lines = [f"Exported {len(exported)} file(s):"] + exported
    if skipped:
        summary_lines.append(f"Skipped (no mixamo prefix): {', '.join(skipped)}")

    for line in summary_lines:
        print(line)

    def draw_popup(self, ctx):
        for line in summary_lines:
            self.layout.label(text=line)

    bpy.context.window_manager.popup_menu(draw_popup, title="BVH Export Complete", icon='CHECKMARK')


if __name__ == "__main__":
    main()
