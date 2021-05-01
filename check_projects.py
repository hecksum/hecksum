from delete_old import delete_old
from hecksum.db_models import Project

delete_old()

projects = [
    Project(airtable_id='rec1stqERwHeVoyTr', name='Codecov Bash Uploader'),
    Project(airtable_id='recPGEEzOeJ2gNh7u', name='Transmission Mac OS X'),
    Project(airtable_id='rec6xk5CUPcjsqIyD', name='Transmission Windows x86'),
    Project(airtable_id='recZOMQpGtd524lsj', name='Transmission Windows x64'),
    Project(airtable_id='recVSRZVqVDt2SCom', name='Transmission Linux'),
]
for project in projects:
    check = project.check()
    print(check)
    check.post()
