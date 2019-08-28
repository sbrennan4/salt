# Import Salt Testing Libs
from tests.integration import AdaptedConfigurationTestCaseMixin
from tests.support.unit import TestCases

# Import generic test libs
from tests.support.mock import NO_MOCK, NO_MOCK_REASON, MagicMock, patch

# Import file to test
import salt.pillar.environments as environments

class EnvironmentsTestCase(TestCase, AdaptedConfigurationTestCaseMixin):
    def test_tenancy_groups_set(self):
        import pdb; pdb.set_trace()
        environments.tenancy_groups_set()