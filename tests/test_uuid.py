from concrete.util.concrete_uuid import (
    generate_UUID, bin_to_hex, hex_to_bin, AnalyticUUIDGeneratorFactory,
    generate_uuid_unif, generate_hex_unif, split_uuid, join_uuid,
)

from concrete import AnnotationMetadata, Communication
from concrete.validate import validate_communication

import re
import time
import unittest

UUID_RE = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')


class TestUUID(unittest.TestCase):

    def test_next(self):
        comm = Communication()
        comm.uuid = generate_UUID()

    def test_minimal_communication_with_uuid(self):
        comm = Communication()
        comm.id = "myID"
        comm.metadata = AnnotationMetadata(
            tool="TEST", timestamp=int(time.time()))
        comm.type = "Test Communication"
        comm.uuid = generate_UUID()
        self.assertTrue(validate_communication(comm))


class TestHexToBin(unittest.TestCase):

    def test_hex_to_bin(self):
        self.assertEqual(hex_to_bin('0'), 0)
        self.assertEqual(hex_to_bin('1'), 1)
        self.assertEqual(hex_to_bin('2'), 2)
        self.assertEqual(hex_to_bin('3'), 3)
        self.assertEqual(hex_to_bin('4'), 4)
        self.assertEqual(hex_to_bin('5'), 5)
        self.assertEqual(hex_to_bin('6'), 6)
        self.assertEqual(hex_to_bin('7'), 7)
        self.assertEqual(hex_to_bin('8'), 8)
        self.assertEqual(hex_to_bin('9'), 9)
        self.assertEqual(hex_to_bin('a'), 10)
        self.assertEqual(hex_to_bin('A'), 10)
        self.assertEqual(hex_to_bin('b'), 11)
        self.assertEqual(hex_to_bin('B'), 11)
        self.assertEqual(hex_to_bin('c'), 12)
        self.assertEqual(hex_to_bin('C'), 12)
        self.assertEqual(hex_to_bin('d'), 13)
        self.assertEqual(hex_to_bin('D'), 13)
        self.assertEqual(hex_to_bin('e'), 14)
        self.assertEqual(hex_to_bin('E'), 14)
        self.assertEqual(hex_to_bin('f'), 15)
        self.assertEqual(hex_to_bin('F'), 15)
        self.assertEqual(hex_to_bin('caf'), 15 + 10 * 16 + 12 * 256)
        self.assertEqual(hex_to_bin('cafe3'), 3 + 14 * 16 +
                         15 * 256 + 10 * 4096 + 12 * 65536)


class TestBinToHex(unittest.TestCase):

    def test_bin_to_hex(self):
        self.assertEqual(bin_to_hex(0), '0')
        self.assertEqual(bin_to_hex(1), '1')
        self.assertEqual(bin_to_hex(2), '2')
        self.assertEqual(bin_to_hex(3), '3')
        self.assertEqual(bin_to_hex(4), '4')
        self.assertEqual(bin_to_hex(5), '5')
        self.assertEqual(bin_to_hex(6), '6')
        self.assertEqual(bin_to_hex(7), '7')
        self.assertEqual(bin_to_hex(8), '8')
        self.assertEqual(bin_to_hex(9), '9')
        self.assertEqual(bin_to_hex(10).lower(), 'a')
        self.assertEqual(bin_to_hex(11).lower(), 'b')
        self.assertEqual(bin_to_hex(12).lower(), 'c')
        self.assertEqual(bin_to_hex(13).lower(), 'd')
        self.assertEqual(bin_to_hex(14).lower(), 'e')
        self.assertEqual(bin_to_hex(15).lower(), 'f')
        self.assertEqual(bin_to_hex(15 + 10 * 16 + 12 * 256).lower(), 'caf')
        self.assertEqual(bin_to_hex(3 + 14 * 16 + 15 * 256 +
                                    10 * 4096 + 12 * 65536).lower(), 'cafe3')

    def test_bin_to_hex_with_len(self):
        self.assertEqual(bin_to_hex(0, 4), '0000')
        self.assertEqual(bin_to_hex(1, 4), '0001')
        self.assertEqual(bin_to_hex(2, 4), '0002')
        self.assertEqual(bin_to_hex(3, 4), '0003')
        self.assertEqual(bin_to_hex(4, 4), '0004')
        self.assertEqual(bin_to_hex(5, 4), '0005')
        self.assertEqual(bin_to_hex(6, 4), '0006')
        self.assertEqual(bin_to_hex(7, 4), '0007')
        self.assertEqual(bin_to_hex(8, 4), '0008')
        self.assertEqual(bin_to_hex(9, 4), '0009')
        self.assertEqual(bin_to_hex(10, 4).lower(), '000a')
        self.assertEqual(bin_to_hex(11, 4).lower(), '000b')
        self.assertEqual(bin_to_hex(12, 4).lower(), '000c')
        self.assertEqual(bin_to_hex(13, 4).lower(), '000d')
        self.assertEqual(bin_to_hex(14, 4).lower(), '000e')
        self.assertEqual(bin_to_hex(15, 4).lower(), '000f')
        self.assertEqual(bin_to_hex(
            15 + 10 * 16 + 12 * 256, 4).lower(), '0caf')
        with self.assertRaises(ValueError):
            bin_to_hex(3 + 14 * 16 + 15 * 256 + 10 * 4096 + 12 * 65536, 4)


