"""
Helper functions for generating Concrete UUIDs
"""

# Force 'import uuid' to import the Python standard library module
# named "uuid", and not the "concrete.uuid" module
from __future__ import absolute_import

import uuid as python_uuid

from thrift.Thrift import TType
from concrete.uuid.ttypes import UUID
from concrete.metadata.ttypes import AnnotationMetadata
from concrete.util.mem_io import communication_deep_copy

from inspect import isroutine
import random
import logging


def generate_UUID():
    """Helper function for generating a Concrete UUID object
    """
    return UUID(uuidString=str(python_uuid.uuid4()))


def hex_to_bin(h):
    return int(h, 16)


def bin_to_hex(b, n=None):
    h = hex(b)[2:]
    if h.endswith('L'):
        h = h[:-1]
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
        return UUID(uuidString=join_uuid(
            self._xs, self._ys, bin_to_hex(self._z, self._z_len)
        ))


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


def _filtered_getmembers(obj):
    '''
    Generate key-value pairs of object members that may contain UUIDs.
    Over-generate, but filter the output enough that concrete objects
    can be traversed recursively using this function without leading to
    stack overflows or infinite loops.
    '''

    for k in dir(obj):
        if not (k[0] == '_' or k == 'thrift_spec' or k == 'read' or
                k == 'write' or k == 'validate'):
            v = getattr(obj, k)
            if not (isroutine(v) or
                    isinstance(v, int) or isinstance(v, float) or
                    isinstance(v, str) or isinstance(v, unicode)):
                yield (k, v)


_FILTERED_TTYPES = set((TType.STRUCT, TType.LIST, TType.MAP, TType.SET))


def _fast_filtered_getmembers(obj):
    'Fast thrift-specific implementation of filtered_getmembers.'

    if hasattr(obj, 'thrift_spec'):
        for s in obj.thrift_spec:
            if s is not None:
                t = s[1]
                if t in _FILTERED_TTYPES:
                    k = s[2]
                    yield (k, getattr(obj, k))


class UUIDClustering(object):
    '''
    Representation of the UUID instance clusters in a concrete
    communication (each cluster represents the set of nested members of
    the communication that reference or are identified by a given UUID).
    '''

    def __init__(self, comm):
        self._clusters = dict()  # map: UUID -> set of nested members
        self._search(comm)

    def hashable_clusters(self):
        '''
        Return the set of unlabeled UUID clusters in a unique and
        hashable format.  Two UUIDClusterings c1 and c2 are equivalent
        (the two underlying communications' UUID structures are
        equivalent) if and only if:

            c1.hashable_clusters() == c2.hashable_clusters()
        '''
        return set(tuple(sorted(c)) for c in self._clusters.values())

    def _search(self, obj, prefix=()):
        '''
        Search obj for UUIDs, calling _add_uuid_field when UUIDs are
        found and calling _search on other object members.
        When _search calls itself, prefix is appended with the object
        member name, forming a uniquely identifiable tuple
        representation of the path from the root object to a nested
        object member.
        '''

        if isinstance(obj, UUID):
            self._add_uuid_field(obj.uuidString, prefix)
        elif isinstance(obj, list):
            for (i, v) in enumerate(obj):
                self._search(v, prefix + (('list', i),))
        elif isinstance(obj, set):
            raise ValueError('UUIDClustering does not support sets')
        elif isinstance(obj, dict):
            for (k, v) in obj.items():
                self._search(v, prefix + (('dict', k),))
        else:
            for (k, v) in _filtered_getmembers(obj):
                self._search(v, prefix + (k,))

    def _add_uuid_field(self, u, f):
        '''
        Add UUID field f (a unique, hashable representation of the path
        from the root communication to a nested UUID object) to the UUID
        cluster indexed by UUID string u.
        '''
        if u in self._clusters:
            self._clusters[u].add(f)
        else:
            self._clusters[u] = set([f])


