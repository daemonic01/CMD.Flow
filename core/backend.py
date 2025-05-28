from utils.data_io import load_projects_from_file, save_projects_to_file
from datetime import date

# --- Osztályok ---

class Reszfeladat:
    _id_counter = 1

    def __init__(
        self,
        nev: str,
        kesz: bool = False,
        id: int = None,
        letrehozas_datum: str = None,
        hatarido: str = "",
        leiras: str = ""
    ):
        self.id = id or Reszfeladat._id_counter
        Reszfeladat._id_counter = max(Reszfeladat._id_counter, self.id + 1)
        self.nev = nev
        self.kesz = kesz

        # New metadata fields
        self.letrehozas_datum = letrehozas_datum or date.today().isoformat()
        self.hatarido = hatarido
        self.leiras = leiras

    def toggle(self):
        self.kesz = not self.kesz

    def to_dict(self):
        return {
            "id": self.id,
            "nev": self.nev,
            "kesz": self.kesz,
            "letrehozas_datum": self.letrehozas_datum,
            "hatarido": self.hatarido,
            "leiras": self.leiras
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            nev=data["nev"],
            kesz=data.get("kesz", False),
            id=data.get("id"),
            letrehozas_datum=data.get("letrehozas_datum", date.today().isoformat()),
            hatarido=data.get("hatarido", ""),
            leiras=data.get("leiras", "")
        )


class Feladat:
    _id_counter = 1

    def __init__(self, nev: str, id: int = None, letrehozas_datum: str = None, hatarido: str = "", leiras: str = ""):
        self.id = id or Feladat._id_counter
        Feladat._id_counter = max(Feladat._id_counter, self.id + 1)
        self.nev = nev
        self.reszfeladatok: list[Reszfeladat] = []

        # New metadata fields
        self.letrehozas_datum = letrehozas_datum or date.today().isoformat()
        self.hatarido = hatarido
        self.leiras = leiras

    def add_reszfeladat(self, nev: str):
        self.reszfeladatok.append(Reszfeladat(nev))

    def progress(self) -> int:
        if not self.reszfeladatok:
            return 0
        keszek = sum(1 for r in self.reszfeladatok if r.kesz)
        return int((keszek / len(self.reszfeladatok)) * 100)

    def get_reszfeladat_by_id(self, id: int):
        return next((r for r in self.reszfeladatok if r.id == id), None)

    def to_dict(self):
        return {
            "id": self.id,
            "nev": self.nev,
            "letrehozas_datum": self.letrehozas_datum,
            "hatarido": self.hatarido,
            "leiras": self.leiras,
            "reszfeladatok": [r.to_dict() for r in self.reszfeladatok]
        }

    def remove_reszfeladat(self, reszfeladat):
        if reszfeladat in self.reszfeladatok:
            self.reszfeladatok.remove(reszfeladat)

    @classmethod
    def from_dict(cls, data):
        f = cls(
            nev=data["nev"],
            id=data.get("id"),
            letrehozas_datum=data.get("letrehozas_datum", date.today().isoformat()),
            hatarido=data.get("hatarido", ""),
            leiras=data.get("leiras", "")
        )
        f.reszfeladatok = [Reszfeladat.from_dict(r) for r in data.get("reszfeladatok", [])]
        return f




    @classmethod
    def from_dict(cls, data):
        f = cls(data["nev"], data["id"])
        f.reszfeladatok = [Reszfeladat.from_dict(r) for r in data["reszfeladatok"]]
        return f


class Fazis:
    _id_counter = 1

    def __init__(self, nev: str, id: int = None, letrehozas_datum: str = None, hatarido: str = "", leiras: str = ""):
        self.id = id or Fazis._id_counter
        Fazis._id_counter = max(Fazis._id_counter, self.id + 1)
        self.nev = nev
        self.feladatok: list[Feladat] = []

        # New metadata fields
        self.letrehozas_datum = letrehozas_datum or date.today().isoformat()
        self.hatarido = hatarido
        self.leiras = leiras

    def add_feladat(self, nev: str):
        self.feladatok.append(Feladat(nev))

    def progress(self) -> int:
        if not self.feladatok:
            return 0
        return int(sum(f.progress() for f in self.feladatok) / len(self.feladatok))

    def get_feladat_by_id(self, id: int):
        return next((f for f in self.feladatok if f.id == id), None)

    def to_dict(self):
        return {
            "id": self.id,
            "nev": self.nev,
            "letrehozas_datum": self.letrehozas_datum,
            "hatarido": self.hatarido,
            "leiras": self.leiras,
            "feladatok": [f.to_dict() for f in self.feladatok]
        }

    def remove_feladat(self, feladat):
        if feladat in self.feladatok:
            self.feladatok.remove(feladat)

    @classmethod
    def from_dict(cls, data):
        fazis = cls(
            nev=data["nev"],
            id=data.get("id"),
            letrehozas_datum=data.get("letrehozas_datum", date.today().isoformat()),
            hatarido=data.get("hatarido", ""),
            leiras=data.get("leiras", "")
        )
        fazis.feladatok = [Feladat.from_dict(f) for f in data.get("feladatok", [])]
        return fazis


