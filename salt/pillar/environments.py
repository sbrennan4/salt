# -*- coding: utf-8 -*-
"""
Environments Pillar
=================

Introspection: to which environments does my minion belong?
Provides a pillar with the default name of `environments`
which contains a list of environments which match for a given minion.
This pillar doesnt just _emit_ which environments are associated with a
minion, it actually fully overrides the default behavior of evaluating
all top files of all environments to determine this, allowing you to support
many environments that define their own topfiles without collisions.

.. versionadded:: xxx

Command Line
------------

.. code-block:: bash

    salt-call pillar.get environment
    local:
        - foo
        - bar
        - baz

Configuring Environemnts Pillar
-----------------------------

.. code-block:: yaml

    ext_pillar:
      - environments:
          pillar_name: 'environments'

"""

# Import futures
from __future__ import absolute_import, print_function, unicode_literals

import pprint
import os.path
import logging
import os
import os.path
from datetime import datetime
import requests

# Import Salt libs
import salt.utils.json

# Import 3rd-party libs
from salt.ext import six
from boltons.setutils import IndexedSet

__version__ = '0.0.1'

try:
    import hostinfo

    HAS_HOSTINFO = True
except ImportError:
    HAS_HOSTINFO = False


log = logging.getLogger(__name__)


def __virtual__():
    return HAS_HOSTINFO


# Implement a partial subclass that fetches from sor on HostLookupFailure
# unclear if this is necessary, the only things needing to be mapped at
# provision time are global (salt-core, lifecycle)
if HAS_HOSTINFO:

    class SorFallbackCache(hostinfo.HostCache):
        def __get_by_name(self, name_or_alias):
            try:
                return super(SorFallbackCache, self).__get_by_name(
                    name_or_alias
                )
            except HostLookupFailure:
                # we must simulate a bbcpu.lst line for HostEntry
                # TODO implement
                # ret = __salt__['bb_sor.query'](name_or_alias, key='hostname')
                raise HostLookupFailure

        def __get_by_node(self, node):
            try:
                return super(SorFallbackCache, self).__get_by_name(
                    name_or_alias
                )
            except HostLookupFailure:
                # we must simulate a bbcpu.lst line for HostEntry
                # TODO implement
                raise HostLookupFailure

    # we want to attempt a sor lookup if a node is missing from flat files
    setattr(hostinfo, '__cache', SorFallbackCache())


def tenancy_groups_set():
    groups = IndexedSet()

    # assume config is a sane schema
    # scalar = tag, dict = 'tag' key is tag
    for tenancy in __opts__['evaporator']['tenancies']:
        if isinstance(tenancy, dict):
            groups.add(tenancy['environment'])
        else:
            groups.add(tenancy)

    return groups


def global_tenancy_groups_set():
    groups = IndexedSet()

    # assume config is a sane schema
    # scalar = tag, dict = 'tag' key is tag
    for tenancy in __opts__['evaporator']['tenancies']:
        if isinstance(tenancy, dict) and tenancy.get('global'):
            groups.add(tenancy['environment'])

    return groups


# first try node-id if it exists in grains, then try the minion_id
def resolve_node(minion_id):
    if __grains__.get('bb', {}).get('node-id'):
        node_id = __grains__['bb']['node-id']
        try:
            return hostinfo.host(node_id)
        except hostinfo.HostLookupError:
            log.debug('%s minion not found via node-id.', node_id)

    # if an exception was caught lets try with minion_id
    try:
        return hostinfo.host(minion_id)
    except hostinfo.HostLookupError:
        log.debug('%s minion not found via minion-id.', minion_id)

    # if we've gotten this far its an unknown node
    return None


# the goal here is to
# 1. if a local top for the given repo exists, include it
# 2. if not, include at minimum an empty dict/key so the node is considered in the environment
# all multitenancies are assumed to exist by /{base-path}/{name}-{stage}/ for SN2..S4
# file_roots mapping {name-stage} environment to the above roots exists
def ext_pillar(minion_id, pillar):
    """
    A salt external pillar which provides the list of nodegroups of which the minion is a member.

    :param minion_id: used for compound matching nodegroups
    :param pillar: provided by salt in some contexts, but not used by environments ext_pillar
    :param pillar_name: optional name to use for the pillar, defaults to 'environments'
    :return: a dictionary which is included by the salt master in the pillars returned to the minion
    """

    # hostinfo resolving a node that is None will throw an error
    # Instead lets just return empty array
    if not minion_id:
        return []

    node = resolve_node(minion_id)

    import pdb; pdb.set_trace()

    if node is None:
        return []

    # any matching tenancy_group is a 1 to 1 association with environment
    # we use an IndexedSet to ensure global roots are always highest priority
    environments = IndexedSet(global_tenancy_groups_set() | ( node.groups_set() & tenancy_groups_set()))

    return {'environments': list(environments)}
