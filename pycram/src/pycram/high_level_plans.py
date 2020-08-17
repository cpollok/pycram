from pycram.task import with_tree
from pycram.plan_failures import PlanFailure
from pycram.pr2_description import Arms
from pycram.action_designator import ActionDesignator, SetGripperActionDescription, MoveArmsInSequenceDescription, \
    GripActionDescription, ReleaseActionDescription, PickUpDescription, PlaceDescription, NavigateDescription, \
    MoveArmsIntoConfigurationDescription

@with_tree
def pickup_object(object_designator, arm, gripper_opening, effort,
                  left_reach_poses, right_reach_poses,
                  left_grasp_poses, right_grasp_poses,
                  left_lift_poses, right_lift_poses,
                  **kwargs):
    ActionDesignator(SetGripperActionDescription(arm, gripper_opening).ground()).perform()
    ActionDesignator(MoveArmsInSequenceDescription(left_reach_poses, right_reach_poses)).perform()
    ActionDesignator(MoveArmsInSequenceDescription(left_grasp_poses, right_grasp_poses)).perform()
    ActionDesignator(GripActionDescription(arm, object_designator, effort)).perform()
    ActionDesignator(MoveArmsInSequenceDescription(left_lift_poses, right_lift_poses)).perform()

@with_tree
def place_object(object_designator, arm,
                 left_reach_poses, right_reach_poses,
                 left_place_poses, right_place_poses,
                 left_retract_poses, right_retract_poses,
                 **kwargs):
    # FAIL_MOVE_ARMS = True
    while True:
        try:
            ActionDesignator(MoveArmsInSequenceDescription(left_reach_poses, right_reach_poses)).perform()
            ActionDesignator(MoveArmsInSequenceDescription(left_place_poses, right_place_poses)).perform()
        except PlanFailure:
            # FAIL_MOVE_ARMS = False
            continue
        break

    ActionDesignator(ReleaseActionDescription(arm, object_designator)).perform()
    ActionDesignator(MoveArmsInSequenceDescription(left_retract_poses, right_retract_poses)).perform()

@with_tree
def transport_object(object_designator, arm, target_location):
    ActionDesignator(NavigateDescription(object_designator=object_designator)).perform()
    ActionDesignator(PickUpDescription(object_designator, arm)).perform()
    ActionDesignator(MoveArmsIntoConfigurationDescription(Arms.BOTH)).perform()
    ActionDesignator(NavigateDescription(target_location=target_location)).perform()
    ActionDesignator(PlaceDescription(object_designator, target_location, arm)).perform()