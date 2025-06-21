
# QuickSecurityCam

## Overview

A lightweight Python-based security system that monitors a webcam for motion, records short video clips upon detection, encrypts them with AES-GCM, and uploads to a cloud backend (Cloudinary or Dropbox). It's a simple and easy solution to catching culprits' faces for police even if your computer is stolen. It's designed for minimal dependencies and easy extension to native-code capture modules.

The original incarnation of this was written as a quick script to act as a security camera before going out of town and has been updated to be a little more versatile for possible future extensions.


## Features

- Real-time motion detection via OpenCV background subtraction
- Dark-room mode: reduced sampling under low light to avoid false positives
- Threaded pipeline: main thread handles fast video I/O; background thread encrypts & uploads
- AES-GCM encryption with user-provided 256-bit key
- Abstracted cloud backends: built-in support for Cloudinary & Dropbox, easy to add more
- Graceful shutdown: catches SIGINT/SIGTERM to upload logs before exit
- Cross-platform capture: auto-selects appropriate OpenCV backend on Windows, macOS, Linux

> [!WARNING] Dropbox Update
> Dropbox backend hasn't been fully tested in the refactored version. Avoid relying on it in general without adding session-refresh logic since API keys are short-lived


## Getting Started

1. Clone the repo
```bash
git clone https://github.com/eskutcheon/QuickSecurityCam.git
cd QuickSecurityCam
```

2. Install Python dependencies
```bash
pip install -r requirements.txt
```

3. Create your `tokens.env`
At the project root, create tokens.env containing:
```ini
ENCRYPTION_KEY=<64-hex-chars-256-bit>
DROPBOX_API_KEY=<your_dropbox_token>
CLOUDINARY_CLOUD_NAME=<your_cloud_name>
CLOUDINARY_API_KEY=<your_cloudinary_key>
CLOUDINARY_API_SECRET=<your_cloudinary_secret>
```

#### NOTES
- only one of `DROPBOX_API_KEY` or `CLOUDINARY_API_KEY` must be specified accordingly with the `CLOUD_SERVICE` name in `config.py` (default: "cloudinary")
- `ENCRYPTION_KEY` is currently a 256-bit encryption key for AES-GCM encryption, but more will be supported in the future
- Future supported cloud backends will follow the same <BACKEND>_API_KEY and <BACKEND>_API_SECRET naming patterns


4. Tweak configuration
Edit config.py or override via environment variables as needed:

```python
# config.py
USB_CAM_INDEX = 0             # USB camera index (0 is usually the default index)
# height and width of captured frames (default keeps computational cost lower)
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
# use 1/64 of total frame area as the threshold for motion detection (default is detection in 1 tile in an 8x8 grid)
MIN_AREA = FRAME_WIDTH*FRAME_HEIGHT//64
# duration of each recorded video clip in seconds - needs to be low enough to catch intruders before camera is disabled
VIDEO_CLIP_DURATION = 5
LOCAL_CAPTURE_FOLDER = "motion_captures"    # local directory name where raw and encrypted videos reside
UPLOAD_FOLDER = "webcam_captures"           # remote directory name where encrypted clips are uploaded
ENV_PATH = "./tokens.env"                   # path to file defining environment variables to load at runtime (secret keys)
LOG_FILENAME = "run.log"                    # log file name for logging events
DARK_MODE_THRESHOLD = 10.0                  # threshold for switching to dark mode, where captures are attempted less often
DARK_MODE_INTERVAL = 5.0                    # seconds between attempting video captures in dark mode
CLOUD_SERVICE = "cloudinary"                # or "dropbox"
```


5. Run the system
```python
python intruder_detection.py
```

You should see logs in `motion_captures/run.log`, and encrypted clips/backups in your configured cloud storage.


## Tips & Warnings

- Ensure your webcam drivers are installed and accessible by OpenCV.
- Windows users: no extra setup needed - DirectShow is used by default.
- macOS (untested): you may need to grant camera permissions if prompted.
- Linux (untested): install `v4l-utils` and run with proper user permissions to access `/dev/video*`.
- If your system hangs on startup, check camera permissions or try running as root on Linux.
- Keep your `ENCRYPTION_KEY` secret - losing it will render your captures unrecoverable. I recommend a password manager.
- Regularly rotate your encryption key and purge old backup files when storage/quota nears capacity.
- If you change any default paths such as `LOCAL_CAPTURE_FOLDER`, be sure to add this to the `.gitignore`


## Future Extensions

#### Higher Priority

- **Native Hot-path Replacement**
  - Replace the Python capture/detector with a C++ or Rust OpenCV module that publishes events over a socket; keep the Python consumer/upload logic.
  - The structure of the motion detector is already separated from the remaining code as much as possible

- **Plugin-style Cloud/Connectors**
  - Remove the hard dependence on cloud backends and allow users to write to other remote servers
  - Also allow for other new backends (S3, Azure Blob, Google Drive, FTP, SMB, etc.)

- **Multiple Camera Support & Exclusion Zones**
  - Handle multiple video sources simultaneously (e.g. front door, back yard).
  - Allow users to define "exclusion" or "detection" zones via a simple mask or GUI.

- **Alternative Camera Support**
  - Support a wider array of camera options in addition to the assumed USB webcams
  - Support night-vision/IR streams and automatically switch detection thresholds.

- **Advanced Detection Algorithms**
  - Implement more background subtraction algorithms (e.g. MOG, GMG, KNN) and other motion detection methods (e.g. [entropy-based texture maps](https://github.com/eskutcheon/Purr-Patrol-Turret/blob/master/src/host/tracking.py#L86))
  - Integrate optional, lightweight ML-based detectors (YOLOv5-tiny) for people vs. object classification to reduce false positives


#### Lower Priority

- **Additional Encryption Protocols**
  - Implement more encryption protocol options (e.g. AES, RSA, ECC) abstracted to a common interface.
  - Generally adopt best practices for encryption of CCTV footage

- **On-device Low-Power Mode**
  - Dynamically reduce FPS or suspend detection when on battery or constrained CPU usage.
  - Integrate with OS power events (e.g. Windows "Away Mode," Linux systemd inhibitors).

- **Containerization & Deployment**
  - Provide Docker/Podman images for easy deployment.
  - Helm chart or compose file for multi-service setups (e.g. separate detector, API, dashboard).

- **Web Dashboard & Livestream**
  - Real-time MJPEG/WebRTC stream of the camera feed (with authentication).
  - Dashboard to view recent captures, logs, and health metrics.

- **Push Notifications & Alerts**
  - Integrate with email, SMS (Twilio), or push-services (Pushover, Pushbullet) to alert on motion/failed uploads.










