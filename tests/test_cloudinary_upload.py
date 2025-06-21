


# test_cloudinary_upload.py
from dotenv import load_dotenv
import cloudinary.uploader

from config import *

load_dotenv(dotenv_path=ENV_PATH)

test_file = 'test.bin'
with open(test_file, 'wb') as f:
    f.write(b'This is a test file for Cloudinary upload.')

public_id = f"{UPLOAD_FOLDER}/test"
result = cloudinary.uploader.upload(
    test_file,
    resource_type='raw',
    public_id=public_id
)

print(f"Uploaded to Cloudinary. Secure URL: {result.get('secure_url')}")