import json
import os

import requests

from django.conf import settings

from .agent import Verifier

from . import eventloop, dev

import logging
logger = logging.getLogger(__name__)

TOB_BASE_URL = os.getenv('THE_ORG_BOOK_API_URL')


class ProofRequestManager():

    claim_def_json = None

    def __init__(self):
        proof_request_path = os.path.abspath(
            settings.BASE_DIR + '/proof_request.json')
        try:
            with open(proof_request_path, 'r') as proof_request_file:
                proof_request_json = proof_request_file.read()
        except FileNotFoundError as e:
            logger.error('Could not find proof_request.json. Exiting.')
            raise

        self.proof_request = json.loads(proof_request_json)

    def request_proof(self, filters):
        async def run(filters):

            # if os.getenv('PYTHON_ENV') == 'development':
            #     for attr in self.proof_request['requested_attrs']:
            #         for restriction in self.proof_request['requested_attrs'][attr]['restrictions']:
            #             restriction['schema_key']['version'] = dev.get_unique_version()

            async with Verifier() as verifier:
                response = requests.post(
                    TOB_BASE_URL + '/bcovrin/construct-proof',
                    json={
                        'filters': filters,
                        'proof_request': self.proof_request
                    }
                )

                if response.status_code == 406:
                    return {
                        'success': False,
                        'error': response.json()['detail']
                    }

                proof_response = response.json()
                proof = proof_response['proof']

                parsed_proof = {}
                for attr in proof['requested_proof']['revealed_attrs']:
                    parsed_proof[attr] = \
                        proof['requested_proof']['revealed_attrs'][attr][1]

                verified = await verifier.verify_proof(
                    self.proof_request,
                    proof
                )

                # Convert c_list array to string to remove crlf after each element
                s = json.dumps(proof['proof']['aggregated_proof']['c_list'])
                del proof['proof']['aggregated_proof']['c_list']
                proof['proof']['aggregated_proof']['c_list'] = s

                return {
                    'success': True,
                    'proof': proof,
                    'parsed_proof': parsed_proof,
                    'verified': verified
                }

        return eventloop.do(run(filters))
