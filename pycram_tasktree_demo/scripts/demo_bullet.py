import time
import os
import rospy
import process_modules
import motion_designators
from pycram.pr2_description import Arms
from pycram.designator import MotionDesignator, ObjectDesignator
from pycram.action_designator import *
from pycram.action_designator import TestDescription
from pycram.bullet_world import BulletWorld, Object
from pycram.language import macros, failure_handling, par
from pycram.task import with_tree
from pycram.plan_failures import PlanFailure
from pycram.process_module import ProcessModule

import desig_resolution

resources_path = os.path.join(os.path.dirname(__file__), '..', 'resources')
print(resources_path)
world = BulletWorld()
world.set_gravity([0, 0, -9.8])
plane = Object("floor", "environment", os.path.join(resources_path, "plane.urdf"), world=world)
robot = Object("pr2", "robot", os.path.join(resources_path, "pr2.urdf"))
milk = Object("milk", "milk", os.path.join(resources_path, "milk.stl"), [1.3, 1, 0.95])
cereal = Object("cereal", "cereal", os.path.join(resources_path, "breakfast_cereal.stl"), [1.3, 0.8, 0.95])
kitchen = Object("kitchen", "environment", os.path.join(resources_path, "kitchen.urdf"))

spoon = Object("spoon", "spoon", os.path.join(resources_path, "spoon.stl"), [1.38, 0.7, 0.75])
kitchen.attach(spoon, link="sink_area_left_upper_drawer_main")
kitchen.attach(Object("spoon2", "spoon", os.path.join(resources_path, "spoon.stl"), [1.38, 0.75, 0.75]),
               link="sink_area_left_upper_drawer_main")
kitchen.attach(Object("spoon3", "spoon", os.path.join(resources_path, "spoon.stl"), [1.38, 0.65, 0.75]),
               link="sink_area_left_upper_drawer_main")
kitchen.attach(Object("spoon4", "spoon", os.path.join(resources_path, "spoon.stl"), [1.38, 0.6, 0.75]),
               link="sink_area_left_upper_drawer_main")

bowl = Object("bowl", "bowl", os.path.join(resources_path, "bowl.stl"), [1.4, 0.725, 0.5])
kitchen.attach(bowl, link="sink_area_left_middle_drawer_main")
kitchen.attach(Object("bowl2", "bowl", os.path.join(resources_path, "bowl.stl"), [1.4, 0.925, 0.5]),
               link="sink_area_left_middle_drawer_main")
kitchen.attach(Object("bowl3", "bowl", os.path.join(resources_path, "bowl.stl"), [1.4, 1.125, 0.5]),
               link="sink_area_left_middle_drawer_main")

BulletWorld.robot = robot

@with_tree
def demo():
    ActionDesignator(TransportObjectDescription(ObjectDesignator([('type', 'milk')]),
                                                arm=Arms.LEFT, target_location=[-1.2, 1.2, 0.95])).perform()
    ActionDesignator(TransportObjectDescription(ObjectDesignator([('type', 'cereal')]),
                                            arm=Arms.RIGHT, target_location=[-1.2, 1, 0.95])).perform()

# def demo():
#     ActionDesignator(TransportObjectDescription(ObjectDesignator([('type', 'milk')]),
#                                                 arm=Arms.LEFT, target_location=[1.3, -1, 0.95])).perform()
#     ActionDesignator(TransportObjectDescription(ObjectDesignator([('type', 'cereal')]),
#                                             arm=Arms.RIGHT, target_location=[1.3, -1.2, 0.95])).perform()

