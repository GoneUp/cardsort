import os
from typing import Optional

class GpioManager:
    """
    Manages GPIO access with optional mock mode for development/testing.
    Use MOCK_HARDWARE=1 environment variable to enable mock mode.
    """
    
    def __init__(self):
        self._mock_mode = bool(os.getenv('MOCK_HARDWARE'))
        self._gpio = None
        if not self._mock_mode:
            try:
                import RPi.GPIO as GPIO
                self._gpio = GPIO
            except ImportError:
                print("Warning: RPi.GPIO not available, falling back to mock mode")
                self._mock_mode = True
    
    @property
    def BCM(self) -> int:
        """BCM pin numbering mode"""
        return self._gpio.BCM if self._gpio else 11
    
    @property
    def OUT(self) -> int:
        """Output pin mode"""
        return self._gpio.OUT if self._gpio else 0
    
    @property
    def IN(self) -> int:
        """Input pin mode"""
        return self._gpio.IN if self._gpio else 1
    
    @property
    def HIGH(self) -> int:
        """Logic high level"""
        return self._gpio.HIGH if self._gpio else 1
    
    @property
    def LOW(self) -> int:
        """Logic low level"""
        return self._gpio.LOW if self._gpio else 0
    
    def setmode(self, mode: int) -> None:
        """Set the pin numbering mode"""
        if not self._mock_mode:
            self._gpio.setmode(mode)
    
    def setup(self, pin: int, mode: int) -> None:
        """Set up a GPIO pin"""
        if not self._mock_mode:
            self._gpio.setup(pin, mode)
    
    def input(self, pin: int) -> int:
        """Read from a GPIO pin"""
        if self._mock_mode:
            # In mock mode, simulate the home sensor by returning HIGH
            # after a few reads to simulate finding home
            if not hasattr(self, '_mock_reads'):
                self._mock_reads = 0
            self._mock_reads += 1
            return self.HIGH if self._mock_reads > 5 else self.LOW
        return self._gpio.input(pin)
    
    def output(self, pin: int, value: int) -> None:
        """Write to a GPIO pin"""
        if not self._mock_mode:
            self._gpio.output(pin, value)
    
    def cleanup(self) -> None:
        """Clean up GPIO resources"""
        if not self._mock_mode and self._gpio:
            self._gpio.cleanup()

# Global instance
gpio = GpioManager()