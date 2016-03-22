# -*- coding: utf-8 -*-
'''
Module for sending value to statuscake

.. versionadded:: 2015.5.0

:configuration: This module can be used by either passing an api key and version
    directly or by specifying both in a configuration profile in the salt
    master/minion config.

    For example:

    .. code-block:: yaml

        statuscake:
          username: toto
          api_key: peWcBiMOS9HrZG15peWcBiMOS9HrZG15

'''

# Import Python libs
from __future__ import absolute_import
import logging

# Import 3rd-party libs
# pylint: disable=import-error,no-name-in-module,redefined-builtin
from salt.ext.six.moves.urllib.parse import urljoin as _urljoin
from salt.ext.six.moves.urllib.parse import urlencode as _urlencode
from salt.ext.six.moves import range
import salt.ext.six.moves.http_client
# pylint: enable=import-error,no-name-in-module

log = logging.getLogger(__name__)

__virtualname__ = 'statuscake'

CACHET_PARAMS_DEFINITION = {
    'components': {
        'add': {
            'name': {'mandatory': True },
            'status': {'mandatory': True },
            'description': {'mandatory': False, 'default': None },
            'link': {'mandatory': False, 'default': None },
            'order': {'mandatory': False, 'default': 0 },
            'group_id': {'mandatory': False, 'default': None },
            'enabled': {'mandatory': False, 'default': True },
        },
        'update': {
            'name': {'mandatory': False },
            'status': {'mandatory': False },
            'link': {'mandatory': False, 'default': None },
            'order': {'mandatory': False, 'default': None },
            'group_id': {'mandatory': False, 'default': None },
        },
    },
    'components.groups': {
        'add': {
            'name': {'mandatory': True },
            'order': {'mandatory': False, 'default': 0 },
        },
        'update': {
            'name': {'mandatory': False },
            'order': {'mandatory': False },
        },
    },
    'incidents': {
        'add': {
            'name': {'mandatory': True },
            'message': {'mandatory': True },
            'status': {'mandatory': True },
            'visible': {'mandatory': True, 'default': 1 },
            'component_id': {'mandatory': False, 'default': None },
            'component_status': {'mandatory': False, 'default': None },
            'notify': {'mandatory': False, 'default': False },
        },
        'update': {
            'name': {'mandatory': False },
            'message': {'mandatory': False },
            'status': {'mandatory': False },
            'visible': {'mandatory': False, 'default': 1 },
            'component_id': {'mandatory': False },
            'notify': {'mandatory': False },
        },
    },
    'metrics': {
        'add': {
            'name': {'mandatory': True },
            'suffix': {'mandatory': True },
            'description': {'mandatory': True },
            'default_value': {'mandatory': True, 'default': 0 },
            'display_chart': {'mandatory': False, 'default': 1 },
        },
    },
    'metrics.points': {
        'add': {
            'value': {'mandatory': True },
        },
    },
}


def __virtual__():
    '''
    Return virtual name of the module.

    :return: The virtual name of the module.
    '''
    return __virtualname__

def _build_args(obj, method, **kwargs):
    '''
    Helpers to build parameters
    According to CACHET_PARAMS_DEFINITION return formated args
    '''

    if obj not in CACHET_PARAMS_DEFINITION:
        raise Exception('%s not in CACHET_PARAMS_DEFINITION' % obj)

    if method not in CACHET_PARAMS_DEFINITION[obj]:
        raise Exception('%s not in CACHET_PARAMS_DEFINITION[%s]' % (method, obj))

    args = {}
    for k, config in CACHET_PARAMS_DEFINITION[obj][method].items():
        if config['mandatory']:
            if k not in kwargs:
                if 'default' in config:
                    args[k] = config['default']
                else:
                    return {'res': False, 'message': 'Mandatory params %s is missing' % k }
            else:
                args[k] = kwargs[k]
        elif k in kwargs:
            args[k] = kwargs[k]
        elif 'default' in config and config['default']:
            args[k] = config['default']

    return {'res': True, 'data': args }


def _query(function,
           username=None,
           api_key=None,
           auth=False,
           args=None,
           method='GET',
           header_dict=None,
           data=None,
           page=None):
    '''
    Statuscake object method function to construct and execute on the API URL.

    :param username:    The Statuscake username.
    :param api_key:     The Statuscake api key.
    :param function:    The Statuscake api function to perform.
    :param method:      The HTTP method, e.g. GET or POST.
    :param data:        The data to be sent for POST method.
    :return:            The json response from the API call or False.
    '''
    query_params = {}

    ret = {'message': '',
           'res': True}

    api_url = 'https://www.statuscake.com/'

    if auth:
        if not api_key:
            api_key = __salt__['config.get']('statuscake.api_key') or \
                __salt__['config.get']('statuscake:api_key')

            if not api_key:
                log.error('No Statuscake api key found.')
                ret['message'] = 'No Statuscake api key found.'
                ret['res'] = False
                return ret

        if not username:
            username = __salt__['config.get']('statuscake.username') or \
                __salt__['config.get']('statuscake:username')

            if not username:
                log.error('No Statuscake username found.')
                ret['message'] = 'No Statuscake username found.'
                ret['res'] = False
                return ret

    base_url = _urljoin(api_url, '/API/')
    url = _urljoin(base_url, function, False)

    if isinstance(args, dict):
        query_params = args

    if header_dict is None:
        header_dict = {}

    if auth:
        if 'API' not in header_dict:
            header_dict['API'] = api_key
        if 'Username' not in header_dict:
            header_dict['Username'] = username

    result = salt.utils.http.query(
        url,
        method,
        params=query_params,
        data=data,
        decode=True,
        status=True,
        header_dict=header_dict,
        opts=__opts__,
    )

    if result.get('status', None) == salt.ext.six.moves.http_client.OK:
        log.warning('test')
        log.warning(result)
        log.warning(url)
        _result = result['dict']
        if 'error' in _result:
            ret['message'] = _result['error']
            ret['res'] = False
            return ret
        ret['message'] = _result.get('data')
        return ret
    elif result.get('status', None) == salt.ext.six.moves.http_client.NO_CONTENT:
        return True
    else:
        log.debug(url)
        log.debug(query_params)
        log.debug(data)
        log.debug(result)
        if 'error' in result:
            ret['message'] = result['error']
            ret['res'] = False
            return ret
        ret['message'] = _result.get(response)
        return ret


def get_locations():
    '''
    API locations endpoint

    :return: dictionnary with res = True or False and message or error.

    CLI Example:

    .. code-block:: bash

        salt '*' statuscake.get_locations
    '''
    ret = {'message': '',
           'res': True}

    url = 'https://www.statuscake.com/API/Locations/json'
    result = salt.utils.http.query(url,'GET',decode=True,status=True)
    if result.get('status', None) == salt.ext.six.moves.http_client.OK:
        _result = result['dict']
        ret['message'] = _result.values()
    else:
        ret['res'] = False

    return  ret
