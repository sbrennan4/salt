# -*- coding: utf-8 -*-
'''
Helpful decorators for module writing
'''

# Import python libs
from __future__ import absolute_import, print_function, unicode_literals
import functools
import logging
from boltons.funcutils import wraps

# Import salt libs
from salt.exceptions import CommandExecutionError, SaltConfigurationError, AuthorizationError
from salt.utils.ctx import RequestContext
from salt.log import LOG_LEVELS

# Import 3rd-party libs
from salt.ext import six

log = logging.getLogger(__name__)

class Authorize(object):
    '''
    This decorator will check if a given call is permitted based on the calling
    user and acl in place (if any).
    '''
    # we need to lazy-init ckminions via opts passed on from RequestContext, as
    # we don't have access to it here
    ckminions = None

    def __init__(self, tag, item):
        log.trace('Authorized decorator - tag %s applied', tag)
        self.tag = tag
        self.item = item

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
                # if an auth_check is present, enforce it
            if 'auth_check' not in RequestContext.current:
                log.trace('auth_check not in RequestContext. no-op')
                return f(*args, **kwargs)

            auth_check = RequestContext.current['auth_check']

            if not self.ckminions:
                # late import to avoid circular dependencies
                import salt.utils.minions
                self.ckminions = salt.utils.minions.CkMinions.factory(RequestContext.current['opts'])

            # only apply acl if it is listed in auth_list tag set
            if self.tag not in auth_check.get('tags', []):
                log.trace('loader tag %s not in auth_check tags enforcement list. noop', self.tag)
                return f(*args, **kwargs)

            # borrowed fromalt.utils.decorators.Depends
            if self.tag == 'runners':
                runner_check = self.ckminions.runner_check(
                    auth_check.get('auth_list', []),
                    self.item,
                    {'arg': args, 'kwargs': kwargs},
                )

                if not runner_check or isinstance(runner_check, dict) and 'error' in runner_check:
                    log.error("current auth_check profile: %s", auth_check)
                    raise AuthorizationError('User \'{0}\' is not permissioned to execute runner \'{1}\''.format(auth_check.get('username', 'UNKNOWN'), self.item))

                # if we've made it here, we are good. call the func
                return f(*args, **kwargs)

            if self.tag == 'module':
                if '__opts__' not in f.__globals__ or 'id' not in f.__globals__['__opts__']:
                    raise AuthorizationError('Error occurred - no __opts__ accessible from function.')

                opts = f.__globals__['__opts__']

                # minion loader covers two usecases:
                # 1) master side orchestrations, including salutil.cmd special-cases for salt.state/salt.function
                # 2) minion side re-enforcment of provided authlist
                # orchestration enforcement is equivalent to minion side enforcement, as we know minion being acted on
                # is strictly equivalent to opts['id']. for saltutil.cmd we do not duplicate the work done by the master,
                # if a user is authorized to run saltutil.cmd he/she must still meet the equivalent acl work being done
                # in done in salt.master.Master.publish to successfully publish to those minions

                minion_check = self.ckminions.auth_check(
                    auth_check.get('auth_list', []),
                    self.item,
                    [args, kwargs],
                    opts['id'],
                    'list',
                    minions=[opts['id']],
                    # always accept find_job
                    whitelist=['saltutil.find_job', 'saltutil.is_running', 'grains.get', 'config.get', 'config.option'],
                )
                if not minion_check or isinstance(minion_check, dict) and 'error' in minion_check:
                    # Authorization error occurred. Do not continue.
                    if auth_check == 'eauth' and not auth_list and 'username' in extra and 'eauth' in extra:
                        log.debug('Auth configuration for eauth "%s" and user "%s" is empty', extra['eauth'], extra['username'])
                    log.error("current auth_check profile: %s", auth_check)
                    raise AuthorizationError('User \'{0}\' is not permissioned to execute module function \'{1}\' on minion \'{2}\''.format(auth_check.get('username', 'UNKNOWN'), self.item, opts['id']))

                # if we've made it here, we are good. call the func
                return f(*args, **kwargs)

            # this invocation is the default for lazyloader tags that are unenforced, i.e. no-op
            return f(*args, **kwargs)

        return wrapper

authorize = Authorize
