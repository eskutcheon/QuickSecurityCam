import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import binascii

# Generate a random 32-byte key and convert it to hex
encryption_key = os.urandom(32)
hex_key = binascii.hexlify(encryption_key).decode()
print(f"Encryption key: {hex_key}")

# Test data
data = b"Hello, this is a test."

# Encrypt the data
iv = os.urandom(12)
cipher = Cipher(algorithms.AES(encryption_key), modes.GCM(iv), backend=default_backend())
encryptor = cipher.encryptor()
encrypted_data = encryptor.update(data) + encryptor.finalize()
tag = encryptor.tag

# Write to file
with open('test.enc', 'wb') as f:
    f.write(iv + tag + encrypted_data)

# Read from file
with open('test.enc', 'rb') as f:
    iv = f.read(12)
    tag = f.read(16)
    encrypted_data = f.read()

# Decrypt the data
cipher = Cipher(algorithms.AES(encryption_key), modes.GCM(iv, tag), backend=default_backend())
decryptor = cipher.decryptor()
decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

print(f"Decrypted data: {decrypted_data}")