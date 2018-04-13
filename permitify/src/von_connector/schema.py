import json
import os

import requests

from django.conf import settings

from .agent import Issuer
from .agent import convert_seed_to_did
from von_agent.util import encode
from von_agent.schema import schema_key_for

from . import eventloop, dev

import logging
logger = logging.getLogger(__name__)

# TODO: resolve url via DID -> endpoint
TOB_BASE_URL = os.getenv('THE_ORG_BOOK_API_URL')
TOB_INDY_SEED = os.getenv('TOB_INDY_SEED')

def claim_value_pair(plain):
    return [str(plain), encode(plain)]


class SchemaManager():

    claim_def_json = None

    def __init__(self):
        schemas_path = os.path.abspath(settings.BASE_DIR + '/schemas.json')
        try:
            with open(schemas_path, 'r') as schemas_file:
                schemas_json = schemas_file.read()
        except FileNotFoundError as e:
            logger.error('Could not find schemas.json. Exiting.')
            raise
        self.schemas = json.loads(schemas_json)

        self.__log_json('Schema start', self.schemas)

        # if os.getenv('PYTHON_ENV') == 'development':
        #     for schema in self.schemas:
        #         schema['version'] = dev.get_unique_version()

    def __log_json(self, heading, data):
        logger.debug(
            "\n============================================================================\n" +
            "{0}\n".format(heading) +
            "----------------------------------------------------------------------------\n" +
            "{0}\n".format(json.dumps(data, indent=2)) +
            "============================================================================\n")
        return

    def __log(self, heading, data):
        logger.debug(
            "\n============================================================================\n" +
            "{0}\n".format(heading) +
            "----------------------------------------------------------------------------\n" +
            "{0}\n".format(data) +
            "============================================================================\n")
        return

    def publish_schema(self, schema):
        async def run(schema):
            async with Issuer() as issuer:
                # Check if schema exists on ledger
                schema_json = await issuer.get_schema(
                    schema_key_for(
                        {
                            'origin_did': issuer.did,
                            'name': schema['name'],
                            'version': schema['version']
                        }
                    )
                )

                # If not, send the schema to the ledger, then get result
                if not json.loads(schema_json):
                    schema_json = await issuer.send_schema(json.dumps(schema))
                
                schema = json.loads(schema_json)

                self.__log_json('schema:', schema)

                # Check if claim definition has been published.
                # If not then publish.
                claim_def_json = await issuer.get_claim_def(
                    schema['seqNo'], issuer.did)
                if not json.loads(claim_def_json):
                    claim_def_json = await issuer.send_claim_def(schema_json)

                claim_def = json.loads(claim_def_json)
                self.__log_json('claim_def:', claim_def)



        return eventloop.do(run(schema))

    def submit_claim(self, schema, claim):
        async def run(schema, claim):
            async with Issuer() as issuer:
                for key, value in claim.items():
                    claim[key] = claim_value_pair(value) if value else \
                        claim_value_pair("")

                self.__log_json('Claim:', claim)
                self.__log_json('Schema:', schema)

                # We need schema from ledger
                schema_json = await issuer.get_schema(
                    schema_key_for(
                        {
                            'origin_did': issuer.did,
                            'name': schema['name'],
                            'version': schema['version']
                        }
                    )
                )
                schema = json.loads(schema_json)

                self.__log_json('Schema:', schema)

                claim_def_json = await issuer.get_claim_def(
                    schema['seqNo'], issuer.did)
                claim_def = json.loads(claim_def_json)

                self.__log_json('Schema:', schema)

                tob_did = await convert_seed_to_did(TOB_INDY_SEED)
                self.__log('TheOrgBook DID:', tob_did)

                # We create a claim offer
                claim_offer_json = await issuer.create_claim_offer(schema_json, tob_did)
                claim_offer = json.loads(claim_offer_json)

                self.__log_json('Claim Offer:', claim_offer)

                self.__log_json('Requesting Claim Request:', 
                    {
                        'claim_offer': claim_offer,
                        'claim_def': claim_def
                    })

                response = requests.post(
                    TOB_BASE_URL + '/bcovrin/generate-claim-request',
                    json={
                        'claim_offer': claim_offer_json,
                        'claim_def': claim_def_json
                    }
                )

                # Build claim
                claim_request = response.json()

                claim_request_json = json.dumps(claim_request)
                self.__log_json('Claim Request Json:', claim_request)

                (_, claim_json) = await issuer.create_claim(
                    claim_request_json, claim)

                self.__log_json('Claim Json:', json.loads(claim_json))

                # Send claim
                response = requests.post(
                    TOB_BASE_URL + '/bcovrin/store-claim',
                    json={
                        'claim_type': schema['data']['name'],
                        'claim_data': json.loads(claim_json)
                    }
                )

                return response.json()

        return eventloop.do(run(schema, claim))
