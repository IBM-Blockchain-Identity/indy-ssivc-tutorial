import json
from importlib import import_module

from django.http import JsonResponse
from django.shortcuts import render

from django.http import Http404

from von_connector.config import Configurator
from von_connector.schema import SchemaManager
from von_connector.proof import ProofRequestManager

import logging
logger = logging.getLogger(__name__)

schema_manager = SchemaManager()
configurator = Configurator()

def admin(request ):
    print('\n\n\n\n\n\n')
    print(json.dumps(configurator.config))
    return render(request, 'admin.index.html', {})
#configurator.config['temp_root_admin']

# get pending requests from redis

# render page

# render(request, admin.html, { 'pending_requests': [ *requests from redis* ] })

# 2. /process_request controller

# continue submit claim...



def index(request):

    # If this is the form for the foundational claim,
    # we have no prequisites so just render.
    if 'foundational' in configurator.config and \
            configurator.config['foundational']:
        return render(
            request,
            configurator.config['template_root'],
            configurator.config
        )

    legal_entity_id = request.GET.get('org_id', None)

    # If id isn't passed in, we render a form to ask for it.
    #if not legal_entity_id:
    #    return render(request, 'missing_id.html')

    logger.info('----\n\n\n\n\n\n{}\n\n\n\n\n'.format(legal_entity_id))

    proof_request_manager = ProofRequestManager()
    proof_response = proof_request_manager.request_proof({
        'legal_entity_id': legal_entity_id
    })

    logger.info('----\n\n\n\n\n\n{}\n\n\n\n\n'.format(proof_response))

    logger.info(legal_entity_id)

    configurator.config['proof_response'] = proof_response

    return render(
        request,
        configurator.config['template_root'],
        configurator.config
    )


def submit_claim(request):
    # Get json request body
    body = json.loads(request.body.decode('utf-8'))

    # Get the schema we care about by 'schema'
    # passed in request
    try:
        schema = next(
            schema for
            schema in
            schema_manager.schemas if
            schema['name'] == body['schema'])
    except StopIteration:
        raise Exception(
            'Schema type "%s" in request did not match any schemas.' %
            body['schema'])




    # if address = 123 fake st:
        # key = current time
        # value = body

        # save in redis
        
        # return 'message'



    # Build schema body skeleton
    claim = {}
    for attr in schema['attr_names']:
        claim[attr] = None

    # Get the schema mapper we care about
    try:
        schema_mapper = next(
            schema_mapper for
            schema_mapper in
            configurator.config['schema_mappers'] if
            schema_mapper['for'] == body['schema'])
    except StopIteration:
        raise Exception(
            'Schema type "%s" in request did not match any schema mappers.' %
            body['schema'])

    # Build claim data from schema mapper
    for attribute in schema_mapper['attributes']:
        # Handle getting value from request data
        if attribute['from'] == 'request':
            claim[attribute['name']] = body[attribute['source']]
        # Handle getting value from helpers (function defined in config)
        elif attribute['from'] == 'helper':
            try:
                helpers = import_module('von_connector.helpers')
                helper = getattr(helpers, attribute['source'])
                claim[attribute['name']] = helper()
            except AttributeError:
                raise Exception(
                    'Cannot find helper "%s"' % attribute['source'])
        # Handle setting value with string literal or None
        elif attribute['from'] == 'literal':
            try:
                value = attribute['source']
            except KeyError:
                value = None

            claim[attribute['name']] = value
        # Handle getting value already set on schema skeleton
        elif attribute['from'] == 'previous':
            try:
                claim[attribute['name']] = \
                    claim[attribute['source']]
            except KeyError:
                raise Exception(
                    'Cannot find previous value "%s"' % attribute['source'])
        else:
            raise Exception('Unkown mapper type "%s"' % attribute['from'])

    claim = schema_manager.submit_claim(schema, claim)

    return JsonResponse({'success': True, 'result': claim})


def verify_dba(request):
    # Get json request body
    body = json.loads(request.body.decode('utf-8'))
    if 'legal_entity_id' not in body or 'doing_business_as_name' not in body:
        raise Exception('Missing required input')
    (verified, message) = schema_manager.verify_dba(body)

    return JsonResponse({'success': verified, 'message': message})
