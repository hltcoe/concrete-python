from __future__ import unicode_literals
from concrete.util import (
    generate_UUID, bin_to_hex, hex_to_bin, AnalyticUUIDGeneratorFactory,
    generate_uuid_unif, generate_hex_unif, split_uuid, join_uuid,
)

from concrete import AnnotationMetadata, Communication
from concrete.validate import validate_communication

import re
import time

from pytest import raises

UUID_RE = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')


def test_generate_UUID():
    comm = Communication()
    comm.uuid = generate_UUID()


def test_validate_minimal_communication_with_uuid():
    comm = Communication()
    comm.id = "myID"
    comm.metadata = AnnotationMetadata(
        tool="TEST", timestamp=int(time.time()))
    comm.type = "Test Communication"
    comm.uuid = generate_UUID()
    assert validate_communication(comm)


def test_hex_to_bin():
    assert hex_to_bin('0') == 0
    assert hex_to_bin('1') == 1
    assert hex_to_bin('2') == 2
    assert hex_to_bin('3') == 3
    assert hex_to_bin('4') == 4
    assert hex_to_bin('5') == 5
    assert hex_to_bin('6') == 6
    assert hex_to_bin('7') == 7
    assert hex_to_bin('8') == 8
    assert hex_to_bin('9') == 9
    assert hex_to_bin('a') == 10
    assert hex_to_bin('A') == 10
    assert hex_to_bin('b') == 11
    assert hex_to_bin('B') == 11
    assert hex_to_bin('c') == 12
    assert hex_to_bin('C') == 12
    assert hex_to_bin('d') == 13
    assert hex_to_bin('D') == 13
    assert hex_to_bin('e') == 14
    assert hex_to_bin('E') == 14
    assert hex_to_bin('f') == 15
    assert hex_to_bin('F') == 15
    assert hex_to_bin('caf') == 15 + 10 * 16 + 12 * 256
    assert hex_to_bin('cafe3') == 3 + 14 * 16 + 15 * 256 + 10 * 4096 + 12 * 65536


def test_bin_to_hex():
    assert bin_to_hex(0) == '0'
    assert bin_to_hex(1) == '1'
    assert bin_to_hex(2) == '2'
    assert bin_to_hex(3) == '3'
    assert bin_to_hex(4) == '4'
    assert bin_to_hex(5) == '5'
    assert bin_to_hex(6) == '6'
    assert bin_to_hex(7) == '7'
    assert bin_to_hex(8) == '8'
    assert bin_to_hex(9) == '9'
    assert bin_to_hex(10).lower() == 'a'
    assert bin_to_hex(11).lower() == 'b'
    assert bin_to_hex(12).lower() == 'c'
    assert bin_to_hex(13).lower() == 'd'
    assert bin_to_hex(14).lower() == 'e'
    assert bin_to_hex(15).lower() == 'f'
    assert bin_to_hex(15 + 10 * 16 + 12 * 256).lower() == 'caf'
    assert bin_to_hex(3 + 14 * 16 + 15 * 256 + 10 * 4096 + 12 * 65536).lower() == 'cafe3'


def test_bin_to_hex_with_len():
    assert bin_to_hex(0, 4) == '0000'
    assert bin_to_hex(1, 4) == '0001'
    assert bin_to_hex(2, 4) == '0002'
    assert bin_to_hex(3, 4) == '0003'
    assert bin_to_hex(4, 4) == '0004'
    assert bin_to_hex(5, 4) == '0005'
    assert bin_to_hex(6, 4) == '0006'
    assert bin_to_hex(7, 4) == '0007'
    assert bin_to_hex(8, 4) == '0008'
    assert bin_to_hex(9, 4) == '0009'
    assert bin_to_hex(10, 4).lower() == '000a'
    assert bin_to_hex(11, 4).lower() == '000b'
    assert bin_to_hex(12, 4).lower() == '000c'
    assert bin_to_hex(13, 4).lower() == '000d'
    assert bin_to_hex(14, 4).lower() == '000e'
    assert bin_to_hex(15, 4).lower() == '000f'
    assert bin_to_hex(15 + 10 * 16 + 12 * 256, 4).lower() == '0caf'
    with raises(ValueError):
        bin_to_hex(3 + 14 * 16 + 15 * 256 + 10 * 4096 + 12 * 65536, 4)


