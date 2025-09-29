# SPDX-License-Identifier: Apache-2.0
# Copyright Blender-DAZ-Scripts authors.

# Usage:
# Select the iris bone after running "Merge Rigs"
# in DAZ Setup's Correction panel.

import bpy

def main():
    arm = bpy.context.object
    pb = bpy.context.active_pose_bone

    if pb is None:
        raise Exception("No active pose bone selected.")
        return

    name = pb.name.lower()

    if not (name.startswith("l_iris") or name.startswith("r_iris")):
        raise Exception("Active bone must be 'l_iris' or 'r_iris'. Got '%s' instead." % pb.name)
        return

    eye_bone = pb.name.replace("iris", "eye")

    if eye_bone not in arm.pose.bones:
        raise Exception("Expected eye bone '%s' not found." % eye_bone)
        return

    con_name = ("Iris Copy %s" % eye_bone)

    for c in pb.constraints:
        if c.name == con_name:
            print("Constraint '%s' already exists. Skipping." % con_name)
            return

    con = pb.constraints.new(type='COPY_ROTATION')
    con.name = con_name
    con.target = arm
    con.subtarget = eye_bone

    con.use_y = False
    con.use_x = con.use_z = True

    con.invert_x = True
    con.invert_y = con.invert_z = False

    con.mix_mode = 'AFTER'
    con.target_space = con.owner_space = 'LOCAL'
    con.influence = 0.1 # for iris to not go out of bounds

if __name__ == "__main__":
    main()
