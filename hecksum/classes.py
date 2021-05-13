from enum import Enum
import hashlib
import os
from typing import Optional

from pydantic import BaseModel
import requests

from settings import IGNORED_EXCEPTIONS

# slug: airtable_id
PROJECTS = {}


class Status(str, Enum):
    # todo: change conjugation to match
    passing = 'Passing'
    error = 'Error'
    failing = 'Failing'


class Version(BaseModel):
    number: Optional[str] = None
    os: Optional[str] = None
    platform: Optional[str] = None

    class Config:
        allow_mutation = False

    def __str__(self):
        return ' '.join([value for field_name, value in self if value])


class Check(BaseModel):
    project_slug: str
    version: Version
    status: Status
    checksum: str
    download_url: str

    class Config:
        use_enum_values = True

    def post(self) -> requests.Response:
        headers = {'Authorization': f'Bearer {os.environ["AIRTABLE_API_KEY"]}'}
        payload = {
            'fields': {
                'Project': [PROJECTS[self.project_slug]],
                'Version': str(self.version),
                'Status': self.status,
                'Download': self.download_url,
                'Checksum': self.checksum,
            },
            'typecast': True
        }
        return requests.post('https://api.airtable.com/v0/appPt1p6IWk5Cjv2E/Checks', json=payload, headers=headers)


class Reference(BaseModel):
    project_slug: str
    version: Version
    algorithm: str
    download_url: str
    checksum: str

    class Config:
        allow_mutation = False

    def get_download_checksum(self) -> str:
        h = hashlib.new(self.algorithm)
        r = requests.get(self.download_url, stream=True)
        r.raise_for_status()
        for chunk in r.iter_content(1024 ** 2):
            h.update(chunk)
        checksum = h.hexdigest()
        return checksum

    def check(self) -> Check:
        try:
            download_checksum = self.get_download_checksum()
        except IGNORED_EXCEPTIONS:
            status = Status.error
        else:
            status = Status.passing if self.checksum == download_checksum else Status.failing
        return Check(
            project_slug=self.project_slug,
            version=self.version,
            status=status,
            checksum=self.checksum,
            download_url=self.download_url,
        )