class UUIDCompressor(object):

    def __init__(self, single_analytic=False):
        self.single_analytic = single_analytic

    def compress(self, comm):
        'Return a deep copy of comm with compressed UUIDs.'

        cc = communication_deep_copy(comm)
        self.augf = AnalyticUUIDGeneratorFactory(cc)
        self.augs = dict()
        self.uuid_map = dict()

        self._compress_uuids(cc)
        self._compress_uuid_refs(cc)

        return cc

    def _compress_uuids(self, obj, name_is_uuid=False, tool=None):
        'Generate new UUIDs in "uuid" fields and save mapping'

        tool = self._get_tool(obj, tool)

        if name_is_uuid:
            if isinstance(obj, UUID):
                obj.uuidString = self._gen_uuid(obj, tool)
            else:
                logging.warning('uuid not instance of UUID')

        if not isinstance(obj, UUID):  # we already took care of "uuid"
            self._apply(
                lambda elt, elt_name_is_uuid: self._compress_uuids(
                    elt, name_is_uuid=elt_name_is_uuid, tool=tool
                ),
                obj
            )

    def _compress_uuid_refs(self, obj, name_is_uuid=False, tool=None):
        'Update UUID references (not in "uuid" fields) using saved mapping'

        tool = self._get_tool(obj, tool)

        if isinstance(obj, UUID):
            if not name_is_uuid:
                obj.uuidString = self.uuid_map[obj.uuidString]
        else:
            self._apply(
                lambda elt, elt_name_is_uuid: self._compress_uuid_refs(
                    elt, name_is_uuid=elt_name_is_uuid, tool=tool
                ),
                obj
            )

    def _get_tool(self, obj, tool=None):
        '''
        Return tool for this object, given the parent tool;
        update self.augs
        '''

        if hasattr(obj, 'metadata'):
            if isinstance(obj.metadata, AnnotationMetadata):
                tool = obj.metadata.tool
            else:
                logging.warning('metadata not instance of AnnotationMetadata')
        if self.single_analytic:
            tool = None
        if tool not in self.augs:
            self.augs[tool] = self.augf.create()
        return tool

    def _gen_uuid(self, old_uuid, tool):
        '''
        Return a new UUID for the provided tool, using self.augs;
        update self.uuid_map
        '''

        aug = self.augs[tool]
        new_uuid = aug.next()
        if old_uuid.uuidString in self.uuid_map:
            raise ValueError('encountered UUID %s twice, aborting' %
                             old_uuid.uuidString)
        self.uuid_map[old_uuid.uuidString] = new_uuid.uuidString
        return new_uuid.uuidString

    @classmethod
    def _apply(cls, f, x):
        '''
        Apply f to the members of x if it is a basic container type,
        otherwise apply f to x directly.
        '''

        if isinstance(x, list):
            for elt in x:
                f(elt, False)
        elif isinstance(x, set):
            for elt in x:
                f(elt, False)
        elif isinstance(x, dict):
            for elt in x.values():
                f(elt, False)
        else:
            for (k, v) in _fast_filtered_getmembers(x):
                f(v, k == 'uuid')


def compress_uuids(comm, verify=False, single_analytic=False):
    '''
    Create a copy of communication comm with UUIDs converted according
    to the compressible UUID scheme.  Return a 2-tuple containing that
    new communication and the UUIDCompressor object used to perform
    the conversion.

    If verify is True, use a heuristic to verify the UUID link structure
    is preserved in the new communication.  If single_analytic is True,
    use a single analytic prefix for all UUIDs in comm.

    If verify is True and comm has references added, throw a ValueError
    because verification would cause an infinite loop.
    '''

    if verify and hasattr(comm, 'tokenizationForUUID'):
        raise ValueError('cannot verify communication with references')

    uc = UUIDCompressor(single_analytic=single_analytic)

    new_comm = uc.compress(comm)

    num_old_uuids = len(set(uc.uuid_map.keys()))
    num_new_uuids = len(set(uc.uuid_map.values()))

    if verify:
        c1 = UUIDClustering(comm).hashable_clusters()
        c2 = UUIDClustering(new_comm).hashable_clusters()

        # Verification is c1 == c2;
        # also check UUID map lengths are the same as a sanity-check
        if num_old_uuids == num_new_uuids and c1 == c2:
            logging.info('verified %s (%d uuid instances, %d uuids)'
                         % (comm.id, sum(len(c) for c in c1), len(c1)))
        else:
            logging.error('%s failed verification' % comm.id)
            logging.error('uuid counts: %d -> %d'
                          % (num_old_uuids, num_new_uuids))
            logging.error('verified number of uuids: %d -> %d'
                          % (len(c1), len(c2)))
            logging.error('verified number of uuid instances: %d -> %d'
                          % (sum(map(len, c1)), sum(map(len, c2))))
            raise Exception('%s failed verification' % comm.id)

    else:
        if num_old_uuids != num_new_uuids:
            logging.warning('uuid counts are not the same (%d -> %d)'
                            % (num_old_uuids, num_new_uuids))

    return (new_comm, uc)