def test_split_uuid_valid():
    assert (
        split_uuid('7575a428-aaf7-4c2e-929e-1e2a0ab59e16') ==
        ('7575a428aaf7', '4c2e929e', '1e2a0ab59e16')
    )


def test_split_uuid_too_many_pieces():
    with raises(ValueError):
        split_uuid('aaf7-7575a428-aaf7-4c2e-929e-1e2a0ab59e16')


def test_split_uuid_too_few_pieces():
    with raises(ValueError):
        split_uuid('7575a428-4c2e-929e-1e2a0ab59e16')


def test_split_uuid_first_piece_too_long():
    with raises(ValueError):
        split_uuid('7575a428a-aaf7-4c2e-929e-1e2a0ab59e16')


def test_split_uuid_second_piece_too_long():
    with raises(ValueError):
        split_uuid('7575a428-aaf7a-4c2e-929e-1e2a0ab59e16')


def test_split_uuid_third_piece_too_long():
    with raises(ValueError):
        split_uuid('7575a428-aaf7-4c2ea-929e-1e2a0ab59e16')


def test_split_uuid_fourth_piece_too_long():
    with raises(ValueError):
        split_uuid('7575a428-aaf7-4c2e-929ea-1e2a0ab59e16')


def test_split_uuid_fifth_piece_too_long():
    with raises(ValueError):
        split_uuid('7575a428-aaf7-4c2e-929e-1e2a0ab59e16a')


def test_split_uuid_first_piece_too_short():
    with raises(ValueError):
        split_uuid('7575a42-aaf7-4c2e-929e-1e2a0ab59e16')


def test_split_uuid_second_piece_too_short():
    with raises(ValueError):
        split_uuid('7575a428-aaf-4c2e-929e-1e2a0ab59e16')


def test_split_uuid_third_piece_too_short():
    with raises(ValueError):
        split_uuid('7575a428-aaf7-4c2-929e-1e2a0ab59e16')


def test_split_uuid_fourth_piece_too_short():
    with raises(ValueError):
        split_uuid('7575a428-aaf7-4c2e-929-1e2a0ab59e16')


def test_split_uuid_fifth_piece_too_short():
    with raises(ValueError):
        split_uuid('7575a428-aaf7-4c2e-929e-1e2a0ab59e1')


def test_join_uuid_valid():
    assert (
        join_uuid('7575a428aaf7', '4c2e929e', '1e2a0ab59e16') ==
        '7575a428-aaf7-4c2e-929e-1e2a0ab59e16'
    )


def test_join_uuid_first_piece_too_long():
    with raises(ValueError):
        join_uuid('7575a428aaf7a', '4c2e929e', '1e2a0ab59e16')


def test_join_uuid_second_piece_too_long():
    with raises(ValueError):
        join_uuid('7575a428aaf7', '4c2e929ea', '1e2a0ab59e16')


def test_join_uuid_third_piece_too_long():
    with raises(ValueError):
        join_uuid('7575a428aaf7', '4c2e929e', '1e2a0ab59e16a')


def test_join_uuid_first_piece_too_short():
    with raises(ValueError):
        join_uuid('7575a428aaf', '4c2e929e', '1e2a0ab59e16')


def test_join_uuid_second_piece_too_short():
    with raises(ValueError):
        join_uuid('7575a428aaf7', '4c2e929', '1e2a0ab59e16')


def test_join_uuid_third_piece_too_short():
    with raises(ValueError):
        join_uuid('7575a428aaf7', '4c2e929e', '1e2a0ab59e1')


def test_generate_hex_unif_range():
    n = 1000  # (1 - 1/16)^n = 9e-29
    r = set()
    for i in range(n):
        r.add(generate_hex_unif(1))
    assert (
        sorted(map(lambda x: str(x).lower(), r)) ==
        [c for c in '0123456789abcdef']
    )


def test_generate_hex_unif_len():
    h = generate_hex_unif(21)  # (1/16)^(n-1) = 8e-25
    assert len(h) == 21
    assert len(set(c for c in h)) > 1


