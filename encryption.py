
import os
import binascii
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
# local imports
from config import ENCRYPTION_KEY



def _hex_to_bytes(hex_string: str) -> bytes:
    """ Convert a hex string to bytes """
    try:
        return binascii.unhexlify(hex_string)
    except binascii.Error as e:
        raise ValueError(f"Invalid hex string: {e}")


def encrypt_file(file_path: str) -> str:
    """ encrypt a file using AES-GCM and return the path to the encrypted file (.enc) """
    key_bytes = _hex_to_bytes(ENCRYPTION_KEY)
    # read local file data to encrypt as binary
    with open(file_path, 'rb') as f:
        data = f.read()
    # generate a random 12-byte IV for AES GCM encryption
    iv = os.urandom(12)
    cipher = Cipher(algorithms.AES(key_bytes), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(data) + encryptor.finalize()
    out_path = file_path + '.enc'
    with open(out_path, 'wb') as f:
        f.write(iv + encrypted + encryptor.tag)
    return out_path


def decrypt_file(encrypted_file_path, output_file_path):
    try:
        key_bytes = _hex_to_bytes(ENCRYPTION_KEY)
        file_size = os.path.getsize(encrypted_file_path)
        # read encrypted file in binary format
        with open(encrypted_file_path, 'rb') as f:
            iv = f.read(12) # 12 byte IV
            # read the encrypted data except IV and tag
            encrypted_data = f.read(file_size - 28)
            tag = f.read(16)  # 16-byte tag
        # create cipher object using the same key and IV
        cipher = Cipher(algorithms.AES(key_bytes), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        # write decrypted data to the output file
        with open(output_file_path, 'wb') as f:
            f.write(decrypted_data)
        # print(f"Decryption successful: {output_file_path}")
    except Exception as e:
        print((f"An error occurred during decryption: {e}"))
        raise e