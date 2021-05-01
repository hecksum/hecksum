from delete_old import delete_old
from hecksum.classes import Project

delete_old()

projects = [
    Project(airtable_id='rec1stqERwHeVoyTr', name='Codecov Bash Uploader'),
    Project(airtable_id='recPGEEzOeJ2gNh7u', name='Transmission Mac OS X'),
    Project(airtable_id='rec6xk5CUPcjsqIyD', name='Transmission Windows x86'),
    Project(airtable_id='recZOMQpGtd524lsj', name='Transmission Windows x64'),
    Project(airtable_id='recVSRZVqVDt2SCom', name='Transmission Linux'),
    Project(airtable_id='recAbyXIsNXtCTqG0', name='Doppler linux amd64'),
    Project(airtable_id='recSYll22rCAOJxeZ', name='Doppler linux i386'),
    Project(airtable_id='recfduW1SngHHYh5E', name='Doppler linux armv7'),
    Project(airtable_id='rec5y2KWOIsmOzvvR', name='Doppler openbsd arm64'),
    Project(airtable_id='rec613Kd84C8LDG5J', name='Doppler linux armv6'),
    Project(airtable_id='recGsPwOjP0NlJuLf', name='Doppler openbsd armv6'),
    Project(airtable_id='recrUUgD10DkaOtmx', name='Doppler macOS amd64'),
    Project(airtable_id='recmnF2Khz6oC7V19', name='Doppler macOS arm64'),
    Project(airtable_id='rec0u2DXEAU6YKfiH', name='Doppler freebsd armv7'),
    Project(airtable_id='reckOzKhl10nkgSzd', name='Doppler openbsd amd64'),
    Project(airtable_id='rec7YQ94cDVtApU5J', name='Doppler openbsd i386'),
    Project(airtable_id='recF7Wi9E0pz4eniA', name='Doppler linux arm64'),
    Project(airtable_id='recwhoNNXgerQa6Or', name='Doppler openbsd armv7'),
    Project(airtable_id='recywBFflOyzTDbki', name='Doppler freebsd amd64'),
    Project(airtable_id='rec178Xu6xwR5gyi9', name='Doppler netbsd amd64'),
    Project(airtable_id='recsEXYvQtRrkc9ax', name='Doppler windows amd64'),
    Project(airtable_id='recMxKQLHnRjENMmw', name='Doppler netbsd armv7'),
    Project(airtable_id='rec4OjI4l1DLYkOXo', name='Doppler freebsd arm64'),
    Project(airtable_id='reccc1BO9ICulnVJ6', name='Doppler netbsd i386'),
    Project(airtable_id='recRAn5yVy1LGHZ1E', name='Doppler netbsd armv6'),
    Project(airtable_id='recBheQ4Z6ikftKXU', name='Doppler freebsd armv6'),
    Project(airtable_id='recj96T0Pbp5wWuRX', name='Doppler windows armv7'),
    Project(airtable_id='recIuYEZhjk5he8Dw', name='Doppler windows armv6'),
]
for project in projects:
    check = project.check()
    print(check)
    check.post()