class TestSplitUUID(unittest.TestCase):

    def test_split_uuid_valid(self):
        self.assertEqual(
            split_uuid('7575a428-aaf7-4c2e-929e-1e2a0ab59e16'),
            ('7575a428aaf7', '4c2e929e', '1e2a0ab59e16')
        )

    def test_split_uuid_too_many_pieces(self):
        with self.assertRaises(ValueError):
            split_uuid('aaf7-7575a428-aaf7-4c2e-929e-1e2a0ab59e16')

    def test_split_uuid_too_few_pieces(self):
        with self.assertRaises(ValueError):
            split_uuid('7575a428-4c2e-929e-1e2a0ab59e16')

    def test_split_uuid_first_piece_too_long(self):
        with self.assertRaises(ValueError):
            split_uuid('7575a428a-aaf7-4c2e-929e-1e2a0ab59e16')

    def test_split_uuid_second_piece_too_long(self):
        with self.assertRaises(ValueError):
            split_uuid('7575a428-aaf7a-4c2e-929e-1e2a0ab59e16')

    def test_split_uuid_third_piece_too_long(self):
        with self.assertRaises(ValueError):
            split_uuid('7575a428-aaf7-4c2ea-929e-1e2a0ab59e16')

    def test_split_uuid_fourth_piece_too_long(self):
        with self.assertRaises(ValueError):
            split_uuid('7575a428-aaf7-4c2e-929ea-1e2a0ab59e16')

    def test_split_uuid_fifth_piece_too_long(self):
        with self.assertRaises(ValueError):
            split_uuid('7575a428-aaf7-4c2e-929e-1e2a0ab59e16a')

    def test_split_uuid_first_piece_too_short(self):
        with self.assertRaises(ValueError):
            split_uuid('7575a42-aaf7-4c2e-929e-1e2a0ab59e16')

    def test_split_uuid_second_piece_too_short(self):
        with self.assertRaises(ValueError):
            split_uuid('7575a428-aaf-4c2e-929e-1e2a0ab59e16')

    def test_split_uuid_third_piece_too_short(self):
        with self.assertRaises(ValueError):
            split_uuid('7575a428-aaf7-4c2-929e-1e2a0ab59e16')

    def test_split_uuid_fourth_piece_too_short(self):
        with self.assertRaises(ValueError):
            split_uuid('7575a428-aaf7-4c2e-929-1e2a0ab59e16')

    def test_split_uuid_fifth_piece_too_short(self):
        with self.assertRaises(ValueError):
            split_uuid('7575a428-aaf7-4c2e-929e-1e2a0ab59e1')


class TestJoinUUID(unittest.TestCase):

    def test_join_uuid_valid(self):
        self.assertEquals(
            join_uuid('7575a428aaf7', '4c2e929e', '1e2a0ab59e16'),
            '7575a428-aaf7-4c2e-929e-1e2a0ab59e16'
        )

    def test_join_uuid_first_piece_too_long(self):
        with self.assertRaises(ValueError):
            join_uuid('7575a428aaf7a', '4c2e929e', '1e2a0ab59e16')

    def test_join_uuid_second_piece_too_long(self):
        with self.assertRaises(ValueError):
            join_uuid('7575a428aaf7', '4c2e929ea', '1e2a0ab59e16')

    def test_join_uuid_third_piece_too_long(self):
        with self.assertRaises(ValueError):
            join_uuid('7575a428aaf7', '4c2e929e', '1e2a0ab59e16a')

    def test_join_uuid_first_piece_too_short(self):
        with self.assertRaises(ValueError):
            join_uuid('7575a428aaf', '4c2e929e', '1e2a0ab59e16')

    def test_join_uuid_second_piece_too_short(self):
        with self.assertRaises(ValueError):
            join_uuid('7575a428aaf7', '4c2e929', '1e2a0ab59e16')

    def test_join_uuid_third_piece_too_short(self):
        with self.assertRaises(ValueError):
            join_uuid('7575a428aaf7', '4c2e929e', '1e2a0ab59e1')


