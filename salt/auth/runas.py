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
from salt.utils.ctx import RequestContext
from salt.exceptions import CommandExecutionError, SaltInvocationError

log = logging.getLogger(__name__)

def acl(eauth_opts=None, username=None):
    '''
    given euath_opts specifying another user to run privileges under, return that acl
    IMPORTANT NOTE: this eauth lives within the token system built into salt,
    as such any token minted by it is cast as the runas user, and will not
    change. You must not use a cached token with runas and expect it to be
    recast as a different user.
    :return: auth_list or None
    '''
    if not eauth_opts:
        return None

    if eauth_opts.get('eauth') == 'runas':
        log.error('runas: recursion detected.')
        return None

    loadauth = salt.auth.LoadAuth(__opts__)

    # fetch the proxied auth_list
    try:

        # persist these in the current context for other salt systems ito interact with
        RequestContext.current['eauth_opts'] = eauth_opts
        RequestContext.current['eauth'] = 'runas'

        auth_list = loadauth.get_auth_list(eauth_opts)

        auth_check = RequestContext.current.setdefault('auth_check', {})
        calling_user = username or auth_check.get('username', 'UNKNOWN')
        target_user = eauth_opts.get('username') + ':' + eauth_opts.get('eauth')

        log.info('runas: calling user: %s, target user: %s', calling_user, target_user)
        log.debug('runas: auth_list: %s', auth_list)
    except Exception as exc:
        log.error(exc)
        return None

    return auth_list

def auth(key=None, auth_type=None):
    '''
    acts as master aes key authentication for implicit calls
    '''
    auth_check = RequestContext.current.get('auth_check', {})
    # user_auth can be either from a nested call, or from the immediate call
    user_auth = auth_type == 'user' or auth_check.get('auth_type') == 'user'

    # case 1: cli based non eauth calls; will always have valid aes key
    master_key = salt.utils.master.get_master_key('root', __opts__)
    if user_auth and master_key == key:
        log.debug('runas: cli/non-eauth root user granted')
        return True

    # case 2: eauth codepath. When auth() is called, we can only return true
    # when there is _already_ an authorized auth_check in the current context
    try:
        username = auth_check['username']
        eauth = __opts__['external_auth']['runas'][username]

        if '@runas' in eauth:
            log.debug('runas.auth: user %s granted', username)
            return True
    except Exception:
        username = 'UNKNOWN'
        pass

    log.debug('user %s not in runas external_auth approval list, passing', username)
    return False
