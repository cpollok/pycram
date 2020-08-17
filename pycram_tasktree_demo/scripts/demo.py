import time
from pycram.designator import MotionDesignator
from pycram.process_module import ProcessModule
from pycram.language import macros, par, pursue, try_all, try_in_order

# def succeed():
#     time.sleep(2)
#     pass
#
# def fail():
#     time.sleep(1)
#     raise Exception()
#
# start = time.time()
# with try_in_order as s:
#     fail()
#     succeed()
#     fail()
#     fail()
#     fail()
#
# print(time.time()-start)
# print(s.get_value())

import pycram
from pycram.task import with_tree, TaskTreeNode, Code

@with_tree
def test_parent():
    test()
    test()
    test()

@with_tree
def test():
    test_child(param="asd")
    test_child("bsd", param2="muha")
    test_child("csd", "saule")

@with_tree
def test_child(param, param2="default"):
    # test_deep_child()
    print(param)
    print(param2)

@with_tree
def test_deep_child():
    print("asd2")

@with_tree
def test_loop():
    for i in range(3):
        test_deep_child()


# print(pycram.task.TASK_TREE)
# test_parent()
# print(pycram.task.TASK_TREE)
#
# tt = pycram.task.TASK_TREE
# print(pycram.task.TASK_TREE.pp())
# print("="*20)
#
# tt.execute()
# print(pycram.task.TASK_TREE.pp())
# print("="*20)
#
# tt.children[1].delete()
# tt.execute()
# print(pycram.task.TASK_TREE.pp())
# print("="*20)
#
# new_code = Code("", test.__wrapped__)
# new_node = TaskTreeNode(new_code, tt, "")
# tt.children[0].exec_child_next = new_node
# new_node.fix_path()
# tt.execute()
# print(pycram.task.TASK_TREE.pp())
# print("="*20)
#
# dot = tt.generate_dot()
# dot.render("out/test.dot", view=True)


import graphviz as gv
# from graphviz import Graph, Digraph
# dot = Digraph(comment="TestDigraph")
# n = dot.node("1", "Chris")
# dot.node("2", "Ami")
# dot.node("C", "Lilo")
#
# dot.edges(["12","2C"])
# dot.edge("1", "C", constraint="false")
#
# dot_c = Digraph()
# dot_c.node("X", "Mama")
# dot_c.node("Y", "Papa")
# dot_c.node("Z", "Domi")
# dot_c.edges(["XY", "XZ", "YZ"])
# dot.subgraph(dot_c)
#
# dot.node("X", "Plan 0 -- Node 0\ncost=0 h=14.084 : {Look:4}\n* Bd[ObjLoc[a, now], i0, 0.950] = True", shape="box", style="filled") #, colorscheme="pastel16", color="3")
#
# dot.render("out/test.dot", view=True)
from pycram.action_designator import PickUpDescription, ActionDesignator, MoveArmsInSequenceDescription, TransportObjectDescription
from pycram.designator import Designator, ObjectDesignator
from pycram.pr2_description import Arms
import pycram.mobile_pick_place_resolution
from pycram.task import move_node_to_path

# desc = MoveArmsInSequenceDescription(["somewhere"], None)
# desig = ActionDesignator(desc)
# desig.perform()

# desc = PickUpDescription(Designator([("name", "TestObj"), ("pose", "<Object Pose>")]), Arms.LEFT)
desc = TransportObjectDescription(ObjectDesignator([("name", "TestObj"), ("pose", "<Object Pose>")]),
                                  Arms.LEFT, "Somewhere else")
desig = ActionDesignator(desc)
desig.perform()

tt : TaskTreeNode = pycram.task.TASK_TREE
# dot = tt.generate_dot()
# dot.render("out/test.dot", view=True)

# node = tt.get_child_by_path("place_object.0/move_arms.1")
# move_node_to_path(node.copy(), "navigate_near_object", -1)
# move_node_to_path(node.copy(), "navigate_near_object", -1)
# move_node_to_path(node.copy(), "navigate_near_object", -1)
# move_node_to_path(node.copy(), "navigate_near_object", -1)
# tt.get_child_by_path("move_arms").delete()
# tt.get_child_by_path("navigate_near_object").delete_previous(True)

move_node_to_path(tt.get_child_by_path("pickup_object"), "place_object", 1)

tt : TaskTreeNode = pycram.task.TASK_TREE
dot = tt.generate_dot()
dot.render("out/test2.dot", view=True)
# tt.execute()
# dot = tt.generate_dot()
# dot.render("out/test2.dot", view=True)