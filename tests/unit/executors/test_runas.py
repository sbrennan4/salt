# -*- coding: utf-8 -*-

# Import python libs
from __future__ import absolute_import, print_function, unicode_literals

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
        with pytest.raises(ValueError):
            runas.get("username must be specified in executor_opts")
