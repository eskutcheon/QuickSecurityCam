import dropbox
import os
from dotenv import load_dotenv

ENV_PATH = "./tokens.env"
try:
    # load environment variables from tokens.env file and sets necessary openCV environment variables (OPENCV_LOG_LEVEL and OPENCV_VIDEOIO_DEBUG)
    load_dotenv(dotenv_path=ENV_PATH)
except FileNotFoundError:
    raise Exception(f"File '{ENV_PATH}' not found. Assuming that environment variables were set manually.")
# get API token from environment variables
DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_API_KEY")
DROPBOX_FOLDER = '/webcam_captures/'
TEST_FILE_PATH = 'test.txt'

# Create a test file
with open(TEST_FILE_PATH, 'w') as f:
    f.write('This is a test file for Dropbox upload.')

def upload_to_dropbox(file_path, dropbox_path):
    dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
    with open(file_path, 'rb') as f:
        dbx.files_upload(f.read(), dropbox_path)

try:
    dropbox_path = DROPBOX_FOLDER + 'test.txt'
    upload_to_dropbox(TEST_FILE_PATH, dropbox_path)
    print(f"Uploaded {TEST_FILE_PATH} to Dropbox at {dropbox_path}")
except dropbox.exceptions.AuthError as e:
    print(f"AuthError: {e}")
except dropbox.exceptions.ApiError as e:
    print(f"ApiError: {e}")
except Exception as e:
    print(f"Error: {e}")
