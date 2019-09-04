# -*- coding: utf-8 -*-

# Import python libs
from __future__ import absolute_import, print_function, unicode_literals
import pytest
import pdb

# Import Salt Testing Libs
from tests.support.mixins import LoaderModuleMockMixin
from tests.support.unit import TestCase, skipIf
from tests.support.mock import NO_MOCK, NO_MOCK_REASON, MagicMock, patch

# Import file to test
import salt.executors.runas as runas

# Import 3rd-party libs
from salt.ext import six
from boltons.setutils import IndexedSet

class RunasTestCase(TestCase):
    '''
    Test cases for salt.executors.runas
    '''
    def test_username_missing(self):
        with pytest.raises(ValueError, match=r'username must be specified in executor_opts'):
            runas.execute(opts='', data={}, func='', args='', kwargs={})

    def test_invalid_executor_opts_strategy(self):
        with pytest.raises(ValueError, match=r'Unrecognized value provided for strategy executor_opts'):
            runas.execute(opts='', data={'executor_opts':{'username': 'junk', 'strategy': 'salt-walk'}}, func='', args='', kwargs={})

    def test_windows_with_group_input(self):
       with patch('salt.utils.platform.is_windows', return_value=True):
           with pytest.raises(ValueError, match=r'group and umask are not supported on windows'):
               runas.execute(opts='', data={'executor_opts':{'username': 'junk', 'group': 'junk'}}, func='', args='', kwargs={})

           with pytest.raises(ValueError, match=r'group and umask are not supported on windows'):
               runas.execute(opts='', data={'executor_opts':{'username': 'junk', 'umask': '0200'}}, func='', args='', kwargs={})

    def test_unix_without_group_input(self):
        my_mock = MagicMock()
        with patch.object(my_mock, 'Pipe', side_effect=lambda: [MagicMock(),MagicMock()]):
            with patch('salt.utils.platform.is_windows', return_value=False):
                with patch('salt.utils.process', my_mock):
                    with patch('salt.utils.user.get_default_group', return_value='salt-junk'):
                        pdb.set_trace()
                        runas_obj = runas.execute(opts='', data={'executor_opts':{'username': 'salt', 'umask': '0200'}, 'fun': 'state.sls'}, func='', args='', kwargs={})
