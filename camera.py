from picamera2 import Picamera2, Preview
from time import sleep

class PiCameraCapture:
    def __init__(self, api_key=None):
        pass

    def capture(self, output_path='/tmp/picture.jpg', preview_time=5):
        picam2 = Picamera2()
        picam2.start_preview(Preview.QTGL)
        sleep(preview_time)
        picam2.capture_file(output_path)
        picam2.stop_preview()

if __name__ == "__main__":
    cam = PiCameraCapture()
    cam.capture()

