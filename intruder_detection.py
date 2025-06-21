


import os
import sys
import time
from datetime import datetime
import signal
import logging
# (from pywin32) needed for COM initialization on Windows since we must initialize COM on any thread that uses it
# import pythoncom
from queue import Queue
from threading import Thread
# local imports
from config import LOCAL_CAPTURE_FOLDER, UPLOAD_FOLDER, CLOUD_SERVICE, LOG_FILENAME
from detector import MotionDetector
from cloud_backends import CloudinaryBackend, DropboxBackend
from encryption import encrypt_file



# choose cloud backend
if CLOUD_SERVICE.lower() == 'cloudinary':
    backend = CloudinaryBackend()
else:
    backend = DropboxBackend()

# Setup logging
os.makedirs(LOCAL_CAPTURE_FOLDER, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOCAL_CAPTURE_FOLDER, LOG_FILENAME),
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)


# graceful shutdown
def handle_exit(signum, frame):
    """ Handle exit signals to upload logs and clean up before exiting """
    logging.info(f'Received signal {signum}, uploading log before exit')
    log_path = os.path.join(LOCAL_CAPTURE_FOLDER, LOG_FILENAME)
    try:
        url = backend.upload(log_path, f"{UPLOAD_FOLDER}/{LOG_FILENAME}")
        logging.info(f'Uploaded log: {url}')
        print(f'Log uploaded to: {url}')
    except Exception as e:
        logging.error(f'Failed to upload log: {e}')
        print(f'Failed to upload log: {e}')
    sys.exit(0)


# register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, lambda s,f: handle_exit(s,f)) # using a lambda in case we want to do something with the frame later
signal.signal(signal.SIGTERM, lambda s,f: handle_exit(s,f))


def producer(q: Queue):
    """ producer function that reads frames from the camera and detects motion """
    md = MotionDetector()
    try:
        # priming loop to stabilize the background subtractor
        md.priming_loop()
        while True:
            frame = md.read_frame()
            if frame is None:
                break
            if md.is_dark(frame):
                time.sleep(md.DARK_MODE_INTERVAL)
                continue
            if md.detect(frame):
                timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                print(f"[{timestamp}] Motion detected! Recording...")
                path = md.record()
                logging.info(f'Motion detected, file {path}')
                q.put(path)
            time.sleep(1)  # 1 second delay to reduce CPU usage (hoping to run this with a powershell script in low power mode later)
    except KeyboardInterrupt:
        logging.info('KeyboardInterrupt received, exiting producer')
    finally:
        md.release()

def consumer(q: Queue):
    """ consumer function that processes files from the queue, encrypts them, then uploads them """
    while True:
        file_path = q.get()
        try:
            enc = encrypt_file(file_path)
            key = f"{UPLOAD_FOLDER}/{os.path.basename(enc)}"
            url = backend.upload(enc, key)
            logging.info(f'Uploaded {enc} to {url}')
        except Exception as e:
            logging.error(f'Error processing {file_path}: {e}')
        finally:
            q.task_done()



if __name__ == '__main__':
    """ producer-consumer setup with producer writing to queue and consumer thread encrypt and uploading queued files """
    queue = Queue(maxsize=10)
    # # ensure DirectShow/COM is initialized in this thread specifically
    # pythoncom.CoInitialize()
    # start consumer thread while the producer runs in the main thread
    t_cons = Thread(target=consumer, args=(queue,), daemon=True)
    t_cons.start()
    producer(queue)  # run producer in the main thread
    queue.join()  # wait until all tasks complete
    t_cons.join()  # wait for consumer thread to finish (it will exit when the queue is empty)
