import time
import os
import rospy
import pycram
import pybullet

from typing import Optional
from pycram.pr2_description import Arms
from pycram.designator import ObjectDesignator
from pycram.action_designator import *
from pycram.bullet_world import BulletWorld, Object
from pycram.task import with_tree, TaskTreeNode, SimulatedTaskTree
from pycram.plan_failures import PlanFailure
from pycram.pr2_knowledge import reach_position_generator, container_opening_distance_generator, object_fetching_location_generator, object_placing_location_generator

import process_modules
import motion_designators
import desig_resolution


resources_path = os.path.join(os.path.dirname(__file__), '..', 'resources')
# print(resources_path)
world = BulletWorld("GUI")
pybullet.resetDebugVisualizerCamera(cameraDistance=5, cameraYaw=30, cameraPitch=-70, cameraTargetPosition=[0,0,0])
world.set_gravity([0, 0, -9.8])
plane = Object("floor", "environment", os.path.join(resources_path, "plane.urdf"), world=world)
robot = Object("pr2", "robot", os.path.join(resources_path, "pr2.urdf"))
kitchen = Object("kitchen", "environment", os.path.join(resources_path, "kitchen.urdf"))

spoon = Object("spoon", "spoon", os.path.join(resources_path, "spoon.stl"), [1.38, 0.7, 0.75])
kitchen.attach(spoon, link="sink_area_left_upper_drawer_main")
kitchen.attach(Object("spoon2", "spoon", os.path.join(resources_path, "spoon.stl"), [1.38, 0.75, 0.75]),
               link="sink_area_left_upper_drawer_main")
kitchen.attach(Object("spoon3", "spoon", os.path.join(resources_path, "spoon.stl"), [1.38, 0.65, 0.75]),
               link="sink_area_left_upper_drawer_main")
kitchen.attach(Object("spoon4", "spoon", os.path.join(resources_path, "spoon.stl"), [1.38, 0.6, 0.75]),
               link="sink_area_left_upper_drawer_main")

bowl1 = Object("bowl", "bowl", os.path.join(resources_path, "bowl.stl"), [1.4, 0.725, 0.5])
bowl2 = Object("bowl2", "bowl", os.path.join(resources_path, "bowl.stl"), [1.4, 0.925, 0.5])
bowl3 = Object("bowl3", "bowl", os.path.join(resources_path, "bowl.stl"), [1.4, 1.125, 0.5])
kitchen.attach(bowl1, link="sink_area_left_middle_drawer_main")
kitchen.attach(bowl2, link="sink_area_left_middle_drawer_main")
kitchen.attach(bowl3, link="sink_area_left_middle_drawer_main")
bowls = [bowl1, bowl2, bowl3]

cereal = Object("cereal", "cereal", os.path.join(resources_path, "breakfast_cereal.stl"), [1.3, 0.8, 0.95])
cereal2 = Object("cereal2", "cereal", os.path.join(resources_path, "breakfast_cereal.stl"), [1.3, 1, 0.95])

milk = Object("milk", "milk", os.path.join(resources_path, "milk.stl"), [1.3, -0.85, 0.8])
kitchen.attach(milk, link="iai_fridge_door")
milk2 = Object("milk2", "milk", os.path.join(resources_path, "milk.stl"), [1.3, -1, 0.8])
kitchen.attach(milk2, link="iai_fridge_door")

BulletWorld.robot = robot

previous_tree : Optional[TaskTreeNode] = None

@with_tree
def introspection_demo(view=False):
    global previous_tree
    attempts = 0
    drawer_desig = ObjectDesignator([('type', 'drawer'), ('name', 'sink_area_left_middle_drawer'), ('part-of', kitchen)])
    robot_position = reach_position_generator(drawer_desig)
    ActionDesignator(ParkArmsDescription(Arms.BOTH)).perform()
    if previous_tree:
        target = previous_tree.get_successful_params_ctx_after("navigate", "detect")[0][0][0]
    else:
        target = next(robot_position)[0]
    ActionDesignator(NavigateDescription(target_position=target)).perform()
    ActionDesignator(
        OpenActionDescription(
            drawer_desig,
            Arms.RIGHT,
            0.3)).perform()
    ActionDesignator(ParkArmsDescription(Arms.BOTH)).perform()
    while True:
        try:
            ActionDesignator(LookAtActionDescription(target=bowl1.get_position())).perform()
            obj = ActionDesignator(DetectActionDescription(ObjectDesignator([('type', 'bowl')]))).perform()
            ActionDesignator(PickUpDescription(obj, arm=Arms.RIGHT)).perform()
            break
        except PlanFailure as f:
            print(f)
            print("Reposition!")
            ActionDesignator(NavigateDescription(target_position=next(robot_position)[0])).perform()
            print("Retry!")
            time.sleep(0.3)
            attempts += 1
            if attempts < 5:
                continue
            else:
                raise f
    previous_tree = pycram.task.TASK_TREE
    ActionDesignator(ParkArmsDescription(Arms.BOTH)).perform()
    pycram.task.TASK_TREE.generate_dot().render("out/introspection.dot", view=view)

