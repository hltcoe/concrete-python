from concrete.util.file_io import CommunicationReader
from multiprocessing import Pool


def _read_comm_ids(path):
    return tuple(comm.id for (comm, _) in CommunicationReader(path))


def test_egg_extraction_with_subprocesses():
    '''
    Egg extraction of accelerated thrift fails when using
    multiple processes due to a locking error... this test
    aims to detect that bug.  (If accelerated thrift is
    installed unpacked, rather than packed in an egg, there
    is no bug; we are only concerned with the case that
    accelerated thrift is installed in an egg.)
    '''

    input_path = 'tests/testdata/simple.tar.gz'
    num_trials = 100
    num_procs = 2
    num_tasks = 4

    for i in xrange(num_trials):
        pool = Pool(num_procs)
        comm_ids_list = pool.map(_read_comm_ids, [input_path] * num_tasks)
        for comm_ids in comm_ids_list:
            assert comm_ids == ('one', 'two', 'three')
