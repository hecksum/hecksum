"""
Call with the name of a ReferenceFactory to try it out.
$ python try_reference.py test_failure
"""
from pprint import pprint
import sys
from time import time

from hecksum import reference_factories

factory_name = sys.argv[1]
print(factory_name)
factory: reference_factories.ReferenceFactory = getattr(reference_factories, factory_name)
ref = factory.make()
pprint(ref.dict())
start = time()
download_checksum = ref.get_download_checksum()
print(time() - start)
print(f'{download_checksum = }')
print(f'Valid: {ref.checksum == download_checksum}')
