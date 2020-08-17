from pycram.action_designator import *
from pycram.mobile_pick_place_plans import move_torso, set_gripper, release, grip, move_arms, move_arms_into_configuration, \
    navigate_to, navigate_near_object, look_at_frame, look_at_object, look_at_location, look_in_direction, detect
from pycram.high_level_plans import pickup_object, place_object, transport_object
from pycram.pr2_description import Arms, ArmConfiguration, Grasp
from pycram.designator import DesignatorError, ObjectDesignator, LocationDesignator

def ground_move_torso(self):
    self.function = lambda : move_torso(self.position)
    return super(MoveTorsoActionDescription, self).ground()

def ground_set_gripper(self):
    self.function = lambda : set_gripper(self.gripper, self.opening)
    return super(SetGripperActionDescription, self).ground()

def ground_release(self):
    self.function = lambda: release(self.gripper, self.object_designator)
    return super(ReleaseActionDescription, self).ground()

def ground_grip(self):
    if self.object_designator:
        self.object_designator = self.object_designator.current()
        self.grasped_object = self.object_designator.rename_prop("pose", "old_pose")
    self.function = lambda : grip(self.gripper, self.effort, self.object_designator)
    return super(GripActionDescription, self).ground()

def ground_move_arms_in_sequence(self):
    self.function = lambda: move_arms(self.left_trajectory, self.right_trajectory)
    return super(MoveArmsInSequenceDescription, self).ground()

def ground_move_arms_into_configuration(self):
    if self.left_configuration is ArmConfiguration.PARK:
        self.left_joint_states = {"shoulder_joint": 0.5, "elbow_joint": 0.4, "wrist_joint": 0.3}
    if self.left_configuration is ArmConfiguration.CARRY:
        self.left_joint_states = {"shoulder_joint": 0.3, "elbow_joint": 0.3, "wrist_joint": 0.5}
    if self.right_configuration is ArmConfiguration.PARK:
        self.right_joint_states = {"shoulder_joint": 0.5, "elbow_joint": 0.4, "wrist_joint": 0.3}
    if self.right_configuration is ArmConfiguration.CARRY:
        self.right_joint_states = {"shoulder_joint": 0.3, "elbow_joint": 0.3, "wrist_joint": 0.5}
    self.function = lambda: move_arms_into_configuration(self.left_joint_states, self.right_joint_states)
    return super(MoveArmsIntoConfigurationDescription, self).ground()

def ground_park_arms(self):
    if self.arm in [Arms.LEFT, Arms.BOTH]:
        self.left_joint_states = {"shoulder_joint": 0.5, "elbow_joint": 0.4, "wrist_joint": 0.3}
    if self.arm in [Arms.RIGHT, Arms.BOTH]:
        self.right_joint_states = {"shoulder_joint": 0.5, "elbow_joint": 0.4, "wrist_joint": 0.3}
    self.function = lambda: move_arms_into_configuration(self.left_joint_states, self.right_joint_states)
    return super(ParkArmsDescription, self).ground()

def ground_pick_up(self):
    if not self.object_designator:
        raise DesignatorError()
    if not self.arm:
        self.arm = Arms.LEFT
    if not self.grasp:
        self.grasp = Grasp.TOP
    self.gripper_opening = 0.9
    self.effort = 1
    if self.arm in [Arms.LEFT, Arms.BOTH]:
        self.left_reach_poses = ["<Reaching Pose>"]
        self.left_grasp_poses = ["<Grasping Pose>"]
        self.left_lift_poses = ["<Lifting Pose>"]
    if self.arm in [Arms.RIGHT, Arms.BOTH]:
        self.right_reach_poses = ["<Reaching Pose>"]
        self.right_grasp_poses = ["<Grasping Pose>"]
        self.right_lift_poses = ["<Lifting Pose>"]
    self.function = lambda : pickup_object(self.object_designator, self.arm, self.gripper_opening, self.effort,
                                           self.left_reach_poses, self.right_reach_poses,
                                           self.left_grasp_poses, self.right_grasp_poses,
                                           self.left_lift_poses, self.right_lift_poses)
    return super(PickUpDescription, self).ground()

def ground_place(self):
    if not self.object_designator:
        raise DesignatorError()
    if not self.arm:
        self.arm = Arms.LEFT
    if self.arm in [Arms.LEFT, Arms.BOTH]:
        self.left_reach_poses = ["<Reaching Pose>"]
        self.left_place_poses = [self.target_location]
        self.left_retract_poses = ["<Lifting Pose>"]
    if self.arm in [Arms.RIGHT, Arms.BOTH]:
        self.right_reach_poses = ["<Reaching Pose>"]
        self.right_place_poses = [self.target_location]
        self.right_retract_poses = ["<Lifting Pose>"]
    self.function = lambda: place_object(self.object_designator, self.arm,
                                         self.left_reach_poses, self.right_reach_poses,
                                         self.left_place_poses, self.right_place_poses,
                                         self.left_retract_poses, self.right_retract_poses)
    return super(PlaceDescription, self).ground()

def ground_navigate(self):
    if self.object_designator:
        self.function = lambda: navigate_near_object(self.object_designator)
    elif self.target_location:
        self.function = lambda: navigate_to(self.target_location)
    else:
        raise DesignatorError("Error: Neither object nor target location were given for navigation.")
    return super(NavigateDescription, self).ground()

def ground_transport(self):
    self.function = lambda: transport_object(self.object_designator, self.arm, self.target_location)
    return super(TransportObjectDescription, self).ground()

def ground_look_at(self):
    if self.target is LocationDesignator:
        self.function = lambda: look_at_location(self.target)
    elif self.target is ObjectDesignator:
        self.function = lambda: look_at_object(self.target)
    elif self.target is str:
        self.function = lambda: look_at_frame(self.target)
    elif self.target is tuple: # TODO?: Use some kind of vector class?
        self.function = lambda: look_in_direction(self.target)
    else:
        raise DesignatorError()
    return super(LookAtActionDescription, self).ground()

def ground_detect(self):
    self.function = lambda : detect(self.object_designator)
    return super(DetectActionDescription, self).ground()

MoveTorsoActionDescription.ground = ground_move_torso
SetGripperActionDescription.ground = ground_set_gripper
ReleaseActionDescription.ground = ground_release
GripActionDescription.ground = ground_grip
MoveArmsInSequenceDescription.ground = ground_move_arms_in_sequence
MoveArmsIntoConfigurationDescription.ground = ground_move_arms_into_configuration
ParkArmsDescription.ground = ground_park_arms
PickUpDescription.ground = ground_pick_up
PlaceDescription.ground = ground_place
NavigateDescription.ground = ground_navigate
TransportObjectDescription.ground = ground_transport
LookAtActionDescription.ground = ground_look_at
DetectActionDescription.ground = ground_detect