import time
from pycram.designator import MotionDesignator
from pycram.process_module import ProcessModule
from pycram.language import macros, par, pursue, try_all

def succeed():
    time.sleep(2)
    pass

def fail():
    time.sleep(1)
    raise Exception()

start = time.time()
with try_all as s:
    fail()
    succeed()
    succeed()
    fail()
    fail()
    fail()

print(time.time()-start)
print(s.get_value())