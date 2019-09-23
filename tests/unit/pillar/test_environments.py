# -*- coding: utf-8 -*-

# Import python libs
from __future__ import absolute_import, print_function, unicode_literals

# Import Salt Testing Libs
from tests.support.mixins import LoaderModuleMockMixin
from tests.support.unit import TestCase, skipIf
from tests.support.mock import NO_MOCK, NO_MOCK_REASON, MagicMock, patch

# Import file to test
import salt.pillar.environments as environments

# Bloomberg specific lib
import hostinfo

# Import 3rd-party libs
from salt.ext import six
from boltons.setutils import IndexedSet

class EnvironmentsTestCase(TestCase, LoaderModuleMockMixin):
    '''
    Test cases for salt.pillar.environments
    '''
    def setup_loader_modules(self):
        return {
            environments: {
                '__opts__': {
                    'evaporator': {
                        'tenancies': [
                            {
                                "name": "sltdm",
                                "groups": ["salt"],
                                "global": False,
                            },
                            {
                                "name": "ndis",
                                "groups": ["natm"],
                                "global": False,
                            },
                            {
                                "name": "salt-coffee",
                                "groups": ["coffee"],
                                "global": True,
                            },
                            {
                                "name": "salt-apple",
                                "groups": ["apple"],
                                "global": True,
                            },
                        ]
                    }
                }
            }
        }

    def test_tenancy_groups_set_one(self):
        node = hostinfo.host('sltdm-rr-129')
        groups = environments.tenancy_groups_set(node)
        self.assertEqual(groups, IndexedSet([u'sltdm']))

    def test_global_tenancy_groups_set(self):
        groups = environments.global_tenancy_groups_set()
        self.assertEqual(groups, IndexedSet([u'salt-coffee', u'salt-apple']))

    @skipIf(environments.HAS_HOSTINFO is False, 'hostinfo has to be installed')
    def test_resolve_node(self):
        mock_grain = {
            "bb": {
                "node-id": 123
            }
        }

        mock_return = "node_id works"
        with patch.object(environments, '__grains__', return_value=mock_grain):
            with patch('hostinfo.host', return_value=mock_return):
                res = environments.resolve_node(mock_return)
                self.assertEqual(res, mock_return)

    def test_ext_pillar_none(self):
        is_running_mock = MagicMock(return_value={'result': False})

        with patch.object(environments, 'resolve_node', MagicMock(return_value=None)):
            result = environments.ext_pillar('minion_id', {})
        self.assertEqual(result, {'environments': ['salt-coffee-nostage', 'salt-apple-nostage'], 'tenancies': ['salt-coffee', 'salt-apple']})

    # parameterize if/when salt switch to pytest runner
    def test_ext_pillar_hostinfo_groups_match_none(self):
        result = environments.ext_pillar('no-exist', {})
        self.assertEqual(result, {'environments': ['salt-coffee-nostage', 'salt-apple-nostage'], 'tenancies': ['salt-coffee', 'salt-apple']})

    def test_ext_pillar_hostinfo_groups_match_some(self):
        result = environments.ext_pillar('sltdm-rr-129', {})
        self.assertEqual(result, {'environments': ['salt-coffee-s2', 'salt-apple-s2', 'sltdm-s2'], 'tenancies': ['salt-coffee', 'salt-apple', 'sltdm']})
