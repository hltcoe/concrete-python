"""
"""

# This file must not be named 'uuid.py', otherwise 'import uuid' will
# try to import this file instead of the Python standard library
# module
import uuid as python_uuid

import concrete

def generate_UUID():
    c_uuid = concrete.UUID()
    c_uuid.uuidString = str(python_uuid.uuid4())
    return c_uuid
