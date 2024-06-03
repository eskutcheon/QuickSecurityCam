import cv2
import dropbox
import time
import datetime
import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import binascii


# config parameters
USB_CAM_INDEX = 0  # USB camera index (0 is usually default camera)
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
# NOTE: above dimensions mean that the area below is roughly 1/300 of total area
MIN_AREA = 1000  # minimum area size for motion detection
# duration of each video clip in seconds - needs to be low enough to catch the degens
VIDEO_CLIP_DURATION = 5

DROPBOX_FOLDER = '/webcam_captures/'
LOCAL_CAPTURE_FOLDER = "motion_captures/"
ENV_PATH = "./tokens.env"
try:
    # load environment variables from tokens.env file and sets necessary openCV environment variables (OPENCV_LOG_LEVEL=debug and OPENCV_VIDEOIO_DEBUG=1)
    load_dotenv(dotenv_path=ENV_PATH)
except FileNotFoundError:
    raise Exception(f"File '{ENV_PATH}' not found. Assuming that environment variables were set manually.")
# get API token and encryption key from environment variables

DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_API_KEY")
# using 32-byte key for AES encryption
encryption_key_hex = os.getenv("ENCRYPTION_KEY")# .encode() # ensure key is in bytes
encryption_key = binascii.unhexlify(encryption_key_hex)



def encrypt_file(file_path):
    # read local file data as binary file
    with open(file_path, 'rb') as f:
        file_data = f.read()
    # generate a random 12-byte IV for AES GCM encryption
    iv = os.urandom(12)
    cipher = Cipher(algorithms.AES(encryption_key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(file_data) + encryptor.finalize()
    encrypted_file_path = file_path + '.enc'
    with open(encrypted_file_path, 'wb') as f:
        f.write(iv + encrypted_data + encryptor.tag)
    return encrypted_file_path

def upload_to_dropbox(file_path, dropbox_path):
    dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
    with open(file_path, 'rb') as f:
        dbx.files_upload(f.read(), dropbox_path)


def video_feed_capture(capture, fgbg):
    while True:
        ret, frame = capture.read()
        if not ret:
            break
        fgmask = fgbg.apply(frame)
        thresh = cv2.threshold(fgmask, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        motion_detected = False
        for c in cnts:
            if cv2.contourArea(c) < MIN_AREA:
                continue
            motion_detected = True
            break
        if motion_detected:
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            video_filename = f"motion_{timestamp}.avi"
            video_filepath = f"./{LOCAL_CAPTURE_FOLDER}/{video_filename}"
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(video_filepath, fourcc, 20.0, (FRAME_WIDTH, FRAME_HEIGHT))
            start_time = time.time()
            while time.time() - start_time < VIDEO_CLIP_DURATION:
                ret, frame = capture.read()
                if not ret:
                    break
                out.write(frame)
            out.release()
            encrypted_file_path = encrypt_file(video_filepath)
            dropbox_path = DROPBOX_FOLDER + os.path.basename(encrypted_file_path)
            upload_to_dropbox(encrypted_file_path, dropbox_path)
            print(f"Uploaded {encrypted_file_path} to Dropbox at {dropbox_path}")
        time.sleep(1)  # 1 second delay to reduce CPU usage (hoping to run this with a powershell script in low power mode later)



if __name__ == "__main__":
    capture = cv2.VideoCapture(USB_CAM_INDEX, cv2.CAP_DSHOW)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    if not capture.isOpened():
        raise Exception("ERROR: Could not open webcam.")
    # initialize background subtractor
    fgbg = cv2.createBackgroundSubtractorMOG2()
    video_feed_capture(capture, fgbg)
    capture.release()
    cv2.destroyAllWindows()
