#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 Sam Doran
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = """
---
module:
author:
    - Sam Doran (@samdoran)
version_added: '2.12'
short_description: Create virtual environments using pyenv. Optionally create symbolic links to programs within the virtual environment.
notes: []
description:
    - Create virtual environments with C(pyenv virtualenv). Requires C(pyenv) and C(pyenv-virtualenv) plugin to be installed.
options:
    bin_path:
        description: Path to link any binaries
    venvs:
        description: List of virtual environments to create.
    python_version:
        description: Default version of Python to use for creating virtual environments when not specified.
"""

EXAMPLES = """
- samdoran.macos.pyenv_virtualenv:
"""

RETURN = """
"""

import os

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.process import get_bin_path


def get_venvs(module, pyenv_bin):
    cmd = [pyenv_bin, 'virtualenvs', '--bare', '--skip-aliases']
    rc, stdout, stderr = module.run_command(cmd, path_prefix='/opt/homebrew/bin')

    return stdout.splitlines()


def create_venvs(module, pyenv_bin):
    current_venvs = get_venvs(module, pyenv_bin)
    changed = False
    cmd = [pyenv_bin, 'virtualenv']
    for venv in module.params['venvs']:
        py_version = venv.get('python_version', module.params['python_version'])
        venv_name = "%s-%s" % (venv['name'], py_version)
        
        if any(venv_name in item for item in current_venvs):
            continue

        changed = True
        if not module.check_mode:
            rc, out, err = module.run_command(cmd + [py_version, venv_name], path_prefix='/opt/homebrew/bin')

        if rc != 0:
            module.fail_json("Failed to create virtual environment %s with command %s: %s" % (venv_name, cmd, err))

    return changed


def install_packages(module, pyenv_bin, pyenv_root):
    changed = False
    for venv in module.params['venvs']:
        if venv.get('install') is False:
            continue

        py_version = venv.get('python_version', module.params['python_version'])
        venv_name = "%s-%s" % (venv['name'], py_version)
        packages = venv.get('packages', venv.get('name'))
        if isinstance(packages, str):
            packages = [packages]

        cmd = ['%s/versions/%s/bin/python' % (pyenv_root, venv_name), '-m', 'pip', 'install']
        cmd.extend(packages)

        if not module.check_mode:
            rc, out, err = module.run_command(cmd, path_prefix='/opt/homebrew/bin')
            if rc != 0:
                module.fail_json("Failed to install packages for %s: %s" % (venv_name, err))

            if 'Requirement already satisfied' not in out:
                changed = True

    return changed


def link_binaries(module, bin_path, pyenv_root):
    changed = False
    for venv in module.params['venvs']:
        if venv.get('link') is False:
            continue

        py_version = venv.get('python_version', module.params['python_version'])
        venv_name = "%s-%s" % (venv['name'], py_version)

        # Look for a single binary name or list of binaries
        binaries = venv.get('binaries', venv.get('binary')) or [venv.get('name')]
        if isinstance(binaries, str):
            binaries = [binaries]

        for bin in binaries:
            src = os.path.join(pyenv_root, 'versions', venv_name, 'bin', bin)
            dest = os.path.join(bin_path, bin)
            if os.path.islink(dest):
                current_src = os.readlink(dest)
                if current_src != src:
                    changed = True
                    if not module.check_mode:
                        os.unlink(dest)
                        os.symlink(src, dest)
            else:
                changed = True
                if not module.check_mode:
                    os.symlink(src, dest)

    return changed


def main():
    module = AnsibleModule(
        argument_spec={
            "bin_path": {"type": "path", "default": "~/bin"},
            "venvs": {"type": "list", "elements": "dict", "required": True},
            "python_version": {"type": "str", "default": "3.10.1"},
        },
        supports_check_mode=True,
    )

    bin_path = module.params['bin_path']

    try:
        pyenv_bin = get_bin_path('pyenv', ['/usr/local/bin', '/opt/homebrew/bin'])
    except ValueError:
        module.fail_json("'Could not find 'pyenv'")

    rc, out, err = module.run_command([pyenv_bin, 'root'], path_prefix='/opt/homebrew/bin')
    pyenv_root = out.strip()

    changed_venvs = create_venvs(module, pyenv_bin)
    changed_packages = install_packages(module, pyenv_bin, pyenv_root)
    changed_binaries = link_binaries(module, bin_path, pyenv_root)

    results = {'changed': any((changed_venvs, changed_packages, changed_binaries))}

    module.exit_json(**results)


if __name__ == '__main__':
    main()