def demo2():
    # ProcessModule.perform(MotionDesignator([('type', 'move-arm-joints'), ('left-arm', 'park'), ('right-arm', 'park')]))
    # ProcessModule.perform(MotionDesignator([('type', 'moving'), ('target', [0.55, 1.3, 0]), ('orientation', [0, 0, 0, 1])]))
    # ProcessModule.perform(MotionDesignator(
    #     [('type', 'opening'), ('container-joint', 'sink_area_left_upper_drawer_main_joint'),
    #      ('container-handle', 'sink_area_left_upper_drawer_handle'), ('arm', 'right'), ('distance', 0.3),
    #      ('part-of', kitchen)]))
    # ProcessModule.perform(MotionDesignator(
    #     [('type', 'closing'), ('container-joint', 'sink_area_left_upper_drawer_main_joint'),
    #      ('container-handle', 'sink_area_left_upper_drawer_handle'), ('arm', 'right'),
    #      ('part-of', kitchen)]))

    ProcessModule.perform(MotionDesignator([('type', 'move-arm-joints'), ('left-arm', 'park'), ('right-arm', 'park')]))
    ProcessModule.perform(MotionDesignator([('type', 'moving'), ('target', [0.55, -0.55, 0]), ('orientation', [0, 0, 0, 1])]))
    ActionDesignator(OpenActionDescription(ObjectDesignator([('type', 'fridge'), ('name', 'iai_fridge'), ('part-of', kitchen)]),
                                           Arms.RIGHT,
                                           1.5)).perform()
    ActionDesignator(
        CloseActionDescription(ObjectDesignator([('type', 'fridge'), ('name', 'iai_fridge'), ('part-of', kitchen)]),
                              Arms.RIGHT)).perform()
    ProcessModule.perform(MotionDesignator([('type', 'move-arm-joints'), ('left-arm', 'park'), ('right-arm', 'park')]))
    ProcessModule.perform(MotionDesignator([('type', 'moving'), ('target', [0.55, 1.3, 0]), ('orientation', [0, 0, 0, 1])]))
    ActionDesignator(
        OpenActionDescription(ObjectDesignator([('type', 'drawer'), ('name', 'sink_area_left_upper_drawer'), ('part-of', kitchen)]),
                              Arms.RIGHT,
                              0.3)).perform()
    ActionDesignator(TransportObjectDescription(ObjectDesignator([('type', 'spoon'),('part-of', kitchen)]),
                                                arm=Arms.RIGHT, target_location=[-1.2, 1.0, 0.95])).perform()
    world.simulate(1)

def reach_position_generator(object_designator):
    yield [0.3, 0.8, 0]
    yield [0.4, 0.8, 0]
    yield [0.5, 0.9, 0]
    yield [0.6, 0.9, 0]

def container_opening_distance_generator(object_designator):
    yield 0.1
    yield 0.2
    yield 0.3
    yield 0.4


def get_working_parameters(action_type, tree):
    pass

old_tree = None

from pycram.task import SimulatedTaskTree

@with_tree
def introspection_demo():
    attempts = 0
    robot_position = reach_position_generator(ObjectDesignator([]))
    ActionDesignator(ParkArmsDescription(Arms.BOTH)).perform()
    ActionDesignator(NavigateDescription(target_position=next(robot_position))).perform()
    ActionDesignator(
        OpenActionDescription(
            ObjectDesignator([('type', 'drawer'), ('name', 'sink_area_left_middle_drawer'), ('part-of', kitchen)]),
            Arms.RIGHT,
            0.3)).perform()
    with SimulatedTaskTree() as st:
        while True:
            try:
                ActionDesignator(LookAtActionDescription(target=bowl.get_position())).perform()
                obj = ActionDesignator(DetectActionDescription(ObjectDesignator([('type', 'bowl')]))).perform()
                ActionDesignator(PickUpDescription(obj, arm=Arms.RIGHT)).perform()
                break
            except PlanFailure as f:
                print(f)
                print("Reposition!")
                ActionDesignator(NavigateDescription(target_position=next(robot_position))).perform()
                print("Retry!")
                time.sleep(0.3)
                attempts += 1
                if attempts < 5:
                    continue
                raise f
        print(st.get_successful_params_ctx_after("navigate", "detect"))
        success_params = st.get_successful_params_ctx_after("navigate", "detect")
    ActionDesignator(NavigateDescription(target_position=success_params[0][0][0])).perform()
    # ActionDesignator(LookAtActionDescription(target=bowl.get_position())).perform()
    # obj = ActionDesignator(DetectActionDescription(ObjectDesignator([('type', 'bowl')]))).perform()
    # ActionDesignator(PickUpDescription(obj, arm=Arms.RIGHT)).perform()

import pycram
from pycram.task import TaskTreeNode
# demo()
# time.sleep(5)
#
# tt : TaskTreeNode = pycram.task.TASK_TREE
# tt.generate_dot().render("out/demo.dot")
# placing_node = tt.children[0].children[7].copy()
# tt.children[0].children[5].delete()
# tt.children[0].children[6].delete()
# tt.children[0].children[7].delete()
# tt.children[0].children[8].delete()
# tt.children[1].children[1].delete()
# tt.children[1].children[2].delete()
# placing_node.parent = tt.children[1]
# tt.children[1].children[7].exec_child_next = placing_node
# placing_node.fix_path()
# tt.generate_dot().render("out/demo_test.dot")
# milk.set_position([1.3, 1, 1])
# cereal.set_position([1.3, 0.8, 1])
# tt.execute()
# tt.generate_dot().render("out/demo_after_change.dot")

# demo2()
introspection_demo()
# pycram.task.TASK_TREE.generate_dot().render("out/introspection.dot", view=True)