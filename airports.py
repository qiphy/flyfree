AIRPORTS = {
    "KUL": {"name": "Kuala Lumpur International", "city": "Kuala Lumpur", "state": "Selangor"},
    "SZB": {"name": "Sultan Abdul Aziz Shah", "city": "Subang", "state": "Selangor"},
    "PEN": {"name": "Penang International", "city": "Penang", "state": "Penang"},
    "BKI": {"name": "Kota Kinabalu International", "city": "Kota Kinabalu", "state": "Sabah"},
    "KCH": {"name": "Kuching International", "city": "Kuching", "state": "Sarawak"},
    "JHB": {"name": "Senai International", "city": "Johor Bahru", "state": "Johor"},
    "LGK": {"name": "Langkawi International", "city": "Langkawi", "state": "Kedah"},
    "TGG": {"name": "Sultan Mahmud", "city": "Kuala Terengganu", "state": "Terengganu"},
    "KUA": {"name": "Sultan Haji Ahmad Shah", "city": "Kuantan", "state": "Pahang"},
    "KBR": {"name": "Sultan Ismail Petra", "city": "Kota Bharu", "state": "Kelantan"},
    "IPH": {"name": "Sultan Azlan Shah", "city": "Ipoh", "state": "Perak"},
    "SDK": {"name": "Sandakan", "city": "Sandakan", "state": "Sabah"},
    "TWU": {"name": "Tawau", "city": "Tawau", "state": "Sabah"},
    "MYY": {"name": "Miri", "city": "Miri", "state": "Sarawak"},
    "SBU": {"name": "Sibu", "city": "Sibu", "state": "Sarawak"},
    "MKM": {"name": "Mukah", "city": "Mukah", "state": "Sarawak"},
    "MLG": {"name": "Malacca", "city": "Malacca", "state": "Malacca"},
}

# Route pairs with scheduled domestic service
DOMESTIC_ROUTES = [
    # Peninsula hub routes from KUL
    ("KUL", "PEN"), ("KUL", "JHB"), ("KUL", "LGK"), ("KUL", "TGG"),
    ("KUL", "KUA"), ("KUL", "KBR"), ("KUL", "IPH"),
    # Peninsula hub routes from SZB (Firefly, Batik Air)
    ("SZB", "PEN"), ("SZB", "JHB"), ("SZB", "LGK"), ("SZB", "KBR"),
    ("SZB", "TGG"), ("SZB", "KUA"), ("SZB", "IPH"),
    # East Malaysia hub routes from KUL
    ("KUL", "BKI"), ("KUL", "KCH"), ("KUL", "SDK"), ("KUL", "TWU"),
    ("KUL", "MYY"), ("KUL", "SBU"),
    # East Malaysia from SZB
    ("SZB", "BKI"), ("SZB", "KCH"),
    # East Malaysia inter-Borneo routes
    ("BKI", "KCH"), ("BKI", "MYY"), ("BKI", "SBU"), ("BKI", "SDK"),
    ("BKI", "TWU"), ("BKI", "MKM"),
    ("KCH", "MYY"), ("KCH", "SBU"), ("KCH", "BKI"),
    ("MYY", "SBU"), ("MYY", "BKI"),
    # Peninsula cross-routes
    ("PEN", "JHB"), ("PEN", "LGK"), ("PEN", "BKI"),
    ("JHB", "KCH"), ("JHB", "BKI"),
    ("LGK", "PEN"),
]
