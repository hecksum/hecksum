from collections.abc import Callable
from contextlib import suppress
from enum import Enum
import hashlib
import os
import re
from typing import ClassVar, Optional

from pydantic import BaseModel
import requests


def get_raised(url: str) -> requests.Response:
    r = requests.get(url)
    r.raise_for_status()
    return r


class Reference(BaseModel):
    hash_function: Optional[str] = None
    checksum_url: Optional[str] = None
    download_url: Optional[str] = None
    checksum: Optional[str] = None


class ReferenceFactory(BaseModel):
    # set to url
    hasher: Callable
    checksum_url: Optional[str] = None
    download_url: Optional[str] = None
    checksum: Optional[str] = None

    class Config:
        allow_mutation = False

    def make(self) -> Reference:
        ref = Reference(
            checksum_url=self.checksum_url,
            download_url=self.download_url,
            checksum=self.checksum,
            hash_function=self.hasher.__qualname__,
        )
        with suppress(Exception):
            self._populate(ref)
        return ref

    def _populate(self, ref) -> None:
        ref.checksum = get_raised(ref.checksum_url).text


class CodecovBashUploader(ReferenceFactory):
    hasher = hashlib.sha512
    download_url = 'https://codecov.io/bash'

    def _populate(self, ref) -> None:
        script = get_raised(ref.download_url).text
        version = re.search(r'VERSION="(.*)"', script).group(1)
        ref.checksum_url = f'https://raw.githubusercontent.com/codecov/codecov-bash/{version}/SHA512SUM'
        checksum = get_raised(ref.checksum_url).text
        ref.checksum = re.search(r'(.*) {2}codecov', checksum).group(1)


class Transmission(ReferenceFactory):
    hasher = hashlib.sha256
    checksum_url = 'https://transmissionbt.com/includes/js/constants.js'
    file_name_template: str
    sha_key: str
    version_key: str

    def _populate(self, ref) -> None:
        constants = get_raised(ref.checksum_url).text
        ref.checksum = re.search(f'{ref.sha_key}: "(.*)"', constants).group(1)
        version = re.search(f'{ref.version_key}: "(.*)"', constants).group(1)
        file_name = ref.file_name_template.format(version=version)
        ref.download_url = f'https://github.com/transmission/transmission-releases/raw/master/{file_name}'


codecov_bash_uploader = CodecovBashUploader()
test_failure = ReferenceFactory(
    download_url='https://hecksum.com/failure.txt',
    checksum_url='https://hecksum.com/failureSHA512.txt',
    hasher=hashlib.sha512,
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

    def reference(self) -> Reference:
        return self.REFERENCE_FACTORIES[self.airtable_id].make()


class Status(str, Enum):
    passing = 'Passing'
    error = 'Error'
    failing = 'Failing'


class Check(BaseModel):
    project: Project
    status: Status
    checksum: Optional[str]
    checksum_url: Optional[str]
    download_url: Optional[str]

    @classmethod
    def create(cls, project: Project):
        ref = project.reference()
        # noinspection PyBroadException
        try:
            download_checksum = cls.create_download_checksum(ref.download_url, ref.hash_func)
        except Exception:
            status = Status.error
        else:
            status = Status.passing if ref.checksum == download_checksum else Status.failing
        return cls(
            project=project,
            status=status,
            checksum=ref.checksum,
            checksum_url=ref.checksum_url,
            download_url=ref.download_url,
        )

    @staticmethod
    def create_download_checksum(url: str, hasher: Callable) -> str:
        r = requests.get(url)
        r.raise_for_status()
        checksum = hasher(r.content).hexdigest()
        return checksum

    def post(self) -> None:
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
        requests.post('https://api.airtable.com/v0/appPt1p6IWk5Cjv2E/Checks', json=payload, headers=headers)


def main():
    pass


if __name__ == '__main__':
    main()