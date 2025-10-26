import os
from typing import Iterable, List
from carddata import CardData


def write_carddata_csv(cards: Iterable[CardData], csv_path: str, magazin_name: str = 'A', start_index: int = 1, ankaufspreis_default: str = 'unbekannt') -> None:
    """Write an iterable of CardData objects to a semicolon-separated CSV.

    Args:
        cards: Iterable of CardData objects. Order is assumed to match magazine slots starting at start_index.
        csv_path: Destination file path to write the CSV to.
        magazin_name: The magazine letter/name to write in the first column.
        start_index: 1-based starting slot number for the first card in `cards`.
        ankaufspreis_default: Default value to place in the Ankaufspreis column when missing.
    """
    header = [
        "Fachbuchstabe","Fachnummer","Kartenname","Bildnummer","Edition","Kartennummer","Sprache","Verlag","Erscheinungsjahr","Region","Seltenheit","Kartentyp","Subtyp","Farbe","Spezialeffekte","Limitierung","Autogramm","Memorabilia","Zustand","Ankaufspreis","Marktwert"
    ]

    os.makedirs(os.path.dirname(csv_path) or '.', exist_ok=True)

    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write(';'.join(header) + '\n')
        index = start_index
        for card in cards:
            # image filename only (without path)
            image_filename = os.path.basename(card.image_path) if getattr(card, 'image_path', None) else ''
            row = [
                magazin_name,
                str(index),
                card.kartenname or '',
                image_filename,
                card.edition or '',
                card.kartennummer or '',
                card.sprache or '',
                card.verlag or '',
                card.erscheinungsjahr or '',
                card.region or '',
                card.seltenheit or '',
                card.kartentyp or '',
                card.subtyp or '',
                card.farbe or '',
                card.spezialeffekte or '',
                card.limitierung or '',
                card.autogramm or '',
                card.memorabilia or '',
                card.zustand or '',
                ankaufspreis_default,
                card.marktwert or ''
            ]
            f.write(';'.join(row) + '\n')
            index += 1
