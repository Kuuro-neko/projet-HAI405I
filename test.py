# Create an unique 8 caracter identifier from an int and a string
# Example: 1 + user1 = 4fd68s14

from uuid import uuid4
from hashlib import sha256

def create_unique_id(id, string):
    return sha256(str(id).encode() + string.encode() + str(uuid4()).encode()).hexdigest()[:8]

print(create_unique_id(1, 'Test1'))
print(create_unique_id(1, 'Test2'))
print(create_unique_id(2, 'Test1'))
print(create_unique_id(3, 'Test1'))