def test_generate_hex_unif_spread():
    n = 1000
    m = 32
    # union bound: (1/16)^m * n^2 = 3e-33
    s = set([generate_hex_unif(m) for i in range(n)])
    assert len(s) == n


def test_generate_uuid_unif_format():
    u = generate_uuid_unif()
    assert UUID_RE.match(u) is not None


def test_generate_uuid_unif_spread():
    n = 1000
    # union bound: (1/16)^32 * n^2 = 3e-33
    s = set([generate_uuid_unif() for i in range(n)])
    assert len(s) == n


class Duck(object):
    pass


def test_AnalyticUUIDGeneratorFactory_x_prefix_no_comm():
    n = 1000
    augf = AnalyticUUIDGeneratorFactory()
    u = augf.comm_uuid
    for i in range(n):
        aug = augf.create()
        assert next(aug).uuidString.startswith(u[:8 + 1 + 4])


def test_AnalyticUUIDGeneratorFactory_x_prefix_with_comm():
    n = 1000
    u = '7575a428-aaf7-4c2e-929e-1e2a0ab59e16'
    comm = Duck()
    comm.uuid = Duck()
    comm.uuid.uuidString = u
    augf = AnalyticUUIDGeneratorFactory(comm)
    assert augf.comm_uuid == u
    for i in range(n):
        aug = augf.create()
        assert next(aug).uuidString.startswith(u[:8 + 1 + 4])


def test_AnalyticUUIDGeneratorFactory_x_prefix_bad_comm_uuid():
    u = '7575a428a-aaf7-4c2e-929e-1e2a0ab59e16'
    comm = Duck()
    comm.uuid = Duck()
    comm.uuid.uuidString = u
    augf = AnalyticUUIDGeneratorFactory(comm)
    with raises(ValueError):
        augf.create()


def test_AnalyticUUIDGeneratorFactory_y_prefix():
    m = 100
    n = 100
    augf = AnalyticUUIDGeneratorFactory()
    for i in range(m):
        aug = augf.create()
        uu = next(aug).uuidString
        for j in range(n - 1):
            assert next(aug).uuidString.startswith(
                uu[:8 + 1 + 4 + 1 + 4 + 1 + 4])


def test_AnalyticUUIDGeneratorFactory_z_increment():
    m = 100
    n = 100
    augf = AnalyticUUIDGeneratorFactory()
    for i in range(m):
        aug = augf.create()
        u = next(aug).uuidString
        z = int(u[8 + 1 + 4 + 1 + 4 + 1 + 4 + 1:], 16)
        for j in range(n - 1):
            u = next(aug).uuidString
            assert (
                int(u[8 + 1 + 4 + 1 + 4 + 1 + 4 + 1:], 16) ==
                (z + 1) % 2**48
            )
            z = (z + 1) % 2**48


def test_AnalyticUUIDGeneratorFactory_x_prefix_spread():
    m = 100
    # union bound: (1/16)^12 * m^2 = 4e-11
    s = set()
    for i in range(m):
        augf = AnalyticUUIDGeneratorFactory()
        aug = augf.create()
        u = next(aug).uuidString
        s.add(u[:8 + 1 + 4])
    assert len(s) == m


def test_AnalyticUUIDGeneratorFactory_y_prefix_spread():
    m = 10
    augf = AnalyticUUIDGeneratorFactory()
    # union bound: (1/16)^8 * m^2 = 2e-8
    s = set()
    for i in range(m):
        aug = augf.create()
        u = next(aug).uuidString
        s.add(u[:8 + 1 + 4 + 1 + 4 + 1 + 4])
    assert len(s) == m


def test_AnalyticUUIDGeneratorFactory_spread():
    m = 100
    n = 100
    augf = AnalyticUUIDGeneratorFactory()
    # union bound: (2m-1)*(1/16)^12 * n^2 = 7e-9
    s = set()
    for i in range(m):
        aug = augf.create()
        u = next(aug).uuidString
        s.add(u)
        for j in range(n - 1):
            u = next(aug).uuidString
            s.add(u)
    assert len(s) == m * n
