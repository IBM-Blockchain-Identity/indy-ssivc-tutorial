import os

from .config import Configurator
from .helpers import uuid

from von_agent.nodepool import NodePool
from von_agent.wallet import Wallet
from von_agent.agents import _BaseAgent
from von_agent.agents import Issuer as VonIssuer
from von_agent.agents import Verifier as VonVerifier
from von_agent.agents import HolderProver as VonHolderProver

from von_connector import genesis

import logging
logger = logging.getLogger(__name__)

config = Configurator().config

WALLET_SEED = os.environ.get('INDY_WALLET_SEED')
if not WALLET_SEED or len(WALLET_SEED) is not 32:
    raise Exception('INDY_WALLET_SEED must be set and be 32 characters long.')


class Issuer:
    def __init__(self):
        genesis_config = genesis.config()
        self.pool = NodePool(
            'permitify-issuer',
            genesis_config['genesis_txn_path'])

        self.instance = VonIssuer(
            self.pool,
            Wallet(
                self.pool.name,
                WALLET_SEED,
                config['name'] + ' Issuer Wallet'
            )
        )

    async def __aenter__(self):
        await self.pool.open()
        return await self.instance.open()

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            logger.error(exc_type, exc_value, traceback)

        await self.instance.close()
        await self.pool.close()


class Verifier:
    def __init__(self):
        genesis_config = genesis.config()
        self.pool = NodePool(
            'permitify-verifier',
            genesis_config['genesis_txn_path'])

        self.instance = VonVerifier(
            self.pool,
            Wallet(
                self.pool.name,
                WALLET_SEED,
                config['name'] + ' Verifier Wallet'
            )
        )

    async def __aenter__(self):
        await self.pool.open()
        return await self.instance.open()

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            logger.error(exc_type, exc_value, traceback)

        await self.instance.close()
        await self.pool.close()


class Holder:
    def __init__(self):
        genesis_config = genesis.config()
        self.pool = NodePool(
            'permitify-holder',
            genesis_config['genesis_txn_path'])

        self.instance = VonHolderProver(
            self.pool,
            Wallet(
                self.pool.name,
                WALLET_SEED,
                config['name'] + ' Holder Wallet'
            )
        )

    async def __aenter__(self):
        await self.pool.open()
        instance = await self.instance.open()
        await self.instance.create_master_secret(uuid())
        return instance

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            logger.error(exc_type, exc_value, traceback)

        await self.instance.close()
        await self.pool.close()

async def convert_seed_to_did(seed):
    genesis_config = genesis.config()
    pool = NodePool(
        'util-agent',
        genesis_config['genesis_txn_path'])

    agent = _BaseAgent(
        pool,
        Wallet(
            pool.name,
            seed,
            seed + '-wallet'
        ),
    )

    await agent.open()
    agent_did = agent.did
    await agent.close()
    return agent_did
