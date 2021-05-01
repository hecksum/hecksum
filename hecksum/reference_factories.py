import re
from typing import Callable, Generator

from hecksum.classes import Reference, Version
from hecksum.functions import get_raised
from settings import IGNORED_EXCEPTIONS

reference_factories = []


def reference_factory(func: Callable) -> Callable:
    def f():
        references = []
        try:
            for reference in func():
                references.append(reference)
        except IGNORED_EXCEPTIONS:
            pass
        return references

    reference_factories.append(f)
    return f


@reference_factory
def codecov_bash_uploader() -> Generator[Reference, None, None]:
    download_url = 'https://codecov.io/bash'
    script = get_raised(download_url).text
    version_number = re.search(r'VERSION="(.*)"', script).group(1)
    checksum_url = f'https://raw.githubusercontent.com/codecov/codecov-bash/{version_number}/SHA512SUM'
    checksum_text = get_raised(checksum_url).text
    checksum = re.search(r'(.*) {2}codecov', checksum_text).group(1)
    reference = Reference(
        project_slug='codecov-bash-uploader',
        version=Version(number=version_number),
        algorithm='sha512',
        download_url=download_url,
        checksum=checksum
    )
    yield reference


@reference_factory
def transmission():
    versions = [
        ('Transmission-{version}.dmg', 'sha256_dmg', 'current_version_dmg', 'MacOS', None),
        ('transmission-{version}-x86.msi', 'sha256_msi32', 'current_version_msi', 'Windows', 'x86'),
        ('transmission-{version}-x64.msi', 'sha256_msi64', 'current_version_msi', 'Windows', 'x64'),
        ('transmission-{version}.tar.xz', 'sha256_tar', 'current_version_tar', 'Linux', None)
    ]
    for file_name_template, sha_key, version_key, os, platform in versions:
        constants = get_raised('https://transmissionbt.com/includes/js/constants.js').text
        checksum = re.search(f'{sha_key}: "(.*)"', constants).group(1)
        version_number = re.search(f'{version_key}: "(.*)"', constants).group(1)
        file_name = file_name_template.format(version=version_number)
        download_url = f'https://github.com/transmission/transmission-releases/raw/master/{file_name}'
        version = Version(number=version_number, os=os)
        reference = Reference(
            project_slug='transmission',
            version=version,
            algorithm='sha256',
            download_url=download_url,
            checksum=checksum,
        )
        yield reference

#
# '''
#    Doppler CLI releases on 23 architectures as of 04/29/2021, this reference takes in an architecture and attempts
#    to verify the doppler CLI release for that architecture. Doppler also releases each architecture in multiple formats.
#    This reference does not handle the multiple formats, instead it picks the first packaging it finds and uses that
#    as the release to download and verify.
# '''
#
#
# class Doppler(ReferenceFactory):
#     algorithm = 'sha256'
#     architecture: str
#
#     # TODO: Doppler releases in multiple formats per architecture. This doesn't handle that and
#     # only retrieves the first file for a particular architecture. We should find a way to support
#     # all the releases in whichever format.
#     def _populate(self, ref: Reference) -> None:
#         latest_release_url = requests.get('https://github.com/DopplerHQ/cli/releases/latest').url
#         version = re.search(r'\d+\.\d+\.\d+', latest_release_url)[0]
#         ref.checksum_url = f'https://github.com/DopplerHQ/cli/releases/download/{version}/checksums.txt'
#         checksum = get_raised(ref.checksum_url).text
#         regex_string = fr'([\w\d]{{64}}) {{2}}(doppler_{version}_{self.architecture}\.[\w\.]+)'
#         release_chucksum = re.search(regex_string, checksum)
#         ref.checksum = release_chucksum.group(1)
#         release_file_name = release_chucksum.group(2)
#         ref.download_url = f'https://github.com/DopplerHQ/cli/releases/download/{version}/{release_file_name}'
#
# ['linux_amd64',
# 'linux_i386',
# 'linux_armv7',
# 'openbsd_arm64',
# 'linux_armv6',
# 'openbsd_armv6',
# 'macOS_amd64',
# 'macOS_arm64',
# 'freebsd_armv7',
# 'openbsd_amd64',
# 'openbsd_i386',
# 'linux_arm64',
# 'openbsd_armv7',
# 'freebsd_amd64',
# 'netbsd_amd64',
# 'windows_amd64',
# 'netbsd_armv7',
# 'freebsd_arm64',
# 'netbsd_i386',
# 'netbsd_armv6',
# 'freebsd_armv6',
# 'windows_armv7',
# 'windows_armv6',]