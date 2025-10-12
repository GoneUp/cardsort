from picamera2 import Picamera2, Preview
from time import sleep

class PiCameraCapture:
    def __init__(self, api_key=None):
        pass

    def capture(self, output_path='/tmp/picture.jpg', preview_time=2, show_preview=True):
        picam2 = Picamera2()
        # Create preview configuration (for live preview)
        preview_config = picam2.create_preview_configuration(
            main={'size': (3024, 4032)},  # High-res portrait for close-up
            lores={'size': (756, 1008)},
            display='main'
        )
        # Create still configuration (for capture)
        still_config = picam2.create_still_configuration(
            main={'size': (3024, 4032), 'format': 'RGB888'},
            lores={'size': (756, 1008)},
            display='main'
        )
        if show_preview:
            picam2.configure(preview_config)
            picam2.start_preview(Preview.QTGL)
            picam2.start()
            sleep(preview_time)
            picam2.stop_preview()
            picam2.stop()
        # Switch to still configuration for capture
        picam2.configure(still_config)
        picam2.set_controls({
            'AnalogueGain': 1.0,         # Normal gain for good light
            'ExposureTime': 150000,       # Short exposure for sharpness (50ms)
            'AeEnable': True,            # Enable auto exposure for normal light
            'AwbEnable': True,           # Enable auto white balance
            'AfMode': 2,                 # Continuous autofocus
            'AfRange': 1,                # Macro focus for close-up
        })
        picam2.start()
        sleep(0.5)  # Short settle before capture
        picam2.capture_file(output_path)
        picam2.close()

if __name__ == "__main__":
    cam = PiCameraCapture()
    cam.capture(show_preview=True)

