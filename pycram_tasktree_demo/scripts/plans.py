from pycram.task import with_tree
from pycram.process_module import ProcessModule
from pycram.designator import MotionDesignator, ObjectDesignator
from pycram.action_designator import *
from pycram.pr2_description import Arms

# Only needed for hack :/
from pycram.bullet_world import BulletWorld

@with_tree
def open_gripper(gripper):
    print("Opening gripper {}".format(gripper))
    ProcessModule.perform(MotionDesignator([('type', 'opening-gripper'), ('gripper', gripper)]))

@with_tree
def close_gripper(gripper):
    print("Closing gripper {}.".format(gripper))
    ProcessModule.perform(MotionDesignator([('type', 'closing-gripper'), ('gripper', gripper)]))

@with_tree
def pick_up(arm, btr_object):
    print("Picking up {} with {}.".format(btr_object, arm))
    motion_arm = "left" if arm is Arms.LEFT else "right"
    # Hack to detach from kitchen.. (Should go into process module maybe)
    btr_object.prop_value('bullet_obj').detach(BulletWorld.current_bullet_world.get_objects_by_name("kitchen")[0])
    ProcessModule.perform(MotionDesignator([('type', 'pick-up'), ('object', btr_object), ('arm', motion_arm)]))
    ActionDesignator(ParkArmsDescription(arm=arm)).perform()

@with_tree
def place(arm, btr_object, target):
    print("Placing {} with {} at {}.".format(btr_object, arm, target))
    motion_arm = "left" if arm is Arms.LEFT else "right"
    ProcessModule.perform(MotionDesignator([('type', 'place'), ('object', btr_object), ('arm', motion_arm), ('target', target)]))
    ActionDesignator(ParkArmsDescription(arm=arm)).perform()

@with_tree
def navigate(target, orientation=[0, 0, 0, 1]):
    print("Moving to {}. Orientation: {}.".format(target, orientation))
    ProcessModule.perform(MotionDesignator([('type', 'moving'), ('target', target), ('orientation', orientation)]))

@with_tree
def park_arms(arms):
    print("Parking arms {}.".format(arms))
    left_arm = [('left-arm', 'park')] if arms in [Arms.LEFT, Arms.BOTH] else []
    right_arm = [('right-arm', 'park')] if arms in [Arms.RIGHT, Arms.BOTH] else []
    ProcessModule.perform(MotionDesignator([('type', 'move-arm-joints')] + left_arm + right_arm))

@with_tree
def detect(object_designator):
    print("Detecting object of type {}.".format(object_designator.prop_value("type")))
    det_object =  ProcessModule.perform(MotionDesignator([('type', 'detecting'), ('object', object_designator.prop_value("type"))]))
    if det_object is None:
        raise PlanFailure("No object detected.")
    detected_obj_desig = object_designator.copy([("pose", det_object.get_pose()), ("bullet_obj", det_object)])
    detected_obj_desig.equate(object_designator)
    return detected_obj_desig

@with_tree
def look_at(target):
    print("Looking at {}.".format(target))
    ProcessModule.perform(MotionDesignator([('type', 'looking'), ('target', target)]))

@with_tree
def access(container_joint, handle_link, arm, distance, btr_object):
    print("Accessing container.")
        # ProcessModule.perform(MotionDesignator([('type', 'accessing'), ('drawer-joint', 'sink_area_left_upper_drawer_main_joint'),
        #                                         ('drawer-handle', 'sink_area_left_upper_drawer_handle'), ('arm', 'left'), ('distance', 0.3), ('part-of', kitchen)]))

@with_tree
def seal():
    pass

@with_tree
def transport(object_designator, arm, target_location):
    fetch_robot_position = [0.7, 0.9, 0]
    fetch_object_position = [1.38, 0.7, 0.75] # [1.3, 0.9, 1]
    # deliver_robot_position = [0.7, -0.9, 0]
    deliver_robot_position = [-1.8, 1, 0]
    ActionDesignator(ParkArmsDescription(Arms.BOTH)).perform()
    # this part has to be in fh to be retried
    ActionDesignator(NavigateDescription(target_position=fetch_robot_position)).perform()
    ActionDesignator(LookAtActionDescription(target=fetch_object_position)).perform()
    obj = ActionDesignator(DetectActionDescription(object_designator)).perform()

    # end of part
    ActionDesignator(PickUpDescription(obj, arm)).perform()
    ActionDesignator(ParkArmsDescription(Arms.BOTH)).perform()
    ActionDesignator(NavigateDescription(target_position=deliver_robot_position)).perform()
    ActionDesignator(PlaceDescription(obj, target_location=target_location, arm=arm)).perform()
    ActionDesignator(ParkArmsDescription(Arms.BOTH)).perform()

def get_container_joint_and_handle(container_desig):
    name = container_desig.prop_value('name')
    if name == "iai_fridge":
        return "iai_fridge_door_joint", "iai_fridge_door_handle"
    elif name == "sink_area_left_upper_drawer":
        return "sink_area_left_upper_drawer_main_joint", "sink_area_left_upper_drawer_handle"
    elif name == "sink_area_left_middle_drawer":
        return "sink_area_left_middle_drawer_main_joint", "sink_area_left_middle_drawer_handle"
    else:
        raise NotImplementedError()

@with_tree
def open_container(object_designator, arm, distance):
    object_type = object_designator.prop_value('type')
    if object_type in ["container", "drawer"]:
        motion_type = "opening-prismatic"
    elif object_type in ["fridge"]:
        motion_type = "opening-rotational"
    else:
        raise NotImplementedError()
    joint, handle = get_container_joint_and_handle(object_designator)
    arm = "left" if arm == Arms.LEFT else "right"
    environment = object_designator.prop_value('part-of')
    ProcessModule.perform(MotionDesignator(
        [('type', motion_type), ('joint', joint),
         ('handle', handle), ('arm', arm), ('distance', distance),
         ('part-of', environment)]))

@with_tree
def close_container(object_designator, arm):
    object_type = object_designator.prop_value('type')
    if object_type in ["container", "drawer"]:
        motion_type = "closing-prismatic"
    elif object_type in ["fridge"]:
        motion_type = "closing-rotational"
    else:
        raise NotImplementedError()
    joint, handle = get_container_joint_and_handle(object_designator)
    arm = "left" if arm == Arms.LEFT else "right"
    environment = object_designator.prop_value('part-of')
    ProcessModule.perform(MotionDesignator(
        [('type', motion_type), ('joint', joint),
         ('handle', handle), ('arm', arm), ('part-of', environment)]))

from pycram.language import failure_handling
from pycram.plan_failures import PlanFailure

@with_tree
def test_plan():
    with failure_handling(5):
        try:
            raise PlanFailure
        except PlanFailure as e:
            print("ASD")
            retry()
