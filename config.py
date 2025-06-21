
import os
from dotenv import load_dotenv



# config parameters
USB_CAM_INDEX = 0  # USB camera index (0 is usually default camera)
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
# use 1/64 of the total frame area as the minimum area for motion detection (basically the threshold is one tile in an 8x8 grid)
MIN_AREA = (FRAME_HEIGHT * FRAME_WIDTH) // 64   # minimum area size for motion detection
# duration of each video clip in seconds - needs to be low enough to catch the degens
VIDEO_CLIP_DURATION = 5
# folder for local webcam captures, saving both the raw and encrypted files
UPLOAD_FOLDER = 'webcam_captures'
LOCAL_CAPTURE_FOLDER = "motion_captures/"
ENV_PATH = "./tokens.env"
LOG_FILENAME = "run.log"  # log file for the application
# dark-room mode parameters (to reduce false positives in low light conditions)
DARK_MODE_THRESHOLD = 10.0  # threshold for dark mode detection
DARK_MODE_INTERVAL = 5  # seconds between dark mode checks
# encryption parameters
# TODO: add settings for encryption beyond the default AES-GCM eventually
# cloud service specification
CLOUD_SERVICE = "cloudinary"  # currently only supports Cloudinary



try:
    # load environment variables from tokens.env file and sets necessary openCV environment variables (OPENCV_LOG_LEVEL=debug and OPENCV_VIDEOIO_DEBUG=1)
    load_dotenv(dotenv_path=ENV_PATH)
except FileNotFoundError:
    print(f"File '{ENV_PATH}' not found - Now assuming that environment variables were set manually...")


# get encryption key from environment variables
#& previously encryption_key_hex
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", None) # using 32-byte key for AES encryption
if not ENCRYPTION_KEY:
    raise Exception("ENCRYPTION_KEY not set in environment variables.")
# #& previously encryption_key
# ENCRYPTION_KEY = binascii.unhexlify(encryption_key_hex)

# get API token and encryption key from environment variables
#& previously CLOUD_ACCESS_TOKEN
DROPBOX_API_KEY = os.getenv("DROPBOX_API_KEY", None)
if CLOUD_SERVICE.lower() == "dropbox" and not DROPBOX_API_KEY:
    raise Exception("DROPBOX_API_KEY not set in environment variables.")
# cloudinary configuration
#& previously cloud_name, api_key, api_secret
# TODO: should probably give CLOUDINARY_CLOUD_NAME a default value since it's less critical than the others
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", None)
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", None)
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", None)
# secure = True
if CLOUD_SERVICE.lower() == "cloudinary" and not (CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET):
    raise Exception("Cloudinary credentials not set in environment variables.")