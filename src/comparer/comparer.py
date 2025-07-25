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
    out_path : Annotated[str, typer.Argument(help="Path to output file")] = 'comparison.json',
    arch : Annotated[str, typer.Option(help="Find packages with specific architecture (x86_64, aarch64, i586, noarch, x86_64-i586)")] = "",
    detailed: Annotated[bool, typer.Option(help="Write to file detailed info about packages (default - just names)")] = False,
    find_sisyphus_only : Annotated[bool, typer.Option(help="Find packages that present only in sisyphus")] = True,
    find_p11_only : Annotated[bool, typer.Option(help="Find packages that present only in p11")] = True,
    find_outdated : Annotated[bool, typer.Option(help="Find packages that have more recent version on p11")] = True,
    use_release : Annotated[bool, typer.Option(help="Use release number instead of version number to detect outdated packages")] = False,
    verbose : Annotated[bool, typer.Option(help="Print info about progress")] = False,
):
    if verbose:
        print("Getting info...")

    packages_sisyphus, packages_p11, arches = get_packages_from_api(arch)
    names = set(i['name'] for i in packages_sisyphus).union(set(i['name'] for i in packages_p11))

    if verbose:
        print("Done!")
        print("Comparing branches...")

    s_structured = {i : {} for i in arches}
    for package in packages_sisyphus:
        s_structured[package['arch']][package['name']] = package

    p_structured = {i : {} for i in arches}
    for package in packages_p11:
        p_structured[package['arch']][package['name']] = package

    if detailed:
        package_list = dict
    else:
        package_list = list

    one_arch = {}
    if find_sisyphus_only:
        one_arch['sisyphus_only'] = package_list()
    if find_p11_only:
        one_arch['p11_only'] = package_list()
    if find_outdated:
        one_arch['outdated'] = package_list()
    output = {i : deepcopy(one_arch) for i in arches}

    if use_release:
        is_older = is_older_release
    else:
        is_older = is_older_version


    for name in names:
        for a in arches:
            if find_sisyphus_only and name in s_structured[a] and name not in p_structured[a]:
                if not detailed:
                    output[a]['sisyphus_only'].append(name)
                else:
                    output[a]['sisyphus_only'][name] = s_structured[a][name]
            if find_p11_only and name not in s_structured[a] and name in p_structured[a]:
                if not detailed:
                    output[a]['p11_only'].append(name)
                else:
                    output[a]['p11_only'][name] = p_structured[a][name]
            if find_outdated and name in s_structured[a] and name in p_structured[a] and is_older(s_structured[a][name], p_structured[a][name]):
                if not detailed:
                    output[a]['outdated'].append(name)
                else:
                    output[a]['outdated'][name] = s_structured[a][name]
                    output[a]['outdated'][name]['latest_version'] = p_structured[a][name]['version']
                    output[a]['outdated'][name]['latest_release'] = p_structured[a][name]['release']


    if arch != "":
        output = output[arch]

    if verbose:
        print("Done!")
        print("Writing to file...")

    with open(out_path, 'w') as f:
        json.dump(output, f)

    if verbose:
        print("Done!")


if __name__ == '__main__':
    compare()
