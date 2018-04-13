import os
import toml
import platform
import requests
from pathlib import Path

from django.conf import settings

import logging
logger = logging.getLogger(__name__)


def getGenesisData():
    """
    Get a copy of the genesis transaction file from the web.
    """
    genesisUrl = os.getenv(
        'GENESIS_URL', 'http://von-web:8000/genesis').lower()
    response = requests.get(genesisUrl)
    return response.text


def checkGenesisFile(genesis_txn_path):
    """
    Check on the genesis transaction file and create it if it does not exist.
    """
    genesis_txn_file = Path(genesis_txn_path)
    if not genesis_txn_file.exists():
        if not genesis_txn_file.parent.exists():
            genesis_txn_file.parent.mkdir(parents=True)
        data = getGenesisData()
        print(data)
        with open(genesis_txn_path, 'x') as genesisFile:
            genesisFile.write(data)


class Configurator():

    config = {}

    def __init__(self):
        # Load entity config
        config_path = os.path.abspath(settings.BASE_DIR + '/config.toml')
        try:
            with open(config_path, 'r') as config_file:
                config_toml = config_file.read()
        except FileNotFoundError as e:
            logger.error('Could not find config.toml. Exiting.')
            raise

        self.config = toml.loads(config_toml)

        genesis_txn_path = "/app/.genesis"

        checkGenesisFile(genesis_txn_path)
        self.config["genesis_txn_path"] = genesis_txn_path
        # bhs: configuring/grabbing the wallet seed is now done through agent.py
        # at least in theory. so i'm commenting this one out to make sure
        # we are using the same env vars as much as possible :(
        #
        # Wallet seeds should be configurable through env or the config file
#        self.config["wallet_seed"] = os.getenv('WALLET_SEED',
#            self.config["wallet_seed"])
