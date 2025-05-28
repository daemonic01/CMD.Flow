import json
import os
from typing import TYPE_CHECKING
import curses
from utils.date_utils import is_valid_date


if TYPE_CHECKING:
    from core.backend import Projekt, Fazis, Feladat, Reszfeladat

def save_projects_to_file(projektek: list["Projekt"], filename="data.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump([p.to_dict() for p in projektek], f, indent=2, ensure_ascii=False)

def load_projects_from_file(filename="data.json") -> list["Projekt"]:
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
        from core.backend import Projekt
        return [Projekt.from_dict(p) for p in data]





def save_entry_form(stdscr, values, row, projektek, level, parent=None, wait_ms=2000):
    curses.curs_set(0)

    nev = values[0].strip()
    if not nev:
        stdscr.addstr(row + 2, 4, "A név megadása kötelező!", curses.A_BOLD)
        stdscr.refresh()
        curses.napms(wait_ms)
        return {"status": "error", "exit": False}

    hatarido = values[2].strip()
    if hatarido and not is_valid_date(hatarido):
        stdscr.addstr(row + 2, 4, "Hibás formátum (YYYY-MM-DD) vagy múltbéli dátumot adtál meg!", curses.A_BOLD)
        stdscr.refresh()
        curses.napms(wait_ms)
        return {"status": "error", "exit": False}

    entry_data = {
        "nev": nev,
        "leiras": values[1].strip(),
        "hatarido": hatarido,
        "priority": values[3]
    }

    from core.backend import Projekt, Fazis, Feladat, Reszfeladat
    if level == "projekt":
        projektek.append(Projekt(**entry_data))
    elif level == "fazis" and parent:
        parent.fazisok.append(Fazis(**entry_data))
    elif level == "feladat" and parent:
        parent.feladatok.append(Feladat(**entry_data))
    elif level == "reszfeladat" and parent:
        parent.reszfeladatok.append(Reszfeladat(**entry_data))

    save_projects_to_file(projektek)
    stdscr.addstr(row + 2, 4, "Mentés sikeres.", curses.A_BOLD)
    stdscr.refresh()
    curses.napms(wait_ms)

    return {"status": "success", "exit": True}
