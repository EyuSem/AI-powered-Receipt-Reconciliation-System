def detect_bank(text):

    if "commercial bank" in text.lower():
        return "CBE"

    if "dashen" in text.lower():
        return "Dashen"

    if "telebirr" in text.lower():
        return "Telebirr"

    return "Unknown"