class TestGenerateHex(unittest.TestCase):

    def test_generate_hex_unif_range(self):
        n = 1000  # (1 - 1/16)^n = 9e-29
        r = set()
        for i in xrange(n):
            r.add(generate_hex_unif(1))
        self.assertEquals(
            sorted(map(lambda x: str(x).lower(), r)),
            [c for c in '0123456789abcdef']
        )

    def test_generate_hex_unif_len(self):
        h = generate_hex_unif(21)  # (1/16)^(n-1) = 8e-25
        self.assertEquals(len(h), 21)
        self.assertTrue(len(set(c for c in h)) > 1)

    def test_generate_hex_unif_spread(self):
        n = 1000
        m = 32
        # union bound: (1/16)^m * n^2 = 3e-33
        s = set([generate_hex_unif(m) for i in xrange(n)])
        self.assertEquals(len(s), n)


class TestGenerateUUID(unittest.TestCase):

    def test_generate_uuid_unif_format(self):
        u = generate_uuid_unif()
        assert UUID_RE.match(u) is not None

    def test_generate_uuid_unif_spread(self):
        n = 1000
        # union bound: (1/16)^32 * n^2 = 3e-33
        s = set([generate_uuid_unif() for i in xrange(n)])
        self.assertEquals(len(s), n)


class Duck(object):
    pass


class TestAnalyticUUIDGeneratorFactory(unittest.TestCase):

    def test_x_prefix_no_comm(self):
        n = 1000
        augf = AnalyticUUIDGeneratorFactory()
        u = augf.comm_uuid
        for i in xrange(n):
            aug = augf.create()
            self.assertTrue(aug.next().uuidString.startswith(u[:8 + 1 + 4]))

    def test_x_prefix_with_comm(self):
        n = 1000
        u = '7575a428-aaf7-4c2e-929e-1e2a0ab59e16'
        comm = Duck()
        comm.uuid = Duck()
        comm.uuid.uuidString = u
        augf = AnalyticUUIDGeneratorFactory(comm)
        self.assertEquals(augf.comm_uuid, u)
        for i in xrange(n):
            aug = augf.create()
            self.assertTrue(aug.next().uuidString.startswith(u[:8 + 1 + 4]))

    def test_x_prefix_bad_comm_uuid(self):
        u = '7575a428a-aaf7-4c2e-929e-1e2a0ab59e16'
        comm = Duck()
        comm.uuid = Duck()
        comm.uuid.uuidString = u
        augf = AnalyticUUIDGeneratorFactory(comm)
        with self.assertRaises(ValueError):
            augf.create()

    def test_y_prefix(self):
        m = 100
        n = 100
        augf = AnalyticUUIDGeneratorFactory()
        for i in xrange(m):
            aug = augf.create()
            uu = aug.next().uuidString
            for j in xrange(n - 1):
                self.assertTrue(aug.next().uuidString.startswith(
                    uu[:8 + 1 + 4 + 1 + 4 + 1 + 4]))

    def test_z_increment(self):
        m = 100
        n = 100
        augf = AnalyticUUIDGeneratorFactory()
        for i in xrange(m):
            aug = augf.create()
            u = aug.next().uuidString
            z = int(u[8 + 1 + 4 + 1 + 4 + 1 + 4 + 1:], 16)
            for j in xrange(n - 1):
                u = aug.next().uuidString
                self.assertEquals(
                    int(u[8 + 1 + 4 + 1 + 4 + 1 + 4 + 1:], 16),
                    (z + 1) % 2**48
                )
                z = (z + 1) % 2**48

    def test_x_prefix_spread(self):
        m = 100
        # union bound: (1/16)^12 * m^2 = 4e-11
        s = set()
        for i in xrange(m):
            augf = AnalyticUUIDGeneratorFactory()
            aug = augf.create()
            u = aug.next().uuidString
            s.add(u[:8 + 1 + 4])
        self.assertEquals(len(s), m)

    def test_y_prefix_spread(self):
        m = 10
        augf = AnalyticUUIDGeneratorFactory()
        # union bound: (1/16)^8 * m^2 = 2e-8
        s = set()
        for i in xrange(m):
            aug = augf.create()
            u = aug.next().uuidString
            s.add(u[:8 + 1 + 4 + 1 + 4 + 1 + 4])
        self.assertEquals(len(s), m)

    def test_spread(self):
        m = 100
        n = 100
        augf = AnalyticUUIDGeneratorFactory()
        # union bound: (2m-1)*(1/16)^12 * n^2 = 7e-9
        s = set()
        for i in xrange(m):
            aug = augf.create()
            u = aug.next().uuidString
            s.add(u)
            for j in xrange(n - 1):
                u = aug.next().uuidString
                s.add(u)
        self.assertEquals(len(s), m * n)
