import unicodedata
from pyfiglet import Figlet

def remove_accents(text):
        return ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )

def generate_figlet(title):
    normalized = remove_accents(title)
    custom = Figlet(font='smslant')   # smslant, slant, small, standard
    ascii_title = custom.renderText(normalized)
    lines = ascii_title.splitlines()
    return lines