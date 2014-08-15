"""
"""

import uuid

import concrete

def generate_UUID():
    concrete_uuid = concrete.UUID()
    concrete_uuid.uuidString = str(uuid.uuid4())
    return concrete_uuid
