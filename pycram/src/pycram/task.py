"""Implementation of task.

Functions:
_block -- wrap multiple statements into a single block.

Classes:
GeneratorList -- implementation of generator list wrappers.
"""
import random
from graphviz import Digraph
from typing import List, Dict, Optional, Tuple
from enum import Enum, auto
from queue import Queue
from functools import wraps

TASK_TREE = None
CURRENT_TASK_TREE_NODE = None

# class TaskStatus(Enum):
#     CREATED = auto()
#     RUNNING = auto()
#     SUSPENDED = auto()
#     SUCCEEDED = auto()
#     FAILED = auto()
#     EVAPORATED = auto()
#
#
# class Task:
#     def __init__(self, name:str="TEST", parent:"Task"=None, path:str="", code=None):
#         self.name : str= name
#         self.parent : "Task" = parent
#         self.children : List["Task"] = []
#         self.status : TaskStatus = TaskStatus.CREATED
#         self.result = None
#         self.thread = None
#         self.thread_fun = None
#         self.path : str = path
#         self.code = code
#         self.constraints : List = []
#         self.message_queue : Queue = Queue()


class Code:
    def __init__(self, body, function=None, args : Tuple=(), kwargs : Dict={}):
        self.body = body
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def execute(self):
        return self.function(*self.args, **self.kwargs)

    def pp(self):
        pp = self.function.__name__ + '('
        for arg in self.args:
            pp += str(arg) + ", "
        for kw, kwarg in self.kwargs.items():
            pp += kw + "=" + str(kwarg)
            pp += ", "
        if self.args or self.kwargs:
            pp = pp[:-2]
        pp += ')'
        return pp

class NoopCode(Code):
    def __init__(self):
        # noop = type(None)  # alternative, but can't take arguments
        noop = lambda *args, **kwargs: None
        super().__init__("", noop)

class TaskTreeNode:
    def __init__(self, code=None, parent:"TaskTreeNode"=None, path:str=""):
        self.code = code
        self.parent : Optional["TaskTreeNode"] = parent
        self.children : List["TaskTreeNode"] = []
        self.path : str = path
        self.exec_child_prev : Optional["TaskTreeNode"] = None
        self.exec_child_next : Optional["TaskTreeNode"] = None
        self.exec_step = 0

    def pp(self):
        # return nothing, when whole exec_child_tree is deleted
        if type(self.code) is NoopCode:
            return ""

        pretty = ""

        # Add previous siblings
        if self.exec_child_prev:
            pretty += self.exec_child_prev.pp()

        # If not root, add line break
        if self.parent:
            pretty += "\n"

        # Indent 2 spaces for each level of depth
        parent = self.parent
        while parent:
            pretty += "  "
            parent = parent.parent

        # if not root, add branch symbol thingy
        if self.parent:
            pretty += "|- "

        # finally add function name
        pretty += self.code.function.__name__ + " (" + self.path + ")"

        # add pp for all children
        for c in self.children:
            pretty += c.pp()

        # Add next siblings
        if self.exec_child_next:
            pretty += self.exec_child_next.pp()

        return pretty

    def generate_dot(self, dot=None):
        if not dot:
            dot = Digraph()
        if type(self.code) is NoopCode:
            return dot
        if self.exec_child_prev:
            dot = self.exec_child_prev.generate_dot(dot)
        label = "\n".join([self.path.split("/")[-1], self.code.pp()])
        dot.node(self.path, label, shape="box", style="filled")
        if self.parent:
            dot.edge(self.parent.path, self.path)
        for c in self.children:
            dot = c.generate_dot(dot)
        if self.exec_child_next:
            dot = self.exec_child_next.generate_dot(dot)
        return dot

    def execute(self):
        self.execute_prev()
        self.exec_step = 0
        global CURRENT_TASK_TREE_NODE
        CURRENT_TASK_TREE_NODE = self
        result = self.code.execute()
        CURRENT_TASK_TREE_NODE = CURRENT_TASK_TREE_NODE.parent
        self.execute_next()
        return result

    def execute_prev(self):
        if self.exec_child_prev:
            return self.exec_child_prev.execute()

    def execute_next(self):
        if self.exec_child_next:
            return self.exec_child_next.execute()

    def execute_child(self):
        result = self.children[self.exec_step].execute()
        self.exec_step += 1
        return result

    def delete(self):
        self.code = NoopCode()

    def add_child(self, child:"TaskTreeNode"):
        self.children.append(child)
        child.fix_path()

    # TODO(?): Remove noop nodes from list?
    def gen_children_list(self):
        result = []
        for c in self.children:
            result += c.gen_sibling_list()
        return result

    def gen_sibling_list(self):
        if self.exec_child_prev and self.exec_child_next:
            return self.exec_child_prev.gen_sibling_list() + [self] + self.exec_child_next.gen_sibling_list()
        elif self.exec_child_prev:
            return self.exec_child_prev.gen_sibling_list() + [self]
        elif self.exec_child_next:
            return [self] + self.exec_child_next.gen_sibling_list()
        else:
            return [self]

    def fix_path(self):
        if not self.parent.path:
            self.parent.fix_path()

        max_name = -1
        if self.parent:
            for c in self.parent.children:
                if c is self:
                    continue
                if c.code.function == self.code.function:
                    max_name = max(max_name, int(c.path[-1]))
        self.path = '/'.join([self.parent.path, self.code.function.__name__]) + str(max_name+1)


def with_tree(fun):
    @wraps(fun)
    def handle_tree(*args, **kwargs):
        global TASK_TREE
        global CURRENT_TASK_TREE_NODE
        code = Code("", fun, args, kwargs)
        if CURRENT_TASK_TREE_NODE is None:
            TASK_TREE = TaskTreeNode(code, None, fun.__name__)
            CURRENT_TASK_TREE_NODE = TASK_TREE
            result = CURRENT_TASK_TREE_NODE.execute()
        else:
            new_node = TaskTreeNode(code, CURRENT_TASK_TREE_NODE, '/'.join([CURRENT_TASK_TREE_NODE.path, fun.__name__]))
            if len(CURRENT_TASK_TREE_NODE.children) <= CURRENT_TASK_TREE_NODE.exec_step:
                CURRENT_TASK_TREE_NODE.add_child(new_node)
            result = CURRENT_TASK_TREE_NODE.execute_child()
        return result
    return handle_tree