class Projekt:
    _id_counter = 1

    def __init__(self, nev: str, id: int = None, letrehozas_datum: str = None, hatarido: str = "", leiras: str = "", priority: int = 1, status: bool = False):
        self.id = id or Projekt._id_counter
        Projekt._id_counter = max(Projekt._id_counter, self.id + 1)
        self.nev = nev
        self.fazisok: list[Fazis] = []
        self.letrehozas_datum = letrehozas_datum or date.today().isoformat()
        self.hatarido = hatarido  # Optional deadline (YYYY-MM-DD or empty)
        self.leiras = leiras      # Optional description
        self.priority = priority
        self.status = status

    def add_fazis(self, nev: str):
        self.fazisok.append(Fazis(nev))

    def progress(self) -> int:
        if not self.fazisok:
            return 0
        return int(sum(f.progress() for f in self.fazisok) / len(self.fazisok))

    def get_fazis_by_id(self, id: int):
        return next((f for f in self.fazisok if f.id == id), None)

    def to_dict(self):
        return {
            "id": self.id,
            "nev": self.nev,
            "letrehozas_datum": self.letrehozas_datum,
            "hatarido": self.hatarido,
            "leiras": self.leiras,
            "priotiry": self.priority,
            "fazisok": [f.to_dict() for f in self.fazisok]
        }

    def is_empty(self):
        return len(self.fazisok) == 0

    def remove_fazis(self, fazis):
        if fazis not in self.fazisok:
            print("Fázis nem található.")
            return

        if fazis.feladatok:
            print(f"A fázis '{fazis.nev}' nem üres.")
            return

        self.fazisok.remove(fazis)

    @classmethod
    def from_dict(cls, data):
        projekt = cls(
            nev=data["nev"],
            id=data.get("id"),
            letrehozas_datum=data.get("letrehozas_datum", date.today().isoformat()),
            hatarido=data.get("hatarido", ""),
            leiras=data.get("leiras", "")
        )
        projekt.fazisok = [Fazis.from_dict(f) for f in data.get("fazisok", [])]
        return projekt







# --- Segédfüggvények ---
def print_struktura(projektek: list[Projekt]):
    for p in projektek:
        print(f"Projekt: {p.nev} (#{p.id}) - {p.progress()}%")
        for fazis in p.fazisok:
            print(f"  Fázis: {fazis.nev} (#{fazis.id}) - {fazis.progress()}%")
            for feladat in fazis.feladatok:
                print(f"    Feladat: {feladat.nev} (#{feladat.id}) - {feladat.progress()}%")
                for resz in feladat.reszfeladatok:
                    status = "[x]" if resz.kesz else "[ ]"
                    print(f"      {status} {resz.nev} (#{resz.id})")

def remove_projekt_by_id(projektek: list[Projekt], id: int) -> list[Projekt]:
    [p for p in projektek if p.id != id]




# --- Interaktív parancskezelés ---
def toggle_reszfeladat_interaktiv(projektek):
    try:
        pid = int(input("Projekt ID: "))
        projekt = next((p for p in projektek if p.id == pid), None)
        if not projekt:
            print("Nincs ilyen projekt.")
            return

        fazid = int(input("  Fázis ID: "))
        fazis = projekt.get_fazis_by_id(fazid)
        if not fazis:
            print("  Nincs ilyen fázis.")
            return

        fid = int(input("    Feladat ID: "))
        feladat = fazis.get_feladat_by_id(fid)
        if not feladat:
            print("    Nincs ilyen feladat.")
            return

        rid = int(input("      Részfeladat ID: "))
        resz = feladat.get_reszfeladat_by_id(rid)
        if not resz:
            print("      Nincs ilyen részfeladat.")
            return

        resz.toggle()
        print("      Részfeladat állapota megváltozott.")
    except ValueError:
        print("Hibás bemenet.")


# --- Main függvény ---

