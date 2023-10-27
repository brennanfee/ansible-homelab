#!/usr/bin/env bash
# Author: Brennan A. Fee
# License: MIT License
#
# This script uses the deb-install script to install Debian/Ubuntu the "Arch"
# way.  The config script sets some values for a specific type of installation
# and then automatically calls the deb-install script.
#
# Short URL: https://tinyurl.com/deb-testing-multi
# Github URL: https://raw.githubusercontent.com/brennanfee/ansible-linux-home/main/bootstrap-configs/debian/testing-multiDisk.bash
#
#
##################  MODIFY THIS SECTION
## Set the deb-install variables\options you want here, make sure to export them.
set_exports() {
  export AUTO_INSTALL_OS=${AUTO_INSTALL_OS:=debian}
  export AUTO_INSTALL_EDITION=${AUTO_INSTALL_EDITION:=testing}
  export AUTO_KERNEL_VERSION=${AUTO_KERNEL_VERSION:=default}

  export AUTO_MAIN_DISK=${AUTO_MAIN_DISK:=smallest}
  export AUTO_SECOND_DISK=${AUTO_SECOND_DISK:=smallest}

  export AUTO_DOMAIN=${AUTO_DOMAIN:=bfee.org}
  export AUTO_CREATE_USER=${AUTO_CREATE_USER:=0}

  export AUTO_CREATE_SERVICE_ACCT=1
  export AUTO_SERVICE_ACCT_SSH_KEY=${AUTO_SERVICE_ACCT_SSH_KEY:=ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAH5mZH2G4fD3f5ofopNdg1NfA4wE4ASwD4drU+w8RYR ansible@bfee.org}

  # Forced settings
  export AUTO_ENCRYPT_DISKS=1
  export AUTO_USE_DATA_DIR=1
}
##################  DO NOT MODIFY BELOW THIS SECTION

check_root() {
  local user_id
  user_id=$(id -u)
  if [[ "${user_id}" != "0" ]]; then
    local RED
    local RESET
    RED="$(tput setaf 1)"
    RESET="$(tput sgr0)"
    echo -e "${RED}ERROR! You must execute the script as the 'root' user.${RESET}\n"
    exit 1
  fi
}

download_deb_installer() {
  local script_file=$1

  local script_url="https://raw.githubusercontent.com/brennanfee/linux-bootstraps/main/scripted-installer/debian/deb-install.bash"

  if [[ ! -f "${script_file}" ]]; then
    # To support testing of other versions of the install script (local versions, branches, etc.)
    if [[ "${CONFIG_SCRIPT_SOURCE:=}" != "" ]]; then
      wget -O "${script_file}" "${CONFIG_SCRIPT_SOURCE}"
    else
      wget -O "${script_file}" "${script_url}"
    fi
  fi
}

read_input_options() {
  # Defaults
  export AUTO_ENCRYPT_DISKS=${AUTO_ENCRYPT_DISKS:=1}
  export AUTO_CONFIRM_SETTINGS=${AUTO_CONFIRM_SETTINGS:=1}
  export AUTO_REBOOT=${AUTO_REBOOT:=0}
  export AUTO_USE_DATA_DIR=${AUTO_USE_DATA_DIR:=0}
  export AUTO_CREATE_SERVICE_ACCT=${AUTO_CREATE_SERVICE_ACCT:=0}

  while [[ "${1:-}" != "" ]]; do
    case $1 in
      -a | --auto | --automatic | --automode | --auto-mode)
        export AUTO_CONFIRM_SETTINGS=0
        export AUTO_REBOOT=1
        ;;
      -c | --confirm | --confirmation)
        export AUTO_CONFIRM_SETTINGS=1
        ;;
      -q | --quiet | --skip-confirm | --skipconfirm | --skip-confirmation | --skipconfirmation | --no-confirm | --noconfirm | --no-confirmation | --noconfirmation)
        export AUTO_CONFIRM_SETTINGS=0
        ;;
      -d | --debug)
        export AUTO_IS_DEBUG=1
        ;;
      --data | --usedata | --use-data)
        export AUTO_USE_DATA_DIR=1
        ;;
      --nodata | --no-data | --nousedata | --no-use-data)
        export AUTO_USE_DATA_DIR=0
        ;;
      --service-acct | --create-service-acct | --svc-acct)
        export AUTO_CREATE_SERVICE_ACCT=1
        ;;
      --no-service-acct | --no-create-service-acct | --no-svc-acct | --nosvc-acct)
        export AUTO_CREATE_SERVICE_ACCT=0
        ;;
      -r | --reboot)
        export AUTO_REBOOT=1
        ;;
      -n | --no-reboot | --noreboot)
        export AUTO_REBOOT=0
        ;;
      -s | --script)
        shift
        CONFIG_SCRIPT_SOURCE=$1
        ;;
      -e | --encrypt | --encrypted)
        export AUTO_ENCRYPT_DISKS=1
        ;;
      -u | --unencrypt | --unencrypted | --not-encrypted | --notencrypted)
        export AUTO_ENCRYPT_DISKS=0
        ;;
      *)
        noop
        ;;
    esac

    shift
  done
}

main() {
  local script_file
  script_file="/tmp/deb-install.bash"

  check_root
  read_input_options "$@"
  set_exports

  download_deb_installer "${script_file}"

  # Now run the script
  bash "${script_file}"
}

main "$@"
