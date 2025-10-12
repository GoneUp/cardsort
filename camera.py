from picamera2 import Picamera2, Preview
from time import sleep

class PiCameraCapture:
    def __init__(self, api_key=None):
        pass

    def capture(self, output_path='/tmp/picture.jpg', preview_time=2, show_preview=True):
        picam2 = Picamera2()
        # Configure camera for low light (dark conditions)
        config = picam2.create_still_configuration(
            main={'size': (1080, 1920)},  # Portrait resolution
            lores={'size': (480, 640)},
            display='main'
        )
        picam2.configure(config)
        # Set best practices for low light and enable autofocus
        picam2.set_controls({
            'AnalogueGain': 8.0,         # Increase gain for sensitivity
            'ExposureTime': 1000000,     # 1 second exposure (adjust as needed)
            'AeEnable': False,           # Disable auto exposure for manual control
            'AwbEnable': True,           # Keep auto white balance
            'AfMode': 2,                 # Enable continuous autofocus (2 = Continuous)
        })
        if show_preview:
            picam2.start_preview(Preview.QTGL)
        picam2.start()
        sleep(preview_time)  # Allow sensor to settle and autofocus
        picam2.capture_file(output_path)
        if show_preview:
            picam2.stop_preview()
        picam2.close()

if __name__ == "__main__":
    cam = PiCameraCapture()
    cam.capture(show_preview=True)

