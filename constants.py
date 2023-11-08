# Pirst step, get each bulletin's XML
BASE_URL = 'https://boe.es/diario_boe/xml.php?id=BOE-S-'

# Second step, extract each item's XML from the bulletin
SPECIFIC_URL = 'https://boe.es/diario_boe/xml.php?id='          # expected something like 'BOE-S-20231101' after ?id=


ITEM_LIST = []