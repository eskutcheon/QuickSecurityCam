
import os
import sys
import time
import datetime
from config import (
    USB_CAM_INDEX, FRAME_WIDTH, FRAME_HEIGHT, MIN_AREA, VIDEO_CLIP_DURATION, LOCAL_CAPTURE_FOLDER,
    DARK_MODE_THRESHOLD, DARK_MODE_INTERVAL
)

#& UPDATE: removed from tokens.env file to simplify the setup for users
os.environ["OPENCV_LOG_LEVEL"] = "ERROR"    # set OpenCV log level to only show errors
os.environ["OPENCV_VIDEOIO_DEBUG"] = "1"    # enable OpenCV video I/O debug mode
import cv2


def get_video_capture_backend():
    """ Determine the appropriate video capture backend based on the operating system. """
    if sys.platform.startswith('win'):
        return cv2.CAP_DSHOW
    elif sys.platform.startswith('darwin'):
        return cv2.CAP_AVFOUNDATION
    else:
        return cv2.CAP_V4L2


class MotionDetector:
    DARK_MODE_INTERVAL = DARK_MODE_INTERVAL  # seconds between dark mode checks
    def __init__(self):
        # set up capture object for USB camera with the appropriate backend based on the OS
        backend = get_video_capture_backend()
        self.cap = cv2.VideoCapture(USB_CAM_INDEX, backend)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        if not self.cap.isOpened():
            raise RuntimeError('Cannot open camera')
        # history size is small to allow quick adaptation to changes in the scene - only considers the last 30 frames (around 30 seconds at 1 fps)
        self.bgsub = cv2.createBackgroundSubtractorMOG2(history=30)
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        self.in_dark_mode = False  # flag to track dark mode state
        # ensure local folder exists for saving motion captures
        os.makedirs(LOCAL_CAPTURE_FOLDER, exist_ok=True)


    def read_frame(self):
        ret, frame = self.cap.read()
        return frame if ret else None


    def detect(self, frame) -> bool:
        fgmask = self.bgsub.apply(frame)
        #thresh = cv2.threshold(fgmask, 25, 255, cv2.THRESH_BINARY)[1]
        #thresh = cv2.dilate(thresh, None, iterations=2)
        thresh = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, self.kernel)
        cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return any(cv2.contourArea(c) >= MIN_AREA for c in cnts)


    def priming_loop(self):
        """ run a priming loop for 5 seconds to allow the background subtractor to stabilize """
        print("Priming background subtractor...")
        for _ in range(10):
            frame = self.read_frame()
            if frame is None:
                break
            _ = self.detect(frame)
            time.sleep(0.5)


    def is_dark(self, frame) -> bool:
        """ Check if the scene is dark based on the mean pixel value across all channels and print status """
        # test if mean across all channels is below a threshold to determine if the scene is very dark
        dark_flag = frame.mean() < DARK_MODE_THRESHOLD
        if dark_flag and not self.in_dark_mode:
            print("Entering dark mode...")
            self.in_dark_mode = True
        elif not dark_flag and self.in_dark_mode:
            print("Exiting dark mode...")
            self.in_dark_mode = False
        return dark_flag


    def record(self) -> str:
        # record a fixed-duration clip to LOCAL_CAPTURE_FOLDER
        timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        filename = f"motion_{timestamp}.avi"
        path = os.path.join(LOCAL_CAPTURE_FOLDER, filename)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(path, fourcc, 20.0, (FRAME_WIDTH, FRAME_HEIGHT))
        start = time.time()
        while time.time() - start < VIDEO_CLIP_DURATION:
            ret, frame = self.cap.read()
            if not ret:
                break
            out.write(frame)
        out.release()
        return path


    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()