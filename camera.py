from picamera2 import Picamera2, Preview
from time import sleep

class PiCameraCapture:
    def __init__(self, api_key=None):
        pass

    def capture(self, output_path='karte.png', preview_time=2, show_preview=True):
        picam2 = Picamera2()
        # Create preview configuration (for live preview)
        preview_config = picam2.create_preview_configuration(
            main={'size': (4056, 3040)}, 
            lores={'size': (1014, 760)},
            display='main'
        )
        # Create still configuration (for capture)
        still_config = picam2.create_still_configuration(
            main={'size': (4056, 3040), 'format': 'RGB888'},
            lores={'size': (1014, 760)},
            display='main',
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
        picam2.start()
        # Set controls after starting camera for reliable manual exposure
        picam2.set_controls({
         #   'AnalogueGain': 1.0,         # ISO 100
            'ExposureTime': 150000,      
            'AeEnable': False,           # Manual exposure
            'AwbMode': 2,                # Indoor illumination
            'AwbEnable': True,
            'AfMode': 1,                # auto focus
            'AfRange': 1,                # Macro focus for close-up
            'Sharpness': 16,
            'Contrast': 1.1,
            'Saturation': 1.0,
        })
        sleep(1)  # Short settle before capture
        picam2.capture_file(output_path)
        picam2.close()

if __name__ == "__main__":
    cam = PiCameraCapture()
    cam.capture(show_preview=True)

