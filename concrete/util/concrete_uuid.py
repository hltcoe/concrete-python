"""
"""

# Force 'import uuid' to import the Python standard library module
# named "uuid", and not the "concrete.uuid" module
from __future__ import absolute_import

import uuid as python_uuid

import concrete

def generate_UUID():
    c_uuid = concrete.UUID()
    c_uuid.uuidString = str(python_uuid.uuid4())
    return c_uuid