@with_tree
def prospection_demo(view=False):
    container_desig = ObjectDesignator([('type', 'drawer'), ('name', 'sink_area_left_upper_drawer'), ('part-of', kitchen)])
    container_opening = container_opening_distance_generator(container_desig)
    ActionDesignator(ParkArmsDescription(Arms.BOTH)).perform()
    robot_position = reach_position_generator(ObjectDesignator([]))  # "Hack" to have the right position right away
    ActionDesignator(NavigateDescription(target_position=next(robot_position)[0])).perform()
    while True:
        with SimulatedTaskTree() as st:
            try:
                ActionDesignator(OpenActionDescription(container_desig, Arms.RIGHT, distance=next(container_opening))).perform()
                ActionDesignator(ParkArmsDescription(Arms.BOTH)).perform()
                ActionDesignator(LookAtActionDescription(target=bowl1.get_position())).perform()
                obj = ActionDesignator(DetectActionDescription(ObjectDesignator([('type', 'spoon')]))).perform()
                ActionDesignator(PickUpDescription(obj, arm=Arms.RIGHT)).perform()
                params = st.get_successful_params_ctx_after("open_container", "pick_up")
                break
            except PlanFailure as f:
                print(f)
                print("Retry!")
            except StopIteration:
                print("No more retries left.")
                return
    ActionDesignator(OpenActionDescription(*params[0][0])).perform()
    ActionDesignator(ParkArmsDescription(Arms.BOTH)).perform()
    ActionDesignator(LookAtActionDescription(target=spoon.get_position())).perform()
    obj = ActionDesignator(DetectActionDescription(ObjectDesignator([('type', 'spoon')]))).perform()
    ActionDesignator(PickUpDescription(obj, arm=Arms.RIGHT)).perform()
    ActionDesignator(ParkArmsDescription(Arms.BOTH)).perform()
    pycram.task.TASK_TREE.generate_dot().render("out/prospection.dot", view=view)

@with_tree
def reorganization_demo_plan():
    fridge_desig = ObjectDesignator([('type', 'fridge'), ('name', 'iai_fridge'), ('part-of', kitchen)])
    milk_desig = ObjectDesignator([('type', 'milk'), ('in', fridge_desig)])
    ActionDesignator(TransportObjectDescription(milk_desig, arm=Arms.LEFT,
                                                target_location=[-1.2, 1.2, 0.95])).perform()
    cereal_desig = ObjectDesignator([('type', 'cereal')])
    ActionDesignator(TransportObjectDescription(cereal_desig, arm=Arms.RIGHT,
                                                target_location=[-1.2, 1, 0.95])).perform()

def reorganization_demo(view=False):
    local_state, attachments = world.save_state()
    reorganization_demo_plan()
    world.restore_state(local_state, attachments)
    pycram.task.TASK_TREE.generate_dot().render("out/reorganization.dot", view=view)
    transform_transport_at_once(pycram.task.TASK_TREE)
    pycram.task.TASK_TREE.execute()
    pycram.task.TASK_TREE.generate_dot().render("out/reorganization_after.dot", view=view)

def transform_transport_at_once(task_tree):
    place_node = task_tree.get_child_by_path("transport.0/place").copy()
    task_tree.get_child_by_path("transport.0/navigate.1").delete_following(True)
    task_tree.get_child_by_path("transport.1/place").insert_after(place_node)
    task_tree.get_child_by_path("transport.1/park_arms.2").code.args = (Arms.BOTH, )

