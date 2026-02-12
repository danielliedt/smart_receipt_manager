# Configuration for hardcoded categorization rules
# Order matters: more specific terms should come first

STORES = [
    "Lidl", "Aldi", "Rewe", "Edeka", "Kaufland", 
    "Netto", "Penny", "Norma", "Metro"
]

# Keywords that trigger immediate deletion of the pending name buffer
JUNK_KEYWORDS = [
    "tel.", "telefon", "fax", "steuernummer", "uid", "ust-id", "st-nr",
    "straße", "str.", "platz", "weg", "damm", "allee", 
    "gmbh", "kundenhotline", "markt", "summe", "betrag", "gegeben", 
    "rückgeld", "ec-karte", "bar", "eur", "quittung", "beleg", "datum"
]

# Short names for store identification to avoid inclusion in item names
STORE_SHORT_NAMES = ["edeka", "lidl", "aldi", "rewe", "kaufland", "netto", "penny"]

CATEGORIES = [
    "Energy Drinks", "Beverages", "Alcoholic Beverages",
    "Fresh Produce", "Dairy & Eggs", "Meat & Fish",
    "Pantry & Cooking", "Breakfast & Bakery", "Frozen Food",
    "Sweets & Snacks", "Cleaning", "Personal Care & Health",
    "Pet Supplies", "Financials", "Others(Hardware,Hobby,One-time purchase)", "Miscellaneous"
]

# Mapping keywords to categories
# If a keyword is found, the category is assigned immediately
HARDCODED_RULES = {
    "Financials": ["discount", "rabatt", "aktion", "pfand", "coupon", "gutschrift"],
    
    "Energy Drinks": ["monster", "red bull", "rockstar", "reign", "effect", "kong strong"],
    
    "Cleaning": [
        "scheuer", "reiniger", "putz", "wc", "spül", "wasch", "tasc", 
        "müll", "beutel", "folie", "küchenroll"
    ],
    
    "Others(Hardware,Hobby,One-time purchase)": [
        "brikett", "kohle", "batterie", "kerze", "feuerzeug", "grill", "hobby", "werkzeug", "Papiertrag"
    ],

    "Frozen Food": ["tk ", "tiefk", "pizza", "pomm", "eis ", "wellenschnitt", "iglo", "mccain"],
    
    "Dairy & Eggs": ["käse", "quark", "joghurt", "sahne", "schmand", "butter", "ei ", "eier", "frischmilch", "h-milch"],
    
    "Meat & Fish": ["wurst", "schinken", "salami", "fleisch", "hack", "chick", "hähnchen", "pute", "lachs", "thunfisch"],
    
    "Fresh Produce": ["ingwer", "bio", "lose", "apfel", "banane", "gurke", "tomate fresh", "salat"],
    
    "Beverages": ["wasser", "water", "cola", "fanta", "sprite", "limo", "saft", "nektar", "schorle", "drink", "kaffee", "tee"],
    
    "Sweets & Snacks": ["schoko", "keks", "gummi", "bonbon", "riegel", "hanuta", "chips", "nüsse", "snack"],
    
    "Pantry & Cooking": ["nudeln", "pasta", "fusilli", "reis", "mehl", "zucker", "salz", "ketchup", "senf", "mayo", "öl", "essig", "konserve", "dose", "glas"],
}

# Specific overrides for ambiguous terms
FALSE_FRIENDS = {
    "scheuermilch": "Household & Cleaning",
    "reinigungsmilch": "Personal Care & Health",
    "eisspray": "Personal Care & Health",
    "karosseriebutter": "Miscellaneous",
    "oetk.": "Pantry & Cooking",
}
