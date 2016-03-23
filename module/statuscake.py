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
import json

# Import 3rd-party libs
# pylint: disable=import-error,no-name-in-module,redefined-builtin
from salt.ext.six.moves.urllib.parse import urljoin as _urljoin
from salt.ext.six.moves.urllib.parse import urlencode as _urlencode
from salt.ext.six.moves import range
import salt.ext.six.moves.http_client
# pylint: enable=import-error,no-name-in-module

log = logging.getLogger(__name__)

__virtualname__ = 'statuscake'

STATUSCAKE_PARAMS_DEFINITION = {
    'test': {
        'TestID': {'mandatory': False },
        'Paused': {'mandatory': False },
        'WebsiteName': {'mandatory': True },
        'WebsiteURL': {'mandatory': True },
        'Port': {'mandatory': False },
        'NodeLocations': {'mandatory': False },
        'Timeout': {'mandatory': False },
        'PingURL': {'mandatory': False },
        'Confirmation': {'mandatory': False },
        'CheckRate': {'mandatory': True, 'default': 300 },
        'BasicUser': {'mandatory': False },
        'BasicPass': {'mandatory': False },
        'Public': {'mandatory': False },
        'LogoImage': {'mandatory': False },
        'Branding': {'mandatory': False },
        'WebsiteHost': {'mandatory': False },
        'Virus': {'mandatory': False },
        'FindString': {'mandatory': False },
        'DoNotFind': {'mandatory': False },
        'TestType': {'mandatory': True, 'default': 'HTTP' },
        'ContactGroup': {'mandatory': False },
        'RealBrowser': {'mandatory': False },
        'TriggerRate': {'mandatory': False },
        'TestTags': {'mandatory': False },
        'StatusCodes': {'mandatory': False },
    },
}


def __virtual__():
    '''
    Return virtual name of the module.

    :return: The virtual name of the module.
    '''
    return __virtualname__

def build_args(obj, **kwargs):
    '''
    Helpers to build parameters
    According to STATUSCAKE_PARAMS_DEFINITION return formated args
    '''

    if obj not in STATUSCAKE_PARAMS_DEFINITION:
        raise Exception('%s not in STATUSCAKE_PARAMS_DEFINITION' % obj)

    args = {}
    for k, config in STATUSCAKE_PARAMS_DEFINITION[obj].items():
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

def _check_api_key(api_key):
    if not api_key:
        api_key = __salt__['config.get']('statuscake.api_key') or \
            __salt__['config.get']('statuscake:api_key')

        if not api_key:
            return {'res': False, 'message': 'No Statuscake api_key found'}

    return { 'res': True, 'data': api_key }

def _check_api_username(username):
    if not username:
        username = __salt__['config.get']('statuscake.username') or \
            __salt__['config.get']('statuscake:username')

        if not username:
            return {'res': False, 'message': 'No Statuscake username found'}

    return { 'res': True, 'data': username }

def _handle_get_result(result):
    ret = {'message': '', 'res': True}
    if result.get('status', None) == salt.ext.six.moves.http_client.OK:
        _result = result['dict']
        if 'ErrNo' in _result:
            ret['res'] = False
            ret['message'] = _result['Error']
        else:
            ret['data'] = _result
    return ret

def _handle_generic_result(result):
    ret = {'message': '', 'res': True}

    if result.get('status', None) == salt.ext.six.moves.http_client.OK:
        _result = result['dict']
        if not _result['Success']:
            ret['res'] = False
            ret['message'] = _result['Message']
        else:
            ret['message'] = _result['Message']
        ret['raw'] = _result
    elif result.get('status', None) == salt.ext.six.moves.http_client.NO_CONTENT:
        return True
    else:
        log.debug(url)
        log.debug(query_params)
        log.debug(data)
        log.debug(result)
        ret['res'] = False
    return ret


def _query(url,
           username=None,
           api_key=None,
           auth=False,
           args=None,
           header_dict=None,
           method='GET',
           ):
    '''
    Statuscake object method function to construct and execute on the API URL.

    :param username:    The Statuscake username.
    :param api_key:     The Statuscake api key.
    :param function:    The Statuscake api function to perform.
    :param method:      The HTTP method, e.g. GET or POST.
    :param data:        The data to be sent for POST method.
    :return:            The json response from the API call or False.
    '''

    if auth:
        test = _check_api_key(api_key)
        if not test['res']:
            return test
        api_key = test['data']

        test = _check_api_username(username)
        if not test['res']:
            return test
        username = test['data']

    if header_dict is None:
        header_dict = {}

    if method in ['POST', 'PUT']:
        header_dict['Content-Type'] = 'application/x-www-form-urlencoded'

    if auth:
        if 'API' not in header_dict:
            header_dict['API'] = api_key
        if 'Username' not in header_dict:
            header_dict['Username'] = username

    if args:
        args = _urlencode(args)

    result = salt.utils.http.query(
        url,
        method,
        data=args,
        decode=True,
        status=True,
        header_dict=header_dict,
        opts=__opts__,
    )

    if method == 'GET':
        return _handle_get_result(result)
    else:
        return _handle_generic_result(result)

