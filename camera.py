import os
from abc import ABC, abstractmethod
from time import sleep
import logging
from PIL import Image, ImageDraw
from datetime import datetime

class BaseCameraCapture(ABC):
    """Base class defining the camera interface"""
    
    @abstractmethod
    def capture(self, output_path='karte.png', preview_time=5, show_preview=True):
        """Capture an image and save it to the given path"""
        pass

class MockCameraCapture(BaseCameraCapture):
    """Mock camera that generates test images instead of using real hardware"""
    
    def __init__(self):
        self._capture_count = 0
    
    def capture(self, output_path='karte.png', preview_time=5, show_preview=True):
        """Create a test image with timestamp and counter"""
        if show_preview:
            logging.info(f"[MOCK] Showing preview for {preview_time} seconds")
            sleep(preview_time)
        
        # Create a simple test image (800x600 with text)
        width = 800
        height = 600
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw some text
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._capture_count += 1
        
        text = [
            f"MOCK CAMERA CAPTURE",
            f"Time: {timestamp}",
            f"Capture #{self._capture_count}",
            f"Preview: {preview_time}s shown" if show_preview else "No preview"
        ]
        
        # Calculate text positions
        line_height = 30
        start_y = (height - len(text) * line_height) // 2
        
        for i, line in enumerate(text):
            # Draw text centered
            text_width = len(line) * 10  # Approximate width
            x = (width - text_width) // 2
            y = start_y + i * line_height
            draw.text((x, y), line, fill='black')
        
        # Draw a border
        draw.rectangle([0, 0, width-1, height-1], outline='black', width=2)
        
        # Save the image
        img.save(output_path)
        logging.info(f"[MOCK] Captured test image to {output_path}")
        sleep(0.5)  # Simulate brief capture time

try:
    from picamera2 import Picamera2, Preview
    
    class PiCameraCapture(BaseCameraCapture):
        """Real camera implementation using picamera2"""
        
        def __init__(self):
            pass
        
        def capture(self, output_path='karte.png', preview_time=5, show_preview=True):
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
            picam2.start()
            picam2.autofocus_cycle()
            sleep(2)  # Short settle before capture
            picam2.capture_file(output_path)
            picam2.close()
except ImportError:
    logging.warning("picamera2 not available, PiCameraCapture will not be available")
    PiCameraCapture = None

def create_camera():
    """Factory function to create the appropriate camera instance"""
    if os.getenv('MOCK_HARDWARE') or PiCameraCapture is None:
        logging.info("Using mock camera (MOCK_HARDWARE=1 or picamera2 not available)")
        return MockCameraCapture()
    else:
        return PiCameraCapture()

# For backwards compatibility, use the factory function
CameraCapture = create_camera

if __name__ == "__main__":
    # Test both real and mock cameras
    if os.getenv('MOCK_HARDWARE'):
        cam = create_camera()  # Will be mock
        cam.capture(show_preview=True)
    else:
        try:
            cam = create_camera()  # Will be real if available
            cam.capture(show_preview=True)
        except Exception as e:
            print(f"Error with real camera: {e}")
            print("Try running with MOCK_HARDWARE=1 to use mock camera")

