"""
Helper functions for generating Concrete UUIDs
"""

# Force 'import uuid' to import the Python standard library module
# named "uuid", and not the "concrete.uuid" module
from __future__ import absolute_import

import uuid as python_uuid

import concrete

import random


def generate_UUID():
    """Helper function for generating a Concrete UUID object
    """
    c_uuid = concrete.UUID()
    c_uuid.uuidString = str(python_uuid.uuid4())
    return c_uuid


def hex_to_bin(h):
    return int(h, 16)


def bin_to_hex(b, n=None):
    h = hex(b)[2:]
    if n is None:
        n = len(h)
    elif len(h) > n:
        raise ValueError('hex string "%s" is longer than %d chars' % (h, n))
    return ('0' * (n - len(h))) + h


def split_uuid(u):
    p = u.split('-')

    valid_input = (
        len(p) == 5 and
        len(p[0]) == 8 and
        len(p[1]) == 4 and
        len(p[2]) == 4 and
        len(p[3]) == 4 and
        len(p[4]) == 12
    )
    if not valid_input:
        raise ValueError(
            'uuid "%s" is not of the form xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
            % u
        )

    xs = p[0] + p[1]
    ys = p[2] + p[3]
    zs = p[4]

    return (xs, ys, zs)


def join_uuid(xs, ys, zs):
    valid_input = (
        len(xs) == 12 and
        len(ys) == 8 and
        len(zs) == 12
    )
    if not valid_input:
        raise ValueError('uuid pieces do not have lengths 12, 8, 12')

    u = '-'.join((xs[:8], xs[8:], ys[:4], ys[4:], zs))

    return u


def generate_hex_unif(n):
    return ''.join(random.choice('abcdef0123456789') for i in xrange(n))


def generate_uuid_unif():
    return join_uuid(generate_hex_unif(12),
                     generate_hex_unif(8),
                     generate_hex_unif(12))


class _AnalyticUUIDGenerator(object):
    '''
    UUID generator for a given analytic in a given communication.
    '''

    def __init__(self, u):
        (self._xs, ys, zs) = split_uuid(u)
        self._ys = generate_hex_unif(len(ys))
        self._z = hex_to_bin(generate_hex_unif(len(zs)))
        self._z_len = len(zs)
        self._z_bound = 2**(4 * len(zs))
        self.n = 0

    def __iter__(self):
        return self

    def next(self):
        '''
        Generate and return a new concrete UUID.
        StopIteration will never be raised.
        '''
        self._z = (self._z + 1) % self._z_bound
        self.n += 1
        c_uuid = concrete.UUID()
        c_uuid.uuidString = join_uuid(
            self._xs, self._ys, bin_to_hex(self._z, self._z_len))
        return c_uuid


class AnalyticUUIDGeneratorFactory(object):
    '''
    Factory for a compressible UUID generator.

    One factory should be created per communication, and a new generator
    should be created from that factory for each analytic processing the
    communication.  Usually each program represents a single analytic,
    so common usage is

        augf = AnalyticUUIDGeneratorFactory(comm)
        aug = augf.create()
        for <each annotation object created by this analytic>:
            annotation. = aug.next()
            <add annotation to communication>

    or if you're creating a new communication

        augf = AnalyticUUIDGeneratorFactory()
        aug = augf.create()
        comm = <create communication>
        comm.uuid = aug.next()
        for <each annotation object created by this analytic>:
            annotation. = aug.next()
            <add annotation to communication>

    where the annotation objects might be objects of type
    Parse, DependencyParse, TokenTagging, CommunicationTagging, etc.
    '''

    def __init__(self, comm=None):
        if comm is None:
            self.comm_uuid = generate_uuid_unif()
        else:
            self.comm_uuid = comm.uuid.uuidString

    def create(self):
        '''
        Create and return a UUID generator for a new analytic.
        '''
        return _AnalyticUUIDGenerator(self.comm_uuid)
