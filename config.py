



# config parameters
USB_CAM_INDEX = 0  # USB camera index (0 is usually default camera)
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
# NOTE: above dimensions mean that the area below is roughly 1/300 of total area
MIN_AREA = 1000  # minimum area size for motion detection
# duration of each video clip in seconds - needs to be low enough to catch the degens
VIDEO_CLIP_DURATION = 5

UPLOAD_FOLDER = 'webcam_captures'
LOCAL_CAPTURE_FOLDER = "motion_captures/"
ENV_PATH = "./tokens.env"