from pycram.task import with_tree
from pycram.plan_failures import PlanFailure
from pycram.pr2_description import Arms

OBJECT_HELD_LEFT = None
OBJECT_HELD_RIGHT = None

FAIL_MOVE_ARMS = False

@with_tree
def move_torso(position):
    print("Setting torso to {}.".format(position))

@with_tree
def set_gripper(gripper, opening, **kwargs):
    print("Setting gripper {} to {}.".format(gripper, opening))

@with_tree
def release(gripper, object_designator=None, **kwargs):
    if object_designator:
        print("Releasing {} from gripper {}.".format(str(object_designator), str(gripper)))
    else:
        print("Releasing gripper {}.".format(str(gripper)))

@with_tree
def grip(gripper, effort, object_designator=None, **kwargs):
    print("Gripping with {} and effort: {}.".format(gripper, effort))
    if object_designator:
        print("Now holding {}.".format(object_designator.prop_value("name")))
        if gripper == Arms.LEFT:
            global OBJECT_HELD_LEFT
            OBJECT_HELD_LEFT = object_designator
        if gripper == Arms.RIGHT:
            global OBJECT_HELD_RIGHT
            OBJECT_HELD_RIGHT = object_designator

@with_tree
def move_arms(left_trajectory=[], right_trajectory=[], **kwargs):
    if FAIL_MOVE_ARMS:
        raise PlanFailure()
    for p in left_trajectory:
        print("Moving left arm to {}.".format(p))
    for p in right_trajectory:
        print("Moving right arm to {}.".format(p))

@with_tree
def move_arms_into_configuration(left_joint_states={}, right_joint_states={}):
    for s in left_joint_states.items():
        print("Left arm joint '{}' put to {}.".format(s[0], s[1]))
    for s in right_joint_states.items():
        print("Right arm joint '{}' put to {}.".format(s[0], s[1]))

# @with_tree
# def pickup_object(object_designator, arm, gripper_opening, effort,
#                   left_reach_poses, right_reach_poses,
#                   left_grasp_poses, right_grasp_poses,
#                   left_lift_poses, right_lift_poses,
#                   **kwargs):
#     ActionDesignator(SetGripperActionDescription(arm, gripper_opening).ground()).perform()
#     ActionDesignator(MoveArmsInSequenceDescription(left_reach_poses, right_reach_poses)).perform()
#     ActionDesignator(MoveArmsInSequenceDescription(left_grasp_poses, right_grasp_poses)).perform()
#     ActionDesignator(GripActionDescription(arm, object_designator, effort)).perform()
#     ActionDesignator(MoveArmsInSequenceDescription(left_lift_poses, right_lift_poses)).perform()
#
# @with_tree
# def place_object(object_designator, arm,
#                  left_reach_poses, right_reach_poses,
#                  left_place_poses, right_place_poses,
#                  left_retract_poses, right_retract_poses,
#                  **kwargs):
#     global FAIL_MOVE_ARMS
#     FAIL_MOVE_ARMS = True
#     while True:
#         try:
#             ActionDesignator(MoveArmsInSequenceDescription(left_reach_poses, right_reach_poses)).perform()
#             ActionDesignator(MoveArmsInSequenceDescription(left_place_poses, right_place_poses)).perform()
#         except PlanFailure:
#             FAIL_MOVE_ARMS = False
#             continue
#         break
#
#     ActionDesignator(ReleaseActionDescription(arm, object_designator)).perform()
#     ActionDesignator(MoveArmsInSequenceDescription(left_retract_poses, right_retract_poses)).perform()

@with_tree
def navigate_near_object(object_designator):
    print("Robot moves near {}.".format(object_designator.prop_value("name")))

@with_tree
def navigate_to(location):
    print("Robot moves to {}.".format(location))

# @with_tree
# def transport_object(object_designator, arm, target_location):
#     ActionDesignator(NavigateDescription(object_designator=object_designator)).perform()
#     ActionDesignator(PickUpDescription(object_designator, arm)).perform()
#     ActionDesignator(MoveArmsIntoConfigurationDescription(Arms.BOTH)).perform()
#     ActionDesignator(NavigateDescription(target_location=target_location)).perform()
#     ActionDesignator(PlaceDescription(object_designator, target_location, arm)).perform()

@with_tree
def look_at_location(location_designator):
    print("Robot looking at location: {}.".format(location_designator))

@with_tree
def look_at_object(object_designator):
    print("Robot is now looking at {}.".format(object_designator.prop_value("name")))

@with_tree
def look_at_frame(frame):
    print("Robot is now looking at frame {}.".format(frame))

@with_tree
def look_in_direction(direction):
    print("Robot looking in direction {}.".format(direction))

@with_tree
def detect(object_designator):
    # TODO: Enrich the object with some kind of information. Pose etc
    return object_designator