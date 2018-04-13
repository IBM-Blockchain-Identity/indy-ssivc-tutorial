#!/bin/bash

set -e

if [ ! -z "$KUBERNETES" ]; then
  if [ ! -d "/var/lib/indy/sandbox/keys" ]; then
    echo "Ledger does not exist - recreating..."
    chmod -R 755 /var/lib/indy && \
    chown -R indy:indy /var/lib/indy && \
    rm -rf /var/lib/indy/* && \
    su -c "generate_indy_pool_transactions --nodes 4 --clients 0 --nodeNum ${NODENUM} --ips \"${NODE_1_SERVICE_HOST},${NODE_2_SERVICE_HOST},${NODE_3_SERVICE_HOST},${NODE_4_SERVICE_HOST}\"" indy &&
    su -c "start_indy_node Node${NODENUM} ${NODEPORT} ${APIPORT}" indy
  else
    echo "Ledger exists - using..."
    su -c "start_indy_node Node${NODENUM} ${NODEPORT} ${APIPORT}" indy
  fi
else
  NODE_NUM="${1}"
  START_PORT="9700"

  if [ ! -d "/var/lib/indy/sandbox/keys" ]; then
    echo "Ledger does not exist - recreating..."

    if [ ! -z "$IPS" ]; then
      echo von_generate_transactions -s "$IPS" -n "$NODE_NUM"
      su -c "von_generate_transactions -s \"$IPS\" -n \"$NODE_NUM\"" indy
    elif [ ! -z "$IP" ]; then
      echo von_generate_transactions -i "$IP" -n "$NODE_NUM"
      su -c "von_generate_transactions -i \""$IP\"" -n \"$NODE_NUM\"" indy
    else
      echo von_generate_transactions -n "$NODE_NUM"
      su -c "von_generate_transactions -n \"$NODE_NUM\"" indy
    fi
  else
    echo "Ledger exists - using..."
  fi

  echo start_indy_node "Node""$NODE_NUM" $((START_PORT + ( NODE_NUM * 2 ) - 1 )) $(( START_PORT + ( NODE_NUM * 2 ) ))
  su -c "start_indy_node \"Node\"\"$NODE_NUM\" $((START_PORT + ( NODE_NUM * 2 ) - 1 )) $(( START_PORT + ( NODE_NUM * 2 ) ))" indy
fi
