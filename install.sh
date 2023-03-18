#!/usr/bin/env bash

APP_NAME="gcli"
SCRIPT_NAME="gcli.py"
INSTALL_DIR="/usr/local/bin/"
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SCRIPT_ABS_PATH="${SCRIPT_DIR}/${SCRIPT_NAME}"
APP_ABS_PATH="${SCRIPT_DIR}/${APP_NAME}"

# Check if user root
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit 0
fi

# Check current os
case "$(uname -s)" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    FreeBSD*)   machine=FreeBSD;;
    *)          machine="false"
esac

if [ "${machine}" == "false" ]; then
    echo "I dont know what is your os"
    exit 1
fi

# Check installation dir
if ! test -d "${INSTALL_DIR}"; then
	echo "Can not find ${INSTALL_DIR}"
	exit 1
fi

# Check script path
if ! test -f "${SCRIPT_ABS_PATH}"; then
	echo "Can not find ${SCRIPT_ABS_PATH}"
	exit 1
fi

pyinstaller "${SCRIPT_ABS_PATH}"

rm -rf "${HOME}/.${APP_NAME}"
mv -v "${SCRIPT_DIR}/dist/${APP_NAME}" "${HOME}/.${APP_NAME}"

if ! test -h ${INSTALL_DIR}/${APP_NAME}; then
     ln -sv ${HOME}/.${APP_NAME}/${APP_NAME} ${INSTALL_DIR}/${APP_NAME}
fi

rm -rfv {build, dist, gcli.spec}

