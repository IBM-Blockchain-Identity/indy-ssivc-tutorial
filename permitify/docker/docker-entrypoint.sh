#!/bin/bash

echoWarning (){
  _msg=${1}
  _yellow='\033[1;33m'
  _nc='\033[0m' # No Color
  echo -e "${_yellow}${_msg}${_nc}"
}

if [ -z "$@" ]; then
  TEMPLATE_NAME=${TEMPLATE_NAME:-person}
  APPLICATION_IP=${APPLICATION_IP:-0.0.0.0}
  APPLICATION_PORT=${APPLICATION_PORT:-8080}

  echoWarning "----------------------------------------------------------------------------------"
  echoWarning "No command line parameters were provided to the entry point."
  echoWarning "Using the values specified for the environment, or defaults if none are provided."
  echo
  echoWarning "TEMPLATE_NAME: ${TEMPLATE_NAME}"
  echoWarning "APPLICATION_IP: ${APPLICATION_IP}"
  echoWarning "APPLICATION_PORT: ${APPLICATION_PORT}"
  echoWarning "INDY_WALLET_SEED: ${INDY_WALLET_SEED}"
  echoWarning "----------------------------------------------------------------------------------"

  set "${TEMPLATE_NAME}" "python" "manage.py" "runserver" "${APPLICATION_IP}:${APPLICATION_PORT}"
fi

TEMPLATE_NAME=${TEMPLATE_NAME:-$1}
TEMPLATE_DIRECTORY="${HOME}/site_templates/$TEMPLATE_NAME"
shift

echo "================================================================================"
echo "Using template: $TEMPLATE_NAME"
echo "Cmd: $@"
echo "================================================================================"

if [ -d "${TEMPLATE_DIRECTORY}" ]; then
    echo "Copying template directory; ${TEMPLATE_DIRECTORY} ..."
    cp "${TEMPLATE_DIRECTORY}"/* .
else
    echo "Directory ${TEMPLATE_DIRECTORY} doesn't exist."
    exit 1
fi

if [ ! -z "${LEDGER_URL}" ] && [ ! -z "${INDY_WALLET_SEED}" ]; then
	echo "================================================================================"
	echo "Attempting to register our wallet seed '${INDY_WALLET_SEED}' at ${LEDGER_URL}/register"
	echo "================================================================================"
	DATA=$(printf '{"seed":"%s"}' "${INDY_WALLET_SEED}")
	curl -X POST -H "Content-Type: application/json" ${LEDGER_URL}/register -d ${DATA} || true
else
        echo "================================================================================"
        echo "INDY_WALLET_SEED and INDY_WALLET_SEED not set."
	echo "Remember to register with von-web yourself."
        echo "================================================================================"
fi

# python3 manage.py migrate
echo "Starting server ..."
exec "$@"
