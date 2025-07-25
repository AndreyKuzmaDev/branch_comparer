import json

import typer
from typing_extensions import Annotated
import requests
from packaging.version import Version, InvalidVersion
from copy import deepcopy

API_URL = "https://rdb.altlinux.org/api/export/branch_binary_packages/"
BRANCH_SISYPHUS = "sisyphus"
BRANCH_P11 = "p11"

def is_older_version(package1 : dict, package2 : dict) -> bool:
    try:
        v1 = Version(package1['version'])
        v2 = Version(package2['version'])
        return v1 < v2
    except InvalidVersion:
        return False

def is_older_release(package1 : dict, package2 : dict) -> bool:
    try:
        r1 = int(package1['release'][3:])
        r2 = int(package2['release'][3:])
        return r1 < r2
    except ValueError:
        return False

def get_packages_from_api(arch : str) -> (dict, dict, set):
    if arch != "":
        arch_link = "?arch=" + arch
    else:
        arch_link = ""
    r_sisyphus = requests.get(API_URL + BRANCH_SISYPHUS + arch_link).json()
    r_p11 = requests.get(API_URL + BRANCH_P11 + arch_link).json()
    if 'errors' in r_sisyphus and 'errors' in r_p11:
        print("Error:", r_sisyphus['errors']['arch'])
        return dict(), dict(), set()

    if arch != "":
        arches = {arch}
    else:
        arches = set(i['arch'] for i in r_sisyphus['packages']).union(set(i['arch'] for i in r_p11['packages']))

    return r_sisyphus['packages'], r_p11['packages'], arches


def compare(
    arch : Annotated[str, typer.Option(help="Architecture (x86_64, aarch64, i586, noarch, x86_64-i586)")] = "",
    find_sisyphus_only : Annotated[bool, typer.Option(help="Look for packages that present only in sisyphus")] = True,
    find_p11_only : Annotated[bool, typer.Option(help="Look for packages that present only in p11")] = True,
    find_outdated : Annotated[bool, typer.Option(help="Look for packages that have more recent version on p11")] = True,
    out_path : Annotated[str, typer.Argument(help="Architecture (x86_64, aarch64, i586, noarch, x86_64-i586)")] = 'comparison.json',
    use_release : Annotated[bool, typer.Option(help="Use release number instead of version number to detect outdated packages")] = False
):
    packages_sisyphus, packages_p11, arches = get_packages_from_api(arch)
    names = set(i['name'] for i in packages_sisyphus).union(set(i['name'] for i in packages_p11))

    s_structured = {i : {} for i in arches}
    for package in packages_sisyphus:
        s_structured[package['arch']][package['name']] = package

    p_structured = {i : {} for i in arches}
    for package in packages_p11:
        p_structured[package['arch']][package['name']] = package

    one_arch = {}
    if find_sisyphus_only:
        one_arch['sisyphus_only'] = []
    if find_p11_only:
        one_arch['p11_only'] = []
    if find_outdated:
        one_arch['outdated'] = []
    output = {i : deepcopy(one_arch) for i in arches}

    if use_release:
        is_older = is_older_release
    else:
        is_older = is_older_version

    for name in names:
        for a in arches:
            if find_sisyphus_only and name in s_structured[a] and name not in p_structured[a]:
                output[a]['sisyphus_only'].append(name)
            if find_p11_only and name not in s_structured[a] and name in p_structured[a]:
                output[a]['p11_only'].append(name)
            if find_outdated and name in s_structured[a] and name in p_structured[a] and is_older(s_structured[a][name], p_structured[a][name]):
                output[a]['outdated'].append(name)

    with open(out_path, 'w') as f:
        json.dump(output, f)


if __name__ == '__main__':
    compare()
