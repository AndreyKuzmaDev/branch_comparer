import json

import typer
from typing_extensions import Annotated
import requests
from packaging.version import Version, InvalidVersion

API_URL = "https://rdb.altlinux.org/api/export/branch_binary_packages/"
BRANCH_SISYPHUS = "sisyphus"
BRANCH_P11 = "p11"

def is_older(version1 : str, version2 : str) -> bool:
    try:
        v1 = Version(version1)
        v2 = Version(version2)
        return v1 < v2
    except InvalidVersion:
        return False

def get_packages_from_api(arch : str) -> dict:
    if arch != "":
        arch = "?arch=" + arch
    r_sisyphus = requests.get(API_URL + BRANCH_SISYPHUS + arch).json()
    r_p11 = requests.get(API_URL + BRANCH_P11 + arch).json()
    if 'errors' in r_sisyphus and 'errors' in r_p11:
        print("Error:", r_sisyphus['errors'])
        return dict()

    return {
        'sisyphus': r_sisyphus['packages'],
        'p11': r_p11['packages']
    }


def compare(
    arch : Annotated[str, typer.Argument(help="Architecture (x86_64, aarch64, i586, noarch, x86_64-i586)")] = ""
):
    p = get_packages_from_api(arch)
    with open('out.json', 'w') as f:
        json.dump(p, f)

if __name__ == '__main__':
    print(is_older("228", "228.1a"))