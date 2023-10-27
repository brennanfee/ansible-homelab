#!/usr/bin/env python3

import tempfile
import requests
import os
import shutil
import filecmp
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = """
---
module: manage_apt_key
version_added: 0.1.0
short_description:  Replacement for apt_key on Debian systems.
description:
     - The apt-key tool has been deprecated on Debian systems.  This is a replacement for the
      Ansible apt_key module that performs GnuPG key importation and management the "right" way.
      This requires setting up the Debian import source using the [signed-by=<path>] block in order
      to work correctly.  Doing so will mean that only that specific key will be used for that
      specific Debian repository, providing the best security possible.
options:
  input_key_file:
    description:
      - The key to import.  This can be an URL, in which case the key will first be downloaded.
      This can also be a simple path to a local file.
    required: true
    default: null

  output_key_file:
    description:
      - The destination for the key.  It must have a .gpg extension and if the string provided does
      not contain that extension it will be appended.  This can be a full path or a simple file
      name in which case the default_key_path will be prepended.
    required: true
    default: null

  default_key_path:
    description:
      - If output_key_file is a file name with no path information, this path will be prepended to
      the file name as the destination location.
    required: false
    default: /etc/apt/keyrings

  gpg_bin_path:
    description:
      - Location of GPG binary
    require: false
    default: /usr/bin/gpg

  state:
    description:
      - Whether to import (C(present), C(latest)), or remove (C(absent)) a key. C(latest) will only
      report changes if the contents of the key file were actually updated.
    required: false
    choices: [ "present", "absent", "latest" ]
    default: "present"

notes: []
requirements: [ gpg ]
author: Brennan Fee
"""

EXAMPLES = """
- name: Install GPG key from a URL
  manage_apt_key:
    input_key_file: "https://download.docker.com/linux/ubuntu/gpg"
    output_key_file: "docker-archive-keyring.gpg"

- name: Install GPG key from a local file
  manage_apt_key:
    input_key_file: "/home/ansible/key.gpg"
    output_key_file: "docker-archive-keyring.gpg"

- name: Ensure a key file does NOT exist
  manage_apt_key:
    input_key_file: ""
    output_key_file: "docker-archive-keyring.gpg"
    state: absent

- name: Ensure we have the latest key
  manage_apt_key:
    input_key_file: "https://download.docker.com/linux/ubuntu/gpg"
    output_key_file: "docker-archive-keyring.gpg"
    state: latest
"""


class ManageAptKey:
    def __init__(self, module):
        self.m = module
        self.changed = False
        self.debugMessages = []

        self._determine_key_file_name()
        if self.m.params["state"] == "absent":
            self.changed = self._remove_key()
        else:
            self.changed = self._execute_task()

    def _debug(self, msg):
        self.debugMessages.append(msg)

    def _determine_key_file_name(self):
        # Check to make sure the key name ends in the .gpg extension, add it if not
        _, output_ext = os.path.splitext(self.m.params["output_key_file"])
        if output_ext != ".gpg":
            self.m.params["output_key_file"] = f"{self.m.params['output_key_file']}.gpg"

        # If they included a path, use their entire path... otherwise add the key_path
        if os.path.dirname(self.m.params["output_key_file"]) == "":
            self.m.params["output_key_file"] = os.path.join(
                self.m.params["default_key_path"], self.m.params["output_key_file"]
            )

        self._debug(f"Final destination file name: {self.m.params['output_key_file']}")

    def _remove_key(self):
        if os.path.exists(self.m.params["output_key_file"]):
            self._debug("Removing key file.")
            os.remove(self.m.params["output_key_file"])
            return True
        else:
            self._debug("No key file to remove.")
            return False

    def _execute_task(self):
        if os.path.exists(self.m.params["output_key_file"]) and self.m.params["state"] == "present":
            self._debug("State is 'present' and key file already exists.")
            return False

        temp_handle, temp_file = tempfile.mkstemp()
        gpg_file = f"{temp_file}.gpg"
        self._debug(f"Temp file: {temp_file}")

        if self.m.params["input_key_file"].startswith("http"):
            self._debug("Downloading key file from the internet")
            r = requests.get(self.m.params["input_key_file"], allow_redirects=True)
            with os.fdopen(temp_handle, "wb") as f:
                f.write(r.content)
        else:
            self._debug("Copying local key file")
            if os.path.exists(self.m.params["input_key_file"]):
                shutil.copyfile(self.m.params["input_key_file"], temp_file)

        if not os.path.exists(temp_file):
            raise Exception("Unable to read key file.")

        _, file_type, _ = self.m.run_command(["file", "-b", temp_file])
        file_type = file_type.rstrip()
        self._debug(f"Key file type: {file_type}")

        if file_type == "PGP public key block Public-Key (old)":
            # Note: The command automatically adds the .gpg extension
            resRc = self._execute_gpg(f'--batch --yes --dearmor --keyring=gnupg-ring "{temp_file}"')
            if resRc != 0:
                raise Exception(f"GPG returned error {resRc} during dearmor.")
        elif file_type == "PGP public key block Secret-Key":
            _, temp_keyring = tempfile.mkstemp(".gpg")

            resRc = self._execute_gpg(
                '--batch --yes --no-default-keyring --keyring=gnupg-ring:"'
                f'{temp_keyring}" --quiet --import "{temp_file}"'
            )
            if resRc != 0:
                raise Exception(f"GPG returned error {resRc} during import.")

            resRc = self._execute_gpg(
                '--batch --yes --no-default-keyring --keyring=gnupg-ring:"'
                f'{temp_keyring}" --export --output "{gpg_file}"'
            )
            if resRc != 0:
                raise Exception(f"GPG returned error {resRc} during export.")

            os.remove(temp_keyring)
        elif file_type == "PGP/GPG key public ring (v4)":
            shutil.copyfile(temp_file, f"{gpg_file}")
        else:
            raise Exception("Invalid file type.")

        os.remove(temp_file)

        if os.path.exists(self.m.params["output_key_file"]) and self.m.params["state"] == "latest":
            if filecmp.cmp(gpg_file, self.m.params["output_key_file"]):
                self._debug("Key file is already latest.")
                return False

        output_dir = os.path.dirname(self.m.params["output_key_file"])
        if not os.path.exists(output_dir):
            self._debug("Creating output key path because it does not exist.")
            os.makedirs(output_dir)

        self._debug("Copy new or updated key file into place.")
        shutil.move(gpg_file, self.m.params["output_key_file"])
        return True

    def _execute_gpg(self, cmd):
        check_mode = "--dry-run" if self.m.check_mode else ""
        gpg_bin_path = self.m.get_bin_path(self.m.params["gpg_bin_path"], True)

        to_execute = f"{gpg_bin_path} {check_mode} {cmd}"
        self._debug(f"command: {to_execute}")
        rc, _, _ = self.m.run_command(to_execute)
        return rc


def main():
    module = AnsibleModule(
        argument_spec=dict(
            input_key_file=dict(required=True, type="str"),
            output_key_file=dict(required=True, type="str"),
            default_key_path=dict(default="/etc/apt/keyrings", type="str"),
            gpg_bin_path=dict(default="/usr/bin/gpg", type="str"),
            state=dict(default="present", choices=["absent", "present", "latest"]),
        ),
        supports_check_mode=True,
    )

    aak = ManageAptKey(module)

    result = {"changed": aak.changed, "debug": aak.debugMessages}

    module.exit_json(**result)


if __name__ == "__main__":
    main()
