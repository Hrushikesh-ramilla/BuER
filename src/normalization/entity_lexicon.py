"""Multi-jurisdictional legal entity and address vocabulary lexicons."""
from typing import Set

# Indian corporate suffixes and filler tokens
INDIAN_CORPORATE_LEXICON: Set[str] = {
    'pvt', 'private', 'ltd', 'limited', 'llp', 'opc', 'co', 'company',
    'corp', 'corporation', 'inc', 'enterprises', 'enterprise', 'services',
    'solutions', 'technologies', 'technology', 'group', 'industries',
    'shree', 'shri', 'sri', 'india', 'and', 'the', 'm/s', 'trading'
}

# United States corporate forms and standard abbreviations
US_CORPORATE_LEXICON: Set[str] = {
    'inc', 'incorporated', 'corp', 'corporation', 'llc', 'ltd', 'limited',
    'pllc', 'co', 'company', 'pc', 'group', 'holdings', 'services',
    'management', 'enterprises', 'associates', 'partners', 'lp'
}

# French legal business structures
FRENCH_CORPORATE_LEXICON: Set[str] = {
    'sa', 'sas', 'sasu', 'sarl', 'eurl', 'sci', 'scp', 'snc', 'se',
    'groupe', 'developpement', 'fils', 'et', 'france', 'associes',
    'cie', 'compagnie', 'societe', 'club', 'section', 'comite'
}

# Combined global filler tokens
ALL_CORPORATE_FILLER: Set[str] = INDIAN_CORPORATE_LEXICON | US_CORPORATE_LEXICON | FRENCH_CORPORATE_LEXICON

# Standard address abbreviation expansions
ADDRESS_EXPANSIONS = {
    'rd': 'road',
    'st': 'street',
    'ave': 'avenue',
    'blvd': 'boulevard',
    'dr': 'drive',
    'ln': 'lane',
    'ct': 'court',
    'pl': 'place',
    'sq': 'square',
    'hwy': 'highway',
    'pkwy': 'parkway',
    'ste': 'suite',
    'apt': 'apartment',
    'fl': 'floor',
    'bldg': 'building'
}
