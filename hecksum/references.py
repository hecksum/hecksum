import hashlib
import re
from typing import cast, Optional

from pydantic import BaseModel, constr, HttpUrl
import requests

from hecksum.functions import get_raised
from settings import IGNORED_EXCEPTIONS


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

    def get_download_checksum(self) -> str:
        h = hashlib.new(self.algorithm)
        r = requests.get(self.download_url, stream=True)
        r.raise_for_status()
        for chunk in r.iter_content(1024**2):
            h.update(chunk)
        checksum = h.hexdigest()
        return checksum


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

'''
   Doppler CLI releases on 23 architectures as of 04/29/2021, this reference takes in an architecture and attempts
   to verify the doppler CLI release for that architecture. Doppler also releases each architecture in multiple formats.
   This reference does not handle the multiple formats, instead it picks the first packaging it finds and uses that
   as the release to download and verify.
'''
class Doppler(ReferenceFactory):
    algorithm = 'sha256'
    architecture: str

    # TODO: Doppler releases in multiple formats per architecture. This doesn't handle that and
    # only retrieves the first file for a particular architecture. We should find a way to support
    # all the releases in whichever format.
    def _populate(self, ref: Reference) -> None:
        latest_release_url = requests.get('https://github.com/DopplerHQ/cli/releases/latest').url
        version = re.search(r'\d+\.\d+\.\d+', latest_release_url)[0]
        ref.checksum_url = f'https://github.com/DopplerHQ/cli/releases/download/{version}/checksums.txt'
        checksum = get_raised(ref.checksum_url).text
        regex_string = fr'([\w\d]{{64}}) {{2}}(doppler_{version}_{self.architecture}\.[\w\.]+)'
        release_chucksum = re.search(regex_string, checksum)
        ref.checksum = release_chucksum.group(1)
        release_file_name = release_chucksum.group(2)
        ref.download_url = f'https://github.com/DopplerHQ/cli/releases/download/{version}/{release_file_name}'


codecov_bash_uploader = CodecovBashUploader()

test_failure = ReferenceFactory(
    download_url=cast(HttpUrl, 'https://hecksum.com/failure.txt'),
    checksum_url=cast(HttpUrl, 'https://hecksum.com/failureSHA512.txt'),
    algorithm='sha512'
)

############
# Transmission Reference Definitions
############

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


############
# Doppler Reference Definitions
############

doppler_linux_amd64 = Doppler(
    architecture='linux_amd64'
)

doppler_linux_i386 = Doppler(
    architecture='linux_i386'
)

doppler_linux_armv7 = Doppler(
    architecture='linux_armv7'
)

doppler_openbsd_arm64 = Doppler(
    architecture='openbsd_arm64'
)

doppler_linux_armv6 = Doppler(
    architecture='linux_armv6'
)

doppler_openbsd_armv6 = Doppler(
    architecture='openbsd_armv6'
)

doppler_macOS_amd64 = Doppler(
    architecture='macOS_amd64'
)

doppler_macOS_arm64 = Doppler(
    architecture='macOS_arm64'
)

doppler_freebsd_armv7 = Doppler(
    architecture='freebsd_armv7'
)

doppler_openbsd_amd64 = Doppler(
    architecture='openbsd_amd64'
)

doppler_openbsd_i386 = Doppler(
    architecture='openbsd_i386'
)

doppler_linux_arm64 = Doppler(
    architecture='linux_arm64'
)

doppler_openbsd_armv7 = Doppler(
    architecture='openbsd_armv7'
)

doppler_freebsd_amd64 = Doppler(
    architecture='freebsd_amd64'
)

doppler_netbsd_amd64 = Doppler(
    architecture='netbsd_amd64'
)

doppler_windows_amd64 = Doppler(
    architecture='windows_amd64'
)

doppler_netbsd_armv7 = Doppler(
    architecture='netbsd_armv7'
)

doppler_freebsd_arm64 = Doppler(
    architecture='freebsd_arm64'
)

doppler_netbsd_i386 = Doppler(
    architecture='netbsd_i386'
)

doppler_netbsd_armv6 = Doppler(
    architecture='netbsd_armv6'
)

doppler_freebsd_armv6 = Doppler(
    architecture='freebsd_armv6'
)

doppler_windows_armv7 = Doppler(
    architecture='windows_armv7'
)

doppler_windows_armv6 = Doppler(
    architecture='windows_armv6'
)
