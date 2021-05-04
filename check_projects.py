from delete_old import delete_old
from hecksum.reference_factories import reference_factories

delete_old()

for reference_factory in reference_factories:
    references = reference_factory()
    for reference in references:
        check = reference.check()
        check.post()
