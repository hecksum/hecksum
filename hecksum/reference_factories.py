from functools import wraps
import re
from typing import Callable, Generator

from hecksum.classes import Reference, Version
from hecksum.functions import get_raised
from hecksum.releases.doppler import doppler_releases
from hecksum.releases.transmission import transmission_releases
from settings import IGNORED_EXCEPTIONS

reference_factories = []


def reference_factory(func: Callable) -> Callable:
    reference_factories.append(func)
    return func


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
    for file_name_template, sha_key, version_key, os, platform in transmission_releases:
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


'''
    Doppler CLI releases on 23 architectures as of 04/29/2021, this reference takes in an architecture and attempts
    to verify the doppler CLI release for that architecture. Doppler also releases each architecture in multiple formats.
    This reference does not handle the multiple formats, instead it picks the first packaging it finds and uses that
    as the release to download and verify.
    Doppler CLI github: https://github.com/DopplerHQ/cli
'''


@reference_factory
def doppler():
    for os, architecture in doppler_releases:
        # Start by retrieving the latest release of doppler and the published checksums from that release
        latest_release_url = get_raised('https://github.com/DopplerHQ/cli/releases/latest').url
        latest_version = re.search(r'\d+\.\d+\.\d+', latest_release_url)[0]
        checksum_url = f'https://github.com/DopplerHQ/cli/releases/download/{latest_version}/checksums.txt'
        published_checksums = get_raised(checksum_url).text

        # Extract the checksum from the published_checksum we downloaded
        regex_string = fr'([\w\d]{{64}}) {{2}}(doppler_{latest_version}_{os}_{architecture}\.[\w\.]+)'
        release_chucksum = re.search(regex_string, published_checksums)
        release_file_name = release_chucksum.group(2)

        checksum = release_chucksum.group(1)
        download_url = f'https://github.com/DopplerHQ/cli/releases/download/{latest_version}/{release_file_name}'

        reference = Reference(
            project_slug='doppler',
            version=Version(number=latest_version, os=os),
            algorithm='sha256',
            download_url=download_url,
            checksum=checksum
        )
        yield reference
