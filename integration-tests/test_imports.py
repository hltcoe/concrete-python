#!/usr/bin/env python2.7


import os
import sys


def import_ok(module_name):
    try:
        module = __import__(module_name)
        sys.stdout.write('import succeeded: %s -> %s\n' %
                         (module_name, module))
        return True
    except Exception as ex:
        sys.stderr.write('import failed: %s: %s\n' %
                         (module_name, ex.message))
        return False


def test_imports():
    root = 'concrete'
    for (parent_path, dir_entries, file_entries) in os.walk(root):
        for basename in dir_entries:
            dir_path = os.path.join(parent_path, basename)
            module_name = dir_path.replace(os.sep, '.')
            assert import_ok(module_name)
        for basename in file_entries:
            if basename.endswith('.py') and basename != '__init__.py':
                file_path = os.path.join(parent_path, basename)
                module_name = file_path[:-len('.py')].replace(os.sep, '.')
                assert import_ok(module_name)


if __name__ == '__main__':
    test_imports()
