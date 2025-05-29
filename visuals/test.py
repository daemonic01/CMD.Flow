import pyfiglet
from pyfiglet import Figlet


custom = Figlet(font='cybermedium')
fig = custom.renderText("Stonebirth")
#print(fig)


import unicodedata

def remove_accents(text):
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

from pyfiglet import Figlet
f = Figlet(font='slant')
text = 'árok'
text_ascii = remove_accents(text)
print(f.renderText(text_ascii))