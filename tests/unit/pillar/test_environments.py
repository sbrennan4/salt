# -*- coding: utf-8 -*-

# Import python libs
from __future__ import absolute_import, print_function, unicode_literals

# Import Salt Testing Libs
from tests.support.mixins import LoaderModuleMockMixin
from tests.support.unit import TestCase, skipIf, expectedFailure
from tests.support.mock import NO_MOCK, NO_MOCK_REASON, MagicMock, patch

# Import file to test
import salt.pillar.environments as environments

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
                                "environment": "salt-native"
                            },
                            "salt-core",
                            "salt-himalayan",
                            {
                                "environment": "salt-water",
                                "global": True
                            },
                            {
                                "environment": "salt-coffee",
                                "global": True
                            },
                            {
                                "environment": "salt-apple",
                                "global": False
                            },
                        ]
                    }
                }
            }
        }

    def test_tenancy_groups_set_dict(self):
        groups = environments.tenancy_groups_set()
        self.assertEqual(groups, IndexedSet([u'salt-native', u'salt-core', u'salt-himalayan', u'salt-water', u'salt-coffee', u'salt-apple']))

    def test_global_tenancy_groups_set(self):
        groups = environments.global_tenancy_groups_set()
        self.assertEqual(groups, IndexedSet([u'salt-water', u'salt-coffee']))

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
        self.assertEqual(result, [])

    # parameterize if/when salt switch to pytest runner
    def test_ext_pillar_hostinfo_groups_match_none(self):
        mock_node = MagicMock()
        mock_node.groups_set = lambda : {'pacld', 'bpkg'}

        with patch.object(environments, 'resolve_node', return_value=mock_node):
            result = environments.ext_pillar('minion_id', {})
        self.assertEqual(result, {u'environments': [u'salt-water', u'salt-coffee']})

    def test_ext_pillar_hostinfo_groups_match_some(self):
        mock_node = MagicMock()
        mock_groups_set = lambda : {'salt-apple', 'bpkg'}

        with patch.object(environments, 'resolve_node', return_value=mock_node):
            with patch.object(mock_node, 'groups_set', side_effect=mock_groups_set):
                result = environments.ext_pillar('minion_id', {})
        self.assertEqual(result, {u'environments': IndexedSet([u'salt-water', u'salt-coffee', u'salt-apple'])})
