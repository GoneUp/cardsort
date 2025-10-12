from picamera import PiCamera
from time import sleep

class PiCameraCapture:
    def __init__(self, api_key=None):
        pass 

    def capture(self):
        camera = PiCamera()
        camera.start_preview()
        sleep(5)
        camera.capture('/tmp/picture.jpg')
        camera.stop_preview()

if __name__ == "__main__":
    cam = PiCameraCapture()
    cam.capture()

