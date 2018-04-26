import os
import threading

from von_agent.nodepool import NodePool
from von_agent.wallet import Wallet
from tob_api import hyperledger_indy
from von_agent.agents import Issuer as VonIssuer
from von_agent.agents import Verifier as VonVerifier
from von_agent.agents import HolderProver as VonHolderProver

import logging
logger = logging.getLogger(__name__)

WALLET_SEED = os.environ.get('INDY_WALLET_SEED')
if not WALLET_SEED or len(WALLET_SEED) is not 32:
    raise Exception('INDY_WALLET_SEED must be set and be 32 characters long.')

lock = threading.Lock()

class Issuer:
    def __init__(self):
        config = hyperledger_indy.config()
        self.pool = NodePool(
            'the-org-book-issuer',
            config['genesis_txn_path'])

        self.instance = VonIssuer(
            self.pool,
            Wallet(
                self.pool.name,
                WALLET_SEED,
                'TheOrgBook Issuer Wallet'
            )
        )

    async def __aenter__(self):
        logger.info('acquiring lock for Issuer')
        lock.acquire()
        logger.info('acquired lock for Issuer')
        await self.pool.open()
        return await self.instance.open()

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            logger.error(exc_type, exc_value, traceback)

        await self.instance.close()
        await self.pool.close()
        logger.info('Issuer releasing lock')
        lock.release()


class Verifier:
    def __init__(self):
        config = hyperledger_indy.config()
        self.pool = NodePool(
            'the-org-book-verifier',
            config['genesis_txn_path'])

        self.instance = VonVerifier(
            self.pool,
            Wallet(
                self.pool.name,
                WALLET_SEED,
                'TheOrgBook Verifier Wallet'
            )
        )

    async def __aenter__(self):
        logger.info('acquiring lock for Verifier')
        lock.acquire()
        logger.info('acquired lock for Verifier')
        await self.pool.open()
        return await self.instance.open()

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            logger.error(exc_type, exc_value, traceback)

        await self.instance.close()
        await self.pool.close()
        logger.info('Verifier releasing lock')
        lock.release()


class Holder:
    def __init__(self):
        config = hyperledger_indy.config()
        self.pool = NodePool(
            'the-org-book-holder',
            config['genesis_txn_path'])

        self.instance = VonHolderProver(
            self.pool,
            Wallet(
                self.pool.name,
                WALLET_SEED,
                'TheOrgBook Holder Wallet'
            )
        )

    async def __aenter__(self):
        logger.info('acquiring lock for Holder')
        lock.acquire()
        logger.info('acquired lock for Holder')
        await self.pool.open()
        instance = await self.instance.open()
        await self.instance.create_master_secret('secret')
        return instance

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            logger.error(exc_type, exc_value, traceback)

        await self.instance.close()
        await self.pool.close()
        logger.info('Holder releasing lock')
        lock.release()

