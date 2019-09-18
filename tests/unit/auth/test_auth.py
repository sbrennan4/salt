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
import salt.auth as auth

class LoadAuthTestCase(TestCase, LoaderModuleMockMixin):
    '''
    Test cases for salt.auth.__init__
    '''

    def setup_loader_modules(self):
        return {
            auth: {
                '__context__': {},
                '__salt__': {},
                '__opts__': {'extension_modules': ''},
            }
        }

    def setUp(self):
        opts = auth.__opts__
        self.opts = opts
        self.auth = auth.LoadAuth(opts)

    def test__process_acl_eauth_not_in_load(self):
        auth_list=['junk']
        # test when 'eauth' not in load
        ret = self.auth._LoadAuth__process_acl({}, auth_list)
        self.assertEqual(ret, auth_list)

    def test__process_acl_fstr_not_in_self_auth(self):
        auth_list=['abcde']
        # test fstr not in self.auth
        ret = self.auth._LoadAuth__process_acl({'eauth': 'junk'}, auth_list)
        self.assertEqual(ret, auth_list)

    def test__process_acl_eauth_is_ldap(self):
        auth_list=['dummy_junk']
        # test fstr not in self.auth
        ret_ldap_process_acl = self.auth.auth['ldap.process_acl'](auth_list, self.opts)
        ret = self.auth._LoadAuth__process_acl({'eauth': 'ldap'}, auth_list)
        self.assertEqual(ret, ret_ldap_process_acl)

    # def test__process_acl_exception(self):
        # auth_list=['aw12xdftqqq']
        # test self.auth[fstr] exception
        # pdb.set_trace()
        # with patch.object('auth.ldap.process_acl(auth_list, self.opts)', side_effect=lambda: [KeyError(), 'BAD cmd']):
            # with pytest.raises(KeyError):
                # ret = auth.LoadAuth._LoadAuth__process_acl(self.auth, {'eauth': 'junk'}, auth_list)
