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
        self.auth = auth.LoadAuth(opts)

    def test__process_acl(self):
        auth_list=['junk']
        pdb.set_trace()
        ret = auth.LoadAuth._LoadAuth__process_acl(self.auth, {}, auth_list)
        self.assertEqual(ret, auth_list)