@with_tree
def set_table(destination="kitchen_island_countertop", view=False, optimize=False):
    ActionDesignator(ParkArmsDescription(Arms.BOTH)).perform()

    ## FETCH BOWL
    attempts = 0
    middle_drawer_desig = ObjectDesignator([('type', 'drawer'), ('name', 'sink_area_left_middle_drawer'), ('part-of', kitchen)])
    robot_position = reach_position_generator(middle_drawer_desig)
    if optimize:
        target = previous_tree.children[0].get_successful_params_ctx_after("navigate", "detect")[0][0][0]
    else:
        target = next(robot_position)[0]
    ActionDesignator(NavigateDescription(target_position=target)).perform()
    ActionDesignator(OpenActionDescription(middle_drawer_desig,Arms.RIGHT,0.3)).perform()
    ActionDesignator(ParkArmsDescription(Arms.BOTH)).perform()
    bowl_desig = ObjectDesignator([('type', 'bowl')])
    while True:
        try:
            ActionDesignator(LookAtActionDescription(target=[1.4, 0.925, 0.5])).perform()  # bowl1.get_position())).perform()
            bowl_desig = ActionDesignator(DetectActionDescription(bowl_desig)).perform()
            ActionDesignator(PickUpDescription(bowl_desig, arm=Arms.RIGHT)).perform()
            break
        except PlanFailure as f:
            print(f)
            print("Reposition!")
            ActionDesignator(NavigateDescription(target_position=next(robot_position)[0])).perform()
            print("Retry!")
            time.sleep(0.3)
            attempts += 1
            if attempts < 5:
                continue
            else:
                raise f
    ActionDesignator(ParkArmsDescription(Arms.BOTH)).perform()

    ActionDesignator(CloseActionDescription(middle_drawer_desig, Arms.LEFT)).perform()
    ActionDesignator(ParkArmsDescription(Arms.LEFT)).perform()

    ## DELIVER BOWL ##
    target_location_bowl_gen = object_placing_location_generator(bowl_desig, destination)
    target_location_bowl = next(target_location_bowl_gen)
    deliver_robot_position_generator = reach_position_generator(target_location_bowl)
    pos, rot = next(deliver_robot_position_generator)
    while True:
        with SimulatedTaskTree():
            try:
                ActionDesignator(NavigateDescription(target_position=pos, target_orientation=rot)).perform()
                ActionDesignator(PlaceDescription(bowl_desig, target_location=target_location_bowl, arm=Arms.RIGHT)).perform()
                break
            except PlanFailure as f:
                print("Placing failed.")
                pos, rot = next(deliver_robot_position_generator)
                target_location_bowl = next(target_location_bowl_gen)

    ActionDesignator(NavigateDescription(target_position=pos, target_orientation=rot)).perform()
    ActionDesignator(PlaceDescription(bowl_desig, target_location=target_location_bowl, arm=Arms.RIGHT)).perform()
    ActionDesignator(ParkArmsDescription(Arms.RIGHT)).perform()

    ## FETCH SPOON ##
    upper_drawer_desig = ObjectDesignator([('type', 'drawer'), ('name', 'sink_area_left_upper_drawer'), ('part-of', kitchen)])
    container_opening_gen = container_opening_distance_generator(upper_drawer_desig)
    if optimize:
        container_opening = previous_tree.children[0].get_successful_params_ctx_after("open_container", "detect")[0][0][2]
    else:
        container_opening = next(container_opening_gen)
    robot_position = reach_position_generator(ObjectDesignator([]))  # "Hack" to have the right position right away
    ActionDesignator(NavigateDescription(target_position=next(robot_position)[0])).perform()
    spoon_desig = ObjectDesignator([('type', 'spoon')])
    while True:
        try:
            ActionDesignator(OpenActionDescription(upper_drawer_desig, Arms.RIGHT, distance=container_opening)).perform()
            ActionDesignator(ParkArmsDescription(Arms.BOTH)).perform()
            ActionDesignator(LookAtActionDescription(target=[1.38, 0.75, 0.75])).perform()  # spoon.get_position())).perform()
            spoon_desig = ActionDesignator(DetectActionDescription(spoon_desig)).perform()
            ActionDesignator(PickUpDescription(spoon_desig, arm=Arms.RIGHT)).perform()
            break
        except PlanFailure as f:
            print(f)
            container_opening = next(container_opening_gen)
            print("Retry!")
        except StopIteration:
            print("No more retries left.")
            return
    ActionDesignator(ParkArmsDescription(Arms.BOTH)).perform()

    ActionDesignator(CloseActionDescription(upper_drawer_desig, Arms.LEFT)).perform()
    ActionDesignator(ParkArmsDescription(Arms.LEFT)).perform()

    ## DELIVER SPOON ##
    target_location_spoon_gen = object_placing_location_generator(spoon_desig, destination)
    target_location_spoon = next(target_location_spoon_gen)
    deliver_robot_position_generator = reach_position_generator(target_location_spoon)
    pos, rot = next(deliver_robot_position_generator)

    while True:
        with SimulatedTaskTree():
            try:
                ActionDesignator(NavigateDescription(target_position=pos, target_orientation=rot)).perform()
                ActionDesignator(PlaceDescription(spoon_desig, target_location=target_location_spoon, arm=Arms.RIGHT)).perform()
                break
            except PlanFailure as f:
                print("Placing failed.")
                target_location_spoon = next(target_location_spoon_gen)
                pos, rot = next(deliver_robot_position_generator)
    ActionDesignator(NavigateDescription(target_position=pos, target_orientation=rot)).perform()
    ActionDesignator(PlaceDescription(spoon_desig, target_location=target_location_spoon, arm=Arms.RIGHT)).perform()
    ActionDesignator(ParkArmsDescription(Arms.RIGHT)).perform()

    ## TRANSPORT MILK ##
    fridge_desig = ObjectDesignator([('type', 'fridge'), ('name', 'iai_fridge'), ('part-of', kitchen)])
    milk_desig = ObjectDesignator([('type', 'milk'), ('in', fridge_desig)])
    target_location_milk_gen = object_placing_location_generator(milk_desig, destination)
    target_location_milk = next(target_location_milk_gen)
    try:
        with SimulatedTaskTree():
            ActionDesignator(TransportObjectDescription(milk_desig, arm=Arms.LEFT,
                                                        target_location=target_location_milk)).perform()
        ActionDesignator(TransportObjectDescription(milk_desig, arm=Arms.LEFT,
                                                    target_location=target_location_milk)).perform()
    except PlanFailure as f:
        print("Transporting milk failed.")


    ## TRANSPORT CEREAL ##
    cereal_desig = ObjectDesignator([('type', 'cereal')])
    target_location_cereal_gen = object_placing_location_generator(cereal_desig, destination)
    target_location_cereal = next(target_location_cereal_gen)
    try:
        with SimulatedTaskTree():
            ActionDesignator(TransportObjectDescription(cereal_desig, arm=Arms.RIGHT,
                                                        target_location=target_location_cereal)).perform()
        ActionDesignator(TransportObjectDescription(cereal_desig, arm=Arms.RIGHT,
                                                    target_location=target_location_cereal)).perform()
    except PlanFailure as f:
        print("Transporting cereal failed.")

    ## RENDER ##
    pycram.task.TASK_TREE.generate_dot().render("out/set_table.dot", view=view)