def main():
    projektek = load_projects_from_file()

    while True:
        print("\n--- CMD.Flow ---")
        print("Parancsok: add | list | delete | toggle | save | exit")
        parancs = input(">>> ").strip().lower()

        # --- Listázás ---
        if parancs == "list":
            print_struktura(projektek)

        # --- Részfeladat kapcsolás ---
        elif parancs == "toggle":
            toggle_reszfeladat_interaktiv(projektek)

        # --- Adatok mentése ---
        elif parancs == "save":
            save_projects_to_file(projektek)
            print("Mentve.")
        
        # --- Kilépés ---
        elif parancs == "exit":
            print("Kilépés...")
            break

        # --- Új egység hozzáadása ---
        elif parancs.startswith("add"):
            alparancs = parancs.split()
            if len(alparancs) < 2:
                print("Pontosan add mit?")
                continue

            tipus = alparancs[1]

            if tipus == "projekt":
                nev = input("Projekt neve: ")
                projektek.append(Projekt(nev))

            elif tipus == "fazis":
                pid = int(input("Projekt ID: "))
                projekt = next((p for p in projektek if p.id == pid), None)
                if projekt:
                    nev = input("Fázis neve: ")
                    projekt.add_fazis(nev)


            elif tipus == "feladat":
                pid = int(input("Projekt ID: "))
                projekt = next((p for p in projektek if p.id == pid), None)
                if projekt:
                    fid = int(input("Fázis ID: "))
                    fazis = projekt.get_fazis_by_id(fid)
                    if fazis:
                        nev = input("Feladat neve: ")
                        fazis.add_feladat(nev)
                    else:
                        print("Nincs ilyen fázis.")
                else:
                    print("Nincs ilyen projekt.")

            elif tipus == "reszfeladat":
                pid = int(input("Projekt ID: "))
                projekt = next((p for p in projektek if p.id == pid), None)
                if projekt:
                    fid = int(input("Fázis ID: "))
                    fazis = projekt.get_fazis_by_id(fid)
                    if fazis:
                        felid = int(input("Feladat ID: "))
                        feladat = fazis.get_feladat_by_id(felid)
                        if feladat:
                            nev = input("Részfeladat neve: ")
                            feladat.add_reszfeladat(nev)
                        else:
                            print("Nincs ilyen feladat.")
                    else:
                        print("Nincs ilyen fázis.")
                else:
                    print("Nincs ilyen projekt.")

            else:
                print("Ismeretlen add-típus.")

        # --- Egység törlése ---
        elif parancs.startswith("delete"):
            alparancs = parancs.split()
            if len(alparancs) < 2:
                print("Pontosan delete mit?")
                continue

            tipus = alparancs[1]

            if tipus == "projekt":
                pid = int(input("Projekt ID: "))
                projekt = next((p for p in projektek if p.id == pid), None)
                if projekt:
                    if projekt.fazisok:
                        valasz = input(f"A(z) '{projekt.nev}' projekt nem üres. Törlöd? (i/n): ").lower()
                        if valasz != "i":
                            print("Törlés megszakítva.")
                            continue
                    projektek = [p for p in projektek if p.id != pid]
                    print("Projekt törölve.")
                else:
                    print("Nincs ilyen projekt.")

            elif tipus == "fazis":
                pid = int(input("Projekt ID: "))
                projekt = next((p for p in projektek if p.id == pid), None)
                if projekt:
                    fid = int(input("Fázis ID: "))
                    projekt.remove_fazis_by_id(fid)

            elif tipus == "feladat":
                pid = int(input("Projekt ID: "))
                projekt = next((p for p in projektek if p.id == pid), None)
                if projekt:
                    fazid = int(input("Fázis ID: "))
                    fazis = projekt.get_fazis_by_id(fazid)
                    if fazis:
                        felid = int(input("Feladat ID: "))
                        fazis.remove_feladat_by_id(felid)

            elif tipus == "reszfeladat":
                pid = int(input("Projekt ID: "))
                projekt = next((p for p in projektek if p.id == pid), None)
                if projekt:
                    fazid = int(input("Fázis ID: "))
                    fazis = projekt.get_fazis_by_id(fazid)
                    if fazis:
                        felid = int(input("Feladat ID: "))
                        feladat = fazis.get_feladat_by_id(felid)
                        if feladat:
                            rid = int(input("Részfeladat ID: "))
                            feladat.remove_reszfeladat_by_id(rid)

            else:
                print("Ismeretlen delete-típus.")

        else:
            print("Ismeretlen parancs.")


if __name__ == "__main__":
    main()
