# Author: Danilo Piparo 2016
# Copyright CERN

"""Check the project url"""

import requests
import string
from urllib import parse

from tornado import web

def raise_error(emsg):
    raise web.HTTPError(500, reason = emsg)

def is_good_proj_name(proj_name):
    return proj_name.endswith('.git') or proj_name.endswith('.ipynb')

def check_url(url):

    url = parse.unquote(url)

    # Limit the sources
    is_good_server = url.startswith('https://gitlab.cern.ch') or \
                     url.startswith('https://github.com') or \
                     url.startswith('https://raw.githubusercontent.com')
    if not is_good_server:
        raise_error('The URL of the project is not a github or CERN gitlab URL')

    # Check if contains only good characters
    allowed = string.ascii_lowercase +\
              string.ascii_uppercase +\
              string.digits +\
              '/._+-'
    has_allowd_chars = set(url[len('https:'):]) <= set(allowed)
    if not has_allowd_chars:
        raise_error('The URL of the project is invalid.')

    # Limit the kind of project
    is_good_ext = is_good_proj_name(url)
    if not is_good_ext:
        raise_error('The project must be a notebook or a git repository.')

    # Avoid code injection: paranoia mode
    forbidden_seqs = ['&&', '|', ';', ' ', '..', '@']
    is_valid_url = any(i in url for i in forbidden_seqs)
    if not forbidden_seqs:
        raise_error('The URL of the project is invalid.')

    # Check it exists
    request = requests.get(url)
    sc = request.status_code
    if sc != 200:
        raise_error('The URL of the project does not exist or is not reachable (status code is %s)' %sc)

    return True
