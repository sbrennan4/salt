# -*- coding: utf-8 -*-

# Import python libs
from __future__ import absolute_import, print_function, unicode_literals
import pytest
import pdb

# Import Salt Testing Libs
from tests.support.mixins import LoaderModuleMockMixin
from tests.support.unit import TestCase
from tests.support.mock import MagicMock, patch

# Import file to test
import salt.executors.runas as runas

CMD_RUN_ALL_GOOD_RETURN = {
    "retcode": 0,
    "stdout": '{"local": {"return": "Good cmd return", "retcode": 0 }}'
}

CMD_RUN_ALL_BAD_RETURN = {
    "retcode": 2,
    "stderr": "BAD cmd return"
}

class RunasTestCase(TestCase, LoaderModuleMockMixin):
    '''
    Test cases for salt.exexcutors.runas
    '''

    def setup_loader_modules(self):
        return {
            runas: {
                '__context__': {},
                '__salt__': {},
            }
        }

    def test_virtual_name(self):
        ret = runas.__virtual__()
        self.assertEqual(ret, 'runas')

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
        my_mock_2 = MagicMock()
        with patch.object(my_mock_2, 'recv', side_effect=lambda: ['apple']):
            with patch.object(my_mock, 'Pipe', side_effect=lambda: [my_mock_2, MagicMock()]):
                with patch('salt.utils.platform.is_windows', return_value=False):
                    with patch('salt.utils.process', my_mock):
                        with patch('salt.utils.user.get_default_group', return_value='salt-junk'):
                            runas_obj = runas.execute(opts='', data={'executor_opts':{'username': 'junk', 'umask': '0200'}, 'fun': 'state.sls'}, func='', args='', kwargs={})
                            self.assertEqual(runas_obj, 'apple')

                            self.assertEqual(my_mock.MultiprocessingProcess.call_args_list[0][1]['args'][0], 'junk')

                            self.assertEqual(my_mock.MultiprocessingProcess.call_args_list[0][1]['args'][1], 'salt-junk')

                            self.assertEqual(my_mock.MultiprocessingProcess.call_args_list[0][1]['args'][-1]['concurrent'], True)

    def test_unix_with_group_input_exception(self):
        my_mock = MagicMock()
        my_mock_2 = MagicMock()
        with patch.object(my_mock_2, 'recv', side_effect=lambda: [KeyError(), 'BAD cmd']):
            with patch.object(my_mock, 'Pipe', side_effect=lambda: [my_mock_2, MagicMock()]):
                with patch('salt.utils.platform.is_windows', return_value=False):
                    with patch('salt.utils.process', my_mock):
                        with pytest.raises(KeyError):
                            runas_obj = runas.execute(opts='', data={'executor_opts':{'username': 'junk', 'group': 'salt-junk', 'umask': '0200'}, 'fun': 'state.sls'}, func='', args='', kwargs={})


    def test_windows_cmd_run_all_good(self):
        with patch('salt.utils.platform.is_windows', return_value=True):
            with patch.dict(runas.__salt__, {'cmd.run_all': MagicMock(return_value=CMD_RUN_ALL_GOOD_RETURN)}):
                runas_obj = runas.execute(opts={'config_dir': '/junk'}, data={'executor_opts':{'username': 'junk'}, 'fun': 'state.sls'}, func='', args='', kwargs={})
                self.assertEqual(runas_obj, 'Good cmd return')
                self.assertEqual(runas.__context__['retcode'], 0)

                command = ['salt-call', '--out', 'json', '--metadata', '-c', '/junk', '--', 'state.sls', 'concurrent=True']
                runas.__salt__['cmd.run_all'].assert_called_with(command, python_shell=False, runas='junk')

    def test_windows_cmd_run_all_bad(self):
        with patch('salt.utils.platform.is_windows', return_value=True):
            with patch.dict(runas.__salt__, {'cmd.run_all': MagicMock(return_value=CMD_RUN_ALL_BAD_RETURN)}):
                runas_obj = runas.execute(opts={'config_dir': '/junk'}, data={'executor_opts':{'username': 'junk'}, 'fun': 'state.sls'}, func='', args='', kwargs={})
                self.assertEqual(runas_obj, 'BAD cmd return')
                self.assertEqual(runas.__context__['retcode'], 2)
