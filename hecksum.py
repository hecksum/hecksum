from enum import Enum
import hashlib
import os
import re
from typing import cast, ClassVar, Optional

from pydantic import BaseModel, constr, HttpUrl
import requests

DEBUG = bool(os.environ.get('DEBUG', False))
IGNORED_EXCEPTIONS = () if DEBUG else (Exception,)


def get_raised(url: str) -> requests.Response:
    r = requests.get(url)
    r.raise_for_status()
    return r


class BaseReference(BaseModel):
    algorithm: str
    checksum_url: Optional[HttpUrl] = None
    download_url: Optional[HttpUrl] = None
    checksum: Optional[constr(strip_whitespace=True)] = None


class Reference(BaseReference):
    class Config:
        validate_assignment = True

    def populated(self) -> bool:
        return all(self.dict().values())


class ReferenceFactory(BaseReference):
    class Config:
        allow_mutation = False

    def make(self) -> Reference:
        ref = Reference(**self.dict())
        try:
            self._populate(ref)
        except IGNORED_EXCEPTIONS:
            pass
        return ref

    def _populate(self, ref: Reference) -> None:
        ref.checksum = get_raised(ref.checksum_url).text


class CodecovBashUploader(ReferenceFactory):
    algorithm = 'sha512'
    download_url: HttpUrl = 'https://codecov.io/bash'

    def _populate(self, ref: Reference) -> None:
        script = get_raised(ref.download_url).text
        version = re.search(r'VERSION="(.*)"', script).group(1)
        ref.checksum_url = f'https://raw.githubusercontent.com/codecov/codecov-bash/{version}/SHA512SUM'
        checksum = get_raised(ref.checksum_url).text
        ref.checksum = re.search(r'(.*) {2}codecov', checksum).group(1)


class Transmission(ReferenceFactory):
    algorithm = 'sha256'
    checksum_url: HttpUrl = 'https://transmissionbt.com/includes/js/constants.js'
    file_name_template: str
    sha_key: str
    version_key: str

    def _populate(self, ref: Reference) -> None:
        constants = get_raised(ref.checksum_url).text
        ref.checksum = re.search(f'{self.sha_key}: "(.*)"', constants).group(1)
        version = re.search(f'{self.version_key}: "(.*)"', constants).group(1)
        file_name = self.file_name_template.format(version=version)
        ref.download_url = f'https://github.com/transmission/transmission-releases/raw/master/{file_name}'


codecov_bash_uploader = CodecovBashUploader()
test_failure = ReferenceFactory(
    download_url=cast(HttpUrl, 'https://hecksum.com/failure.txt'),
    checksum_url=cast(HttpUrl, 'https://hecksum.com/failureSHA512.txt'),
    algorithm='sha512'
)
transmission_mac = Transmission(
    file_name_template='Transmission-{version}.dmg',
    sha_key='sha256_dmg',
    version_key='current_version_dmg'
)
transmission_win_32 = Transmission(
    file_name_template='transmission-{version}-x86.msi',
    sha_key='sha256_msi32',
    version_key='current_version_msi',
)
transmission_win_64 = Transmission(
    file_name_template='transmission-{version}-x64.msi',
    sha_key='sha256_msi64',
    version_key='current_version_msi',
)
transmission_linux = Transmission(
    file_name_template='transmission-{version}.tar.xz',
    sha_key='sha256_tar',
    version_key='current_version_tar',
)


def create_download_checksum(url: str, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    r = get_raised(url)
    h.update(r.content)
    checksum = h.hexdigest()
    return checksum


class Project(BaseModel):
    name: str
    airtable_id: str
    REFERENCE_FACTORIES: ClassVar[dict[str, ReferenceFactory]] = {
        'rec1stqERwHeVoyTr': codecov_bash_uploader,
        'recU4m6YnYdQ4U76q': test_failure,
        'recPGEEzOeJ2gNh7u': transmission_mac,
        'rec6xk5CUPcjsqIyD': transmission_win_32,
        'recZOMQpGtd524lsj': transmission_win_64,
        'recVSRZVqVDt2SCom': transmission_linux,
    }

    def check(self) -> 'Check':
        reference_factory = self.REFERENCE_FACTORIES[self.airtable_id]
        ref = reference_factory.make()
        try:
            if not ref.populated():
                raise Exception(f'Reference not populated. {ref}')
            download_checksum = create_download_checksum(ref.download_url, ref.algorithm)
        except IGNORED_EXCEPTIONS:
            status = Status.error
        else:
            status = Status.passing if ref.checksum == download_checksum else Status.failing
        return Check(
            project=self,
            status=status,
            checksum=ref.checksum,
            checksum_url=ref.checksum_url,
            download_url=ref.download_url,
        )


class Status(str, Enum):
    passing = 'Passing'
    error = 'Error'
    failing = 'Failing'


class Check(BaseModel):
    project: Project
    status: Status
    checksum: Optional[str]
    checksum_url: Optional[HttpUrl]
    download_url: Optional[HttpUrl]

    class Config:
        use_enum_values = True

    def post(self) -> requests.Response:
        headers = {'Authorization': f'Bearer {os.environ["AIRTABLE_API_KEY"]}'}
        payload = {
            'fields': {
                'Project': [self.project.airtable_id],
                'Status': self.status,
                'Checksum URL': self.checksum_url,
                'Download': self.download_url,
                'Checksum': self.checksum
            },
            'typecast': True
        }
        return requests.post('https://api.airtable.com/v0/appPt1p6IWk5Cjv2E/Checks', json=payload, headers=headers)


def main():
    projects = [
        Project(airtable_id='recU4m6YnYdQ4U76q', name='Test Failure'),
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


if __name__ == '__main__':
    main()
