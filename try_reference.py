"""
Call with the name of a reference_factory function to try it out.
$ python try_reference.py codecov_bash_uploader
"""
import sys
from time import time

from hecksum.reference_factories import reference_factories

factory_name = sys.argv[1]
print(factory_name)
factory, = [f for f in reference_factories if f.__name__ == factory_name]
start = time()
references = factory()
print(time() - start)
for ref in references:
    print(repr(ref))
    start = time()
    check = ref.check()
    print(repr(check))
    print(time() - start)
