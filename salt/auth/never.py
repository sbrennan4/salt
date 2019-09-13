# -*- coding: utf-8 -*-
'''
An "Always Disapproved" eauth interface, intended to stop you from authentication.
'''


def auth(username, password):  # pylint: disable=unused-argument
    '''
    Authenticate!
    '''
    return False
