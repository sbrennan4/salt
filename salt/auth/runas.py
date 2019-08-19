# -*- coding: utf-8 -*-
'''
Provide authentication using simple LDAP binds

:depends:   - ldap Python module
'''

# Import python libs
from __future__ import absolute_import, print_function, unicode_literals
import logging

# Import salt libs
import salt.auth
from salt.exceptions import CommandExecutionError, SaltInvocationError

log = logging.getLogger(__name__)

def acl(username=None, eauth_opts=None):
    '''
    given load, assert that the given username is in eauth_runas_allowed, if so
    respect runas auth kwarg as replacement user to load
    IMPORTANT NOTE: this eauth lives within the token system built into salt,
    as such any token minted by it is cast as the runas user, and will not
    change. You must not use a cached token with runas and expect it to be
    recast as a different user.
    :return: None
    '''
    if not eauth_opts or not username:
        return None

    # we can assume if we are being executed via salt.auth.__get_acl we are
    # already authenticated, so we just need to assert that user is allowed
    # to proxy auth as someone/_anyone_ else
    eauth = __opts__.get('external_auth', {}).get('runas',{}).get(username, [])

    if '@runas' in eauth:
        log.debug('user %s granted for runas', username)

        loadauth = salt.auth.LoadAuth(__opts__)

        # fetch the proxied auth_list
        auth_list = loadauth.get_auth_list(eauth_opts)
        log.error(auth_list)
        return auth_list
    else:
        # if we've reached here the auth failed, return nothing
        log.debug('user %s not in runas external_auth approval list, passing', username)
        return None


def auth(username, password):
    '''
    ensure noone calls this directly
    '''
    log.error('You should be not using runas as an eauth provider directly')
    return False

def groups(username):
    ''' no-op '''
    return None

def process_acl(auth_list):
    ''' no-op '''
    return auth_list
