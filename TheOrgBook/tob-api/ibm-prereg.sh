#!/bin/bash

echo sleeping ...
sleep 10

SEEDS=( ${INDY_WALLET_SEED} )
echo "Wallet keys: ${SEEDS}"
for seed in "${SEEDS[@]}"; do
  if [ ! -z "${LEDGER_URL}/register" ] && [ ! -z "${seed}" ]; then
    echo "================================================================================"
    echo "Attempting to register our wallet seed '${seed}' at ${SEED_REGISTRATION_URL}"
    echo "================================================================================"
    DATA=$(printf '{"seed":"%s"}' "${seed}")
    curl -X POST -H "Content-Type: application/json" ${LEDGER_URL}/register -d ${DATA}
  else
    echo "================================================================================"
    echo "One of the wallet seeds or LEDGER_URL is not set."
    echo "Remember to register with von-web yourself."
    echo "================================================================================"
  fi
done

python manage.py migrate &&
python manage.py runserver 0.0.0.0:8080
