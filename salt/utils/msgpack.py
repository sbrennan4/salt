# -*- coding: utf-8 -*-
'''
Functions to work with MessagePack
'''

from __future__ import absolute_import

# Import Python libs
try:
    # Attempt to import msgpack
    import msgpack
    from msgpack import PackValueError, UnpackValueError
except ImportError:
    # Fall back to msgpack_pure
    import msgpack_pure as msgpack  # pylint: disable=import-error


HAS_MSGPACK = False
try:
    # Attempt to import msgpack
    import msgpack
    # There is a serialization issue on ARM and potentially other platforms
    # for some msgpack bindings, check for it
    if msgpack.loads(msgpack.dumps([1, 2, 3]), use_list=True) is None:
        raise ImportError
    HAS_MSGPACK = True
except ImportError:
    # Fall back to msgpack_pure
    try:
        import msgpack_pure as msgpack  # pylint: disable=import-error
        HAS_MSGPACK = True
    except ImportError:
        # TODO: Come up with a sane way to get a configured logfile
        #       and write to the logfile when this error is hit also
        LOG_FORMAT = '[%(levelname)-8s] %(message)s'
        salt.log.setup_console_logger(log_format=LOG_FORMAT)
        log.fatal('Unable to import msgpack or msgpack_pure python modules')
        # Don't exit if msgpack is not available, this is to make local mode
        # work without msgpack
        #sys.exit(salt.defaults.exitcodes.EX_GENERIC)

version = msgpack.version

if HAS_MSGPACK and not hasattr(msgpack, 'exceptions'):
    class PackValueError(Exception):
        '''
        older versions of msgpack do not have PackValueError
        '''

    class UnpackValueError(Exception):
        '''
        older versions of msgpack do not have UnpackValueError
        '''

    class exceptions(object):
        '''
        older versions of msgpack do not have an exceptions module
        '''
        PackValueError = PackValueError()
        UnpackValueError = UnpackValueError()

    msgpack.exceptions = exceptions()
else:
    exceptions = msgpack.exceptions

# Import Salt libs
from salt.utils.thread_local_proxy import ThreadLocalProxy


def pack(o, stream, **kwargs):
    '''
    .. versionadded:: 2018.3.4

    Wraps msgpack.pack and ensures that the passed object is unwrapped if it is
    a proxy.

    By default, this function uses the msgpack module and falls back to
    msgpack_pure, if the msgpack is not available. You can pass an alternate
    msgpack module using the _msgpack_module argument.
    '''
    msgpack_module = kwargs.pop('_msgpack_module', msgpack)
    orig_enc_func = kwargs.pop('default', lambda x: x)

    def _enc_func(obj):
        obj = ThreadLocalProxy.unproxy(obj)
        return orig_enc_func(obj)

    return msgpack_module.pack(o, stream, default=_enc_func, **kwargs)


def packb(o, **kwargs):
    '''
    .. versionadded:: 2018.3.4

    Wraps msgpack.packb and ensures that the passed object is unwrapped if it
    is a proxy.

    By default, this function uses the msgpack module and falls back to
    msgpack_pure, if the msgpack is not available. You can pass an alternate
    msgpack module using the _msgpack_module argument.
    '''
    msgpack_module = kwargs.pop('_msgpack_module', msgpack)
    orig_enc_func = kwargs.pop('default', lambda x: x)

    def _enc_func(obj):
        obj = ThreadLocalProxy.unproxy(obj)
        return orig_enc_func(obj)

    return msgpack_module.packb(o, default=_enc_func, **kwargs)


def unpack(stream, **kwargs):
    '''
    .. versionadded:: 2018.3.4

    Wraps msgpack.unpack.

    By default, this function uses the msgpack module and falls back to
    msgpack_pure, if the msgpack is not available. You can pass an alternate
    msgpack module using the _msgpack_module argument.
    '''
    msgpack_module = kwargs.pop('_msgpack_module', msgpack)
    return msgpack_module.unpack(stream, **kwargs)


def unpackb(packed, **kwargs):
    '''
    .. versionadded:: 2018.3.4

    Wraps msgpack.unpack.

    By default, this function uses the msgpack module and falls back to
    msgpack_pure, if the msgpack is not available. You can pass an alternate
    msgpack module using the _msgpack_module argument.
    '''
    msgpack_module = kwargs.pop('_msgpack_module', msgpack)
    return msgpack_module.unpackb(packed, **kwargs)


# alias for compatibility to simplejson/marshal/pickle.
load = unpack
loads = unpackb

dump = pack
dumps = packb

Unpacker = msgpack.Unpacker
Packer = msgpack.Packer
