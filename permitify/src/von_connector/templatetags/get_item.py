from django.template.defaulttags import register

import logging
logger = logging.getLogger(__name__)


@register.filter
def get_item(dictionary, key):
    if not type(dictionary) is type({}):
        return None
    return dictionary.get(key)
