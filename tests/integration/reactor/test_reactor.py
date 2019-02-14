# -*- coding: utf-8 -*-
'''

    integration.reactor.reactor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test Salt's reactor system
'''

# Import Python libs
from __future__ import absolute_import

# Import Salt testing libs
from tests.support.case import ModuleCase
from tests.support.helpers import flaky
from tests.support.mixins import SaltMinionEventAssertsMixin

# Import Salt libs
import salt.utils.event


class ReactorTest(ModuleCase, SaltMinionEventAssertsMixin):
    '''
    Test Salt's reactor system
    '''

    @flaky()
    def test_ping_reaction(self):
        '''
        Fire an event on the master and ensure
        that it pings the minion
        '''
        # Create event bus connection
        e = salt.utils.event.get_event('minion', sock_dir=self.minion_opts['sock_dir'], opts=self.minion_opts)

        e.fire_event({'a': 'b'}, '/test_event')

        self.assertMinionEventReceived({'a': 'b'}, queue_wait=5)

    @skipIf(salt.utils.platform.is_windows(), 'no sigalarm on windows')
    def test_reactor_reaction(self):
        '''
        Fire an event on the master and ensure
        The reactor event responds
        '''
        signal.signal(signal.SIGALRM, self.alarm_handler)
        signal.alarm(self.timeout)

        master_event = self.get_event()
        master_event.fire_event({'id': 'minion'}, 'salt/test/reactor')

        try:
            while True:
                event = master_event.get_event(full=True)

                if event is None:
                    continue

                if event.get('tag') == 'test_reaction':
                    self.assertTrue(event['data']['test_reaction'])
                    break
        finally:
            signal.alarm(0)

    @skipIf(salt.utils.platform.is_windows(), 'no sigalarm on windows')
    def test_reactor_is_leader(self):
        '''
        when leader is set to false reactor should timeout/not do anything
        '''
        # by default reactor should be leader
        ret = self.run_run_plus('reactor.is_leader')
        self.assertTrue(ret['return'])

        # make reactor not leader
        self.run_run_plus('reactor.set_leader', False)
        ret = self.run_run_plus('reactor.is_leader')
        self.assertFalse(ret['return'])

        signal.signal(signal.SIGALRM, self.alarm_handler)
        signal.alarm(self.timeout)

        try:
            master_event = self.get_event()
            self.fire_event({'id': 'minion'}, 'salt/test/reactor')

            while True:
                event = master_event.get_event(full=True)

                if event is None:
                    continue

                if event.get('tag') == 'test_reaction':
                    # if we reach this point, the test is a failure
                    self.assertTrue(False)  # pylint: disable=redundant-unittest-assert
                    break
        except TimeoutException as exc:
            self.assertTrue('Timeout' in str(exc))
        finally:
            signal.alarm(0)

        # make reactor leader again
        self.run_run_plus('reactor.set_leader', True)
        ret = self.run_run_plus('reactor.is_leader')
        self.assertTrue(ret['return'])

        # trigger a reaction
        signal.alarm(self.timeout)

        try:
            master_event = self.get_event()
            self.fire_event({'id': 'minion'}, 'salt/test/reactor')

            while True:
                event = master_event.get_event(full=True)

                if event is None:
                    continue

                if event.get('tag') == 'test_reaction':
                    self.assertTrue(event['data']['test_reaction'])
                    break
        finally:
            signal.alarm(0)
