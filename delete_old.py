import os

import requests


def delete_old():
    while True:
        headers = {'Authorization': f'Bearer {os.environ["AIRTABLE_API_KEY"]}'}
        payload = {
            'filterByFormula': "DATETIME_DIFF(TODAY(), {Checked UTC}, 'hours') > 24"

        }
        checks = requests.get(
            'https://api.airtable.com/v0/appPt1p6IWk5Cjv2E/Checks',
            params=payload,
            headers=headers
        ).json()['records']
        if not checks:
            break
        while checks:
            to_delete = [check['id'] for check in checks[-10:]]
            payload = {'records': to_delete}
            r = requests.delete('https://api.airtable.com/v0/appPt1p6IWk5Cjv2E/Checks', params=payload, headers=headers)
            r.raise_for_status()
            del checks[-10:]


if __name__ == '__main__':
    delete_old()
