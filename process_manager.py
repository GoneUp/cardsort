import time
import os
from typing import List, Optional, Dict
from gpio_manager import gpio
from dataclasses import dataclass
from process_control import ProcessController
from carddata import CardData


@dataclass
class CardDataExtended:
    """Extends CardData with processing metadata"""
    card: CardData
    processed_at: float
    magazin_name: str
    position: int


class ProcessManager:
    """
    Manages the card processing system and maintains a database of all processed cards.
    Provides a high-level interface for the web API to control the process and access data.
    """
    
    def __init__(self):
        self._controller: Optional[ProcessController] = None
        self._all_cards: List[CardDataExtended] = []
        self._current_run_start: Optional[float] = None
    
    def start_process(self, magazin_name: str, start_index: int = 1, home_magazine: bool = False) -> None:
        """Start the processing with given parameters"""
        # Initialize controller if needed
        if not self._controller:
            gpio.setmode(gpio.BCM)
            self._controller = ProcessController()
        
        # Check if already running
        if self._controller._thread and self._controller._thread.is_alive():
            raise RuntimeError("Process already running")
        
        def on_card_processed(card: CardData, position: int):
            # Store extended card data when card is processed
            extended = CardDataExtended(
                card=card,
                processed_at=time.time(),
                magazin_name=self._controller.magazin_name,
                position=position
            )
            self._all_cards.append(extended)
        
        # Set up callback and start
        self._current_run_start = time.time()
        self._controller.on_card_processed = on_card_processed
        return self._controller.start_async(
            magazin_name=magazin_name,
            start_index=start_index,
            home_magazine=home_magazine
        )
    
    def stop_process(self, emergency: bool = False) -> None:
        """Stop the current process"""
        if self._controller:
            self._controller.stop(emergency=emergency)
    
    def get_status(self) -> dict:
        """Get current process status including statistics"""
        if not self._controller:
            return {
                "running": False,
                "current_position": 0,
                "magazin_name": None,
                "total_cards_processed": len(self._all_cards),
                "current_run_cards": 0,
                "current_run_time": 0
            }
        
        current_run_cards = 0
        if self._current_run_start:
            # Count cards processed in current run
            current_run_cards = sum(
                1 for card in self._all_cards
                if card.processed_at >= self._current_run_start
            )
        
        return {
            "running": self._controller._thread and self._controller._thread.is_alive(),
            "current_position": self._controller.current_position,
            "magazin_name": self._controller.magazin_name,
            "total_cards_processed": len(self._all_cards),
            "current_run_cards": current_run_cards,
            "current_run_time": time.time() - (self._current_run_start or time.time())
        }
    
    def export_all_cards_csv(self, path: str = None) -> str:
        """Export all processed cards to a single CSV file"""
        if not path:
            path = os.path.join(os.getcwd(), f"all_cards_{int(time.time())}.csv")
        
        # Group cards by magazine for writing
        by_magazine: Dict[str, List[tuple[int, CardData]]] = {}
        for extended in self._all_cards:
            if extended.magazin_name not in by_magazine:
                by_magazine[extended.magazin_name] = []
            by_magazine[extended.magazin_name].append((extended.position, extended.card))
        
        # Write each magazine's cards in order
        all_results = []
        for magazin_name, cards in by_magazine.items():
            # Sort by position
            cards.sort(key=lambda x: x[0])
            all_results.extend([c[1] for c in cards])
        
        from csv_out import write_carddata_csv
        write_carddata_csv(all_results, path)
        return path
    
    def get_processed_cards(self, magazin_name: Optional[str] = None) -> List[CardDataExtended]:
        """Get all processed cards, optionally filtered by magazine"""
        if magazin_name:
            return [c for c in self._all_cards if c.magazin_name == magazin_name]
        return self._all_cards.copy()  # Return copy to prevent external modification