def get_locations():
    '''
    API locations endpoint

    :return: dictionnary with res = True or False and message or error.

    CLI Example:

    .. code-block:: bash

        salt '*' statuscake.get_locations
    '''
    ret = {'message': '', 'res': True}

    url = 'https://www.statuscake.com/API/Locations/json'
    result = salt.utils.http.query(url,'GET', decode=True, status=True)
    if result.get('status', None) == salt.ext.six.moves.http_client.OK:
        _result = result['dict']
        ret['message'] = _result.values()
    else:
        ret['res'] = False

    return  ret


def add_test(WebsiteName, WebsiteURL, CheckRate=60, TestType='HTTP', api_key=None, api_username=None, **kwargs):
    '''
    Add a statuscake test

    :param WebsiteName: WebsiteName. MANDATORY
    :param WebsiteURL: WebsiteURL. MANDATORY
    :param CheckRate: CheckRate. MANDATORY default to 60
    :param TestType: TestType. MANDATORY default to HTTP
    :param api_key: Statuscacke API key.
    :param api_username: Statuscake API username.

    :return: dictionnary with res = True or False and message or error.
    '''

    if not kwargs:
        kwargs = {}

    kwargs['WebsiteName'] = WebsiteName
    kwargs['WebsiteURL'] = WebsiteURL
    kwargs['CheckRate'] = CheckRate
    kwargs['TestType'] = TestType

    test = build_args('test', **kwargs)
    if not test['res']:
        return test
    params = test['data']

    url = 'https://www.statuscake.com/API/Tests/Update'
    method = 'PUT'

    return _query(url=url, 
            method=method, username=api_username, 
            api_key=api_key, auth=True, args=params)

def get_all_tests(api_key=None, api_username=None):
    '''
    Fetch all tests minimum data
    Usefull for searching

    :param api_key: Statuscacke API key.
    :param api_username: Statuscake API username.

    :return: dictionnary with res = True or False and data or error.
    '''
    url = 'https://www.statuscake.com/API/Tests/'
    method = 'GET'

    return _query(url=url, 
            method=method, username=api_username, 
            api_key=api_key, auth=True)

def get_test(id, api_key=None, api_username=None):
    '''
    Fetch specific test data

    :param id: TestID. MANDATORY
    :param api_key: Statuscacke API key.
    :param api_username: Statuscake API username.

    :return: dictionnary with res = True or False and data or error.
    '''
    url = 'https://www.statuscake.com/API/Tests/Details?TestID={0}'.format(id)
    method = 'GET'

    return _query(url=url, 
            method=method, username=api_username, 
            api_key=api_key, auth=True)

def search_test(name, api_key=None, api_username=None):
    '''
    Search for a test with either name or url.

    :param name: WebsiteName. MANDATORY
    :param api_key: Statuscacke API key.
    :param api_username: Statuscake API username.

    :return: dictionnary with res = True or False and id or error.
    '''

    ret = {'message': '', 'res': True}
    if not name and not url:
        ret['res'] = False
        ret['message'] = 'You have to provide at least name or url parameters'
        return ret

    test = get_all_tests(api_key, api_username)
    if not test['res']:
        return test

    data = test['data']
    result = None

    for test in data:
        if test['WebsiteName'] != name:
            continue
        if result:
            ret['res'] = False
            ret['message'] = 'We have multiple test with this name : {0}'.format(name)
        else:
            result = test

    if not result:
        ret['res'] = False
        ret['message'] = 'No test found with this name : {0}'.format(name)
        return ret

    ret['id'] = result['TestID']
    return ret


def delete_test(id, api_key=None, api_username=None):
    '''
    Delete a statuscake test

    :param id: TestID. MANDATORY
    :param api_key: Statuscacke API key.
    :param api_username: Statuscake API username.

    :return: dictionnary with res = True or False and message or error.
    '''

    url = 'https://www.statuscake.com/API/Tests/Details/?TestID={0}'.format(id)
    method = 'DELETE'

    return _query(url=url, 
            method=method, username=api_username, 
            api_key=api_key, auth=True)
