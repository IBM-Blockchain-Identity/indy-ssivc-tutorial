import json

from django.template.defaulttags import register

import logging
logger = logging.getLogger(__name__)


@register.filter
def jsonify(dictionary):
    if not type(dictionary) is type({}):
        return None
    return json.dumps(dictionary, indent=2)
