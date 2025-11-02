import time

class CardData:
    def __init__(self, image_path, kartenname, edition, kartennummer, sprache, verlag, erscheinungsjahr, region, seltenheit, kartentyp, subtyp, farbe, spezialeffekte, limitierung, autogramm, memorabilia, zustand, marktwert, magazin_name: str = 'A', magazin_index: int = 1, processed_at: float = None):
        self.image_path = image_path
        self.kartenname = kartenname
        self.edition = edition
        self.kartennummer = kartennummer
        self.sprache = sprache
        self.verlag = verlag
        self.erscheinungsjahr = erscheinungsjahr
        self.region = region
        self.seltenheit = seltenheit
        self.kartentyp = kartentyp
        self.subtyp = subtyp
        self.farbe = farbe
        self.spezialeffekte = spezialeffekte
        self.limitierung = limitierung
        self.autogramm = autogramm
        self.memorabilia = memorabilia
        self.zustand = zustand
        self.marktwert = marktwert
        self.magazin_name = magazin_name
        self.magazin_index = magazin_index
        self.processed_at = processed_at if processed_at is not None else time.time()
    def __repr__(self):
        return f"CardData({self.image_path}, {self.kartenname}, {self.edition}, {self.kartennummer}, {self.sprache}, {self.verlag}, {self.erscheinungsjahr}, {self.region}, {self.seltenheit}, {self.kartentyp}, {self.subtyp}, {self.farbe}, {self.spezialeffekte}, {self.limitierung}, {self.autogramm}, {self.memorabilia}, {self.zustand}, {self.marktwert}, magazin_name={self.magazin_name}, magazin_index={self.magazin_index}, processed_at={self.processed_at})"