@with_tree
def set_table_for_two(optimize=False):
    set_table(optimize=optimize)
    set_table(optimize=optimize)
    world.simulate(3)

def full_demo_optimized():
    global previous_tree
    s = world.save_state()
    print("================ FIRST SET_TABLE_FOR_TWO ===================")
    set_table_for_two()
    previous_tree = pycram.task.TASK_TREE
    world.restore_state(*s)
    print("================ SECOND SET_TABLE_FOR_TWO ===================")
    set_table_for_two(True)
    world.restore_state(*s)
    tt : TaskTreeNode = pycram.task.TASK_TREE

    ## Re-Organize
    print("================ REORGANIZING ===================")

    ## ALL THE NODES THAT WILL BE MOVED
    pickup_bowl2 = tt.get_child_by_path("set_table.1/pick_up.0").copy()
    pickup_bowl2.code.args = (Arms.LEFT, pickup_bowl2.code.args[1])
    nav_bowl2 = tt.get_child_by_path("set_table.1/navigate.1").copy()
    place_bowl2 = tt.get_child_by_path("set_table.1/place.0").copy()
    place_bowl2.code.args = (Arms.LEFT, *place_bowl2.code.args[1:])
    pickup_spoon2 = tt.get_child_by_path("set_table.1/pick_up.1").copy()
    pickup_spoon2.code.args = (Arms.LEFT, pickup_spoon2.code.args[1])
    nav_spoon2 = tt.get_child_by_path("set_table.1/navigate.3").copy()
    place_spoon2 = tt.get_child_by_path("set_table.1/place.1").copy()
    place_spoon2.code.args = (Arms.LEFT, *place_spoon2.code.args[1:])
    nav_cereal = tt.get_child_by_path("set_table.0/transport.1/navigate.0").copy()
    pickup_cereal = tt.get_child_by_path("set_table.0/transport.1/pick_up.0").copy()
    pickup_cereal.code.args = (Arms.LEFT, pickup_cereal.code.args[1])
    place_cereal = tt.get_child_by_path("set_table.0/transport.1/place.0").copy()
    place_cereal.code.args = (Arms.LEFT, *place_cereal.code.args[1:])

    ## Non-copied, will need reference
    park_arms = tt.get_child_by_path("set_table.0/park_arms.0").copy()
    park_arms.code.args = (Arms.LEFT,)
    closing_bowl_drawer = tt.get_child_by_path("set_table.0/close_container.0")
    closing_spoon_drawer = tt.get_child_by_path("set_table.0/close_container.1")

    # INSERTION POINTS
    pickup_bowl1 = tt.get_child_by_path("set_table.0/pick_up.0")  # after: pickup_bowl2
    place_bowl1 = tt.get_child_by_path("set_table.0/place.0")  # after: nav and place bowl2, park_arms with left
    opening_spoon_drawer = tt.get_child_by_path("set_table.0/open_container.1")  # before: closing_bowl_drawer
    pickup_spoon1 = tt.get_child_by_path("set_table.0/pick_up.1")  # after: pickup_spoon2
    place_spoon1 = tt.get_child_by_path("set_table.0/place.1")  # after: nav and place bowl2, park_arms with left
    close_fridge = tt.get_child_by_path("set_table.0/transport.0/close_container.0")  # after: nav cereal, pickup
    place_milk = tt.get_child_by_path("set_table.0/transport.0/place.0")  # after: place cereal

    tt.generate_dot().render("out/ENDE_vorher.dot")
    print(tt.get_child_by_path("set_table.0").children)
    # INSERTION
    pickup_bowl1.insert_after(pickup_bowl2)
    place_bowl1.insert_after(nav_bowl2)
    nav_bowl2.insert_after(place_bowl2)
    place_bowl2.insert_after(park_arms.copy())
    opening_spoon_drawer.insert_before(closing_bowl_drawer.copy())
    closing_bowl_drawer.delete()
    pickup_spoon1.insert_after(pickup_spoon2)
    place_spoon1.insert_after(nav_spoon2)
    nav_spoon2.insert_after(place_spoon2)
    place_spoon2.insert_after(park_arms.copy())
    close_fridge.insert_after(nav_cereal)
    new_closing_spoon_drawer = closing_spoon_drawer.copy()
    nav_cereal.insert_after(new_closing_spoon_drawer)
    new_closing_spoon_drawer.insert_after(pickup_cereal)
    closing_spoon_drawer.delete()
    place_milk.insert_after(place_cereal)
    last_park = park_arms.copy()
    last_park.code.args = (Arms.BOTH, )
    place_cereal.insert_after(last_park)

    ## Just delete the whole second set_table?
    tt.get_child_by_path("set_table.0/transport.1").delete()
    tt.get_child_by_path("set_table.1").delete()

    tt.generate_dot().render("out/ENDE_nachher.dot")
    print("AFTER ::::::::::::::::::::::::::::::")
    print(tt.get_child_by_path("set_table.0").children)


    world.restore_state(*s)
    print("================ THIRD SET_TABLE_FOR_TWO - THE RE-EXECUTION ===================")
    tt.execute()
    # tt.generate_dot().render("out/ENDE.dot")

state = world.save_state()
# introspection_demo()
# world.restore_state(*state)
# prospection_demo()
# world.restore_state(*state)
# reorganization_demo()
# world.restore_state(*state)
# reorganization_demo()
# world.restore_state(*state)
# set_table_for_two()
full_demo_optimized()
# world.simulate(3)