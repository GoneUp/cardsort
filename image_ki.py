from gemini_request import GeminiImageDescriber
from carddata import CardData
import re

class CardRecognizer:
    def __init__(self):
        self.prompt = """
        Wir benötigen einen CSV-Eintrag für eine Sammelkarte. 
        Basierern sollte es auf dem Bild der Karte, du kannst aber auch weitere Informationen aus deinem Wissen oder dem Internet hinzuziehen, um die Felder bestmöglich auszufüllen.

        Der Eintrag sollte folgendes Format haben:
        Kartenname;Edition;Kartennummer;Sprache;Verlag;Erscheinungsjahr;Region;Seltenheit;Kartentyp;Subtyp;Farbe;Spezialeffekte;Limitierung;Autogramm;Memorabilia;Zustand;Marktwert

        Hinweise zu den einzelnen Feldern:
        - Kartenname: Der offizielle Name der Karte.
        - Edition: Die Serie oder das Set, zu dem die Karte gehört.
        - Kartennummer: Die Nummer der Karte innerhalb der Edition. Wenn nicht vorhanden, dann versuche die Kartenummer aus deinem Wissen oder dem Internet (ebay oder cardmarket) zu ermitteln. Wenn die Kartennummer einen Schrägstrich enthält, dann ist sie eine Limiterungsnummer und keine Kartennummer. Ignoriere solche Nummern.
        - Sprache: Die Sprache, in der die Karte gedruckt ist.
        - Verlag: Der Herausgeber der Karte.
        - Erscheinungsjahr: Das Jahr, in dem die Karte veröffentlicht wurde. Wenn nicht vorhanden, dann versuche das Erscheinungsjahr aus deinem Wissen oder dem Internet (ebay oder cardmarket) zu ermitteln, mit Hilfe des Kartennamen und der Edition.
        - Region: Das geografische Gebiet, in dem die Karte hauptsächlich verwendet wird.
        - Seltenheit: Die Seltenheitsstufe der Karte (z.B. häufig, selten, ultra-selten).
        - Kartentyp: Die Kategorie der Karte (z.B Kreatur, Zauber, Land).
        - Subtyp: Eine spezifischere Klassifikation innerhalb des Kartentyps.
        - Farbe: Die Farbe(n) der Karte (z.B. Rot, Blau, Mehrfarbig).
        - Spezialeffekte: Besondere Merkmale wie Hologramm, Glitzer, etc.
        - Limitierung: Ob die Karte limitiert ist (z.B. Promo, Sonderedition). Wenn vorhanden, gebe die Nummer der Limitierung in Klammern an. Zum Beispiel "Promo (23/100)".
        - Autogramm: Ob die Karte ein Autogramm eines Künstlers oder Spielers hat.
        - Memorabilia: Ob die Karte ein Stück von etwas Echtem (z.B. Stoff von einem Kostüm) enthält.
        - Zustand: Der physische Zustand der Karte (Nutze diese Skala: Perfekt, Booster Frisch, Leichte Gebrauchspuren, Sichtbare Abnutzung, Starke Abnutzung, Beschädigt, Kaputt). Achte auf Beschädigungen wie Kratzer, Knicke, Abnutzung.
        - Marktwert: Der aktuelle geschätzte Marktwert der Karte basierend auf Verkaufsdaten auf Plattformen wie eBay, TCGPlayer, Cardmarket, etc. Beziehe den Zustand der Karte in deine Bewertung mit ein, ziehe pro Stufe 14,28%% ab. Gib den Wert mit Währung an. 

        Bitte fülle Felder aus, bei denen du unsicher bist oder keine Information hast, mit "unbekannt" aus. 
        Geben nur den CSV-Eintrag zurück, ohne zusätzliche Erklärungen oder Text. Gib nicht das definierte CSV-Format zurück, nur den CSV-Eintrag. 
        Verwende in den Felder keine Semikolons. 
        """
        self.describer = GeminiImageDescriber()
    def recognize(self, image_path):
        description = self.describer.describe_image(image_path, prompt=self.prompt)
        print("GeminiImageDescriber: Return: " + str(description))
        # Parse CSV string into CardData
        fields = re.split(r';', description.strip())
        # Pad missing fields with 'unbekannt'
        while len(fields) < 17:
            fields.append('unbekannt')
        return CardData(image_path, *fields[:17])

# Example usage:
# recognizer = CardRecognizer()
# card = recognizer.recognize('samples/test.jpg')
# print(card)
