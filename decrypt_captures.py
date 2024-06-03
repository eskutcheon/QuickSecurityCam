from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv
import os
import binascii

ENV_PATH = "./tokens.env"
try:
    # load environment variables from tokens.env file and sets necessary openCV environment variables (OPENCV_LOG_LEVEL and OPENCV_VIDEOIO_DEBUG)
    load_dotenv(dotenv_path=ENV_PATH)
except FileNotFoundError:
    raise Exception(f"File '{ENV_PATH}' not found. Assuming that environment variables were set manually.")
# get API token and encryption key from environment variables
encryption_key_hex = os.getenv("ENCRYPTION_KEY")# .encode() # ensure key is in bytes
encryption_key = binascii.unhexlify(encryption_key_hex)

def decrypt_file(encrypted_file_path, output_file_path):
    try:
        file_size = os.path.getsize(encrypted_file_path)
        # read encrypted file in binary format
        with open(encrypted_file_path, 'rb') as f:
            iv = f.read(12) # 12 byte IV
            # read the encrypted data except IV and tag
            encrypted_data = f.read(file_size - 28)
            tag = f.read(16)  # 16-byte tag
        # create cipher object using the same key and IV
        cipher = Cipher(algorithms.AES(encryption_key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        # write decrypted data to the output file
        with open(output_file_path, 'wb') as f:
            f.write(decrypted_data)
        # print(f"Decryption successful: {output_file_path}")
    except Exception as e:
        print((f"An error occurred during decryption: {e}"))
        raise e

# TODO: replace with command line input
encrypted_file_path = 'motion_captures/motion_20240602-192003.avi.enc'
output_file_path = 'motion_captures/test_decrypt/decrypted_file.avi'
if not os.path.exists(os.path.dirname(output_file_path)):
    os.makedirs(os.path.dirname(output_file_path))

decrypt_file(encrypted_file_path, output_file_path)
print(f"Decrypted file saved as {output_file_path}")
