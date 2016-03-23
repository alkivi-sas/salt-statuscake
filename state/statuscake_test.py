# -*- coding: utf-8 -*-
'''
Manage Statuscake tests


Create and delete Statuscake test

Statuscake credentials need to be in minion grains

.. code-block:: yaml
    statuscake:
      username: toto
      api_key: peWcBiMOS9HrZG15peWcBiMOS9HrZG15

.. code-block:: yaml

    Statuscake Web Test:
        statuscake_test.present:
          - WebsiteName: Toto
          - WebsiteURL: https://test.toto.com
          - Paused: 1
          - Port: 443
          - Timeout: 30
          - PingURL:
          - CheckRate:
          - BasicUser:
          - BasicPass:
          - Public:
          - LogoImage:
          - Branding:
          - WebsiteHost:
          - Virus:
          - FindString:
          - DoNotFind:
          - TestType:
          - ContactGroup:
          - RealBrowser:
          - TriggerRate:
          - TestTags:
          - StatusCodes:
'''

# Import Python libs
from __future__ import absolute_import
import logging

# Import salt libs
import salt.utils
from salt.exceptions import *

log = logging.getLogger(__name__)

def __virtual__():
    '''
    Only load if statuscake is available
    '''
    return 'statuscake_test' if 'statuscake.search_test' in __salt__ else False


def present(
        name,
        WebsiteName,
        WebsiteURL,
        CheckRate=60,
        TestType='HTTP',
        **kwargs):
    '''
    Ensure the webscenario is present with available steps

    name
        Name of the scenario

    host
        Statuscake host to add the scenario to

    agent 
        User Agent used for the test

    retries
        Retries to perform for the test

    update_interval
        Frequency for the test

    steps
        List of steps to add to the scenario

    '''
    ret = {'name': name, 'result': True, 'comment': '', 'changes': {}}

    test = __salt__['statuscake.search_test'](WebsiteName)

    if not test['res']:
        if __opts__['test']:
            ret['comment'] = 'Statuscake test {0} set to be added.'.format(WebsiteName)
            ret['result'] = None
            return ret

        added = __salt__['statuscake.add_test'](WebsiteName, WebsiteURL,
                CheckRate, TestType, **kwargs)

        if added['res']:
            ret['changes']['old'] = None
            ret['changes']['new'] = added['raw']['Data']
            ret['comment'] = 'Added test {0}.'.format(WebsiteName)
            return ret
        else:
            ret['result'] = False
            ret['comment'] = 'Failed to add test {0}.'.format(WebsiteName)
            ret['error'] = added['message']
            return ret
    else:
        tid = test['id']

        kwargs['TestID'] = tid

        if __opts__['test']:
            msg = 'Statuscake tests {0} set to be updated.'.format(WebsiteName)
            ret['comment'] = msg
            ret['result'] = None
            return ret

        ret['result'] = True
        ret['comment'] = 'Not updating because will cannot check data'
        return ret


def toto():
    if None:
        added = __salt__['boto_route53.add_record'](name, value, zone,
                                                    record_type, identifier,
                                                    ttl, region, key, keyid,
                                                    profile, wait_for_sync,
                                                    split_dns, private_zone)
        if added:
            ret['changes']['old'] = None
            ret['changes']['new'] = {'name': name,
                                     'value': value,
                                     'record_type': record_type,
                                     'ttl': ttl}
            ret['comment'] = 'Added {0} Route53 record.'.format(name)
        else:
            ret['result'] = False
            ret['comment'] = 'Failed to add {0} Route53 record.'.format(name)
            return ret
    elif record:
        need_to_update = False
        # Values can be a comma separated list and some values will end with a
        # period (even if we set it without one). To easily check this we need
        # to split and check with the period stripped from the input and what's
        # in route53.
        # TODO: figure out if this will cause us problems with some records.
        _values = [x.rstrip('.') for x in value.split(',')]
        _r_values = [x.rstrip('.') for x in record['value'].split(',')]
        _values.sort()
        _r_values.sort()
        if _values != _r_values:
            need_to_update = True
        if identifier and identifier != record['identifier']:
            need_to_update = True
        if ttl and str(ttl) != str(record['ttl']):
            need_to_update = True
        if need_to_update:
            if __opts__['test']:
                msg = 'Route53 record {0} set to be updated.'.format(name)
                ret['comment'] = msg
                ret['result'] = None
                return ret
            updated = __salt__['boto_route53.update_record'](name, value, zone,
                                                             record_type,
                                                             identifier, ttl,
                                                             region, key,
                                                             keyid, profile,
                                                             wait_for_sync,
                                                             split_dns,
                                                             private_zone)
            if updated:
                ret['changes']['old'] = record
                ret['changes']['new'] = {'name': name,
                                         'value': value,
                                         'record_type': record_type,
                                         'ttl': ttl}
                ret['comment'] = 'Updated {0} Route53 record.'.format(name)
            else:
                ret['result'] = False
                msg = 'Failed to update {0} Route53 record.'.format(name)
                ret['comment'] = msg
        else:
            ret['comment'] = '{0} exists.'.format(name)
    return ret


def absent(
        name,
        zone,
        record_type,
        identifier=None,
        region=None,
        key=None,
        keyid=None,
        profile=None,
        wait_for_sync=True,
        split_dns=False,
        private_zone=False):
    '''
    Ensure the Route53 record is deleted.

    name
        Name of the record.

    zone
        The zone to delete the record from.

    record_type
        The record type (A, NS, MX, TXT, etc.)

    identifier
        An identifier to match for deletion.

    region
        The region to connect to.

    key
        Secret key to be used.

    keyid
        Access key to be used.

    profile
        A dict with region, key and keyid, or a pillar key (string)
        that contains a dict with region, key and keyid.

    wait_for_sync
        Wait for an INSYNC change status from Route53.

    split_dns
        Route53 supports a public and private DNS zone with the same
        names.

    private_zone
        If using split_dns, specify if this is the private zone.
    '''
    ret = {'name': name, 'result': True, 'comment': '', 'changes': {}}

    record = __salt__['boto_route53.get_record'](name, zone, record_type,
                                                 False, region, key, keyid,
                                                 profile, split_dns,
                                                 private_zone)
    if record:
        if __opts__['test']:
            msg = 'Route53 record {0} set to be deleted.'.format(name)
            ret['comment'] = msg
            ret['result'] = None
            return ret
        deleted = __salt__['boto_route53.delete_record'](name, zone,
                                                         record_type,
                                                         identifier, False,
                                                         region, key, keyid,
                                                         profile,
                                                         wait_for_sync,
                                                         split_dns,
                                                         private_zone)
        if deleted:
            ret['changes']['old'] = record
            ret['changes']['new'] = None
            ret['comment'] = 'Deleted {0} Route53 record.'.format(name)
        else:
            ret['result'] = False
            msg = 'Failed to delete {0} Route53 record.'.format(name)
            ret['comment'] = msg
    else:
        ret['comment'] = '{0} does not exist.'.format(name)
    return ret
