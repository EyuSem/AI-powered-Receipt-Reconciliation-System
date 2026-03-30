def detect_receipt_type(layout_lines):

    text_all = " ".join([l["text"] for l in layout_lines]).lower()

    # remove OCR punctuation noise
    text_all = text_all.replace(";", " ").replace(":", " ")

    # -----------------------------
    # PAYMENT SCREENSHOT DETECTION
    # -----------------------------
    payment_keywords = [
        "transaction",
        "transaction id",
        "transaction number",
        "transaction to",
        "your transaction Verfication is successful",
        "finished",
        "debited",
        "credited",
        "telebirr",
        "commercial bank",
        "bank of ethiopia",
        "transaction id",
        "trx id",
        "payment successful",
        "etb"
    ]

    payment_score = 0

    for k in payment_keywords:
        if k in text_all:
            payment_score += 1

    if payment_score >= 2:
        return "PAYMENT"

    # -----------------------------
    # POS RECEIPT DETECTION
    # -----------------------------
    pos_keywords = [
        "total",
        "vat",
        "receipt",
        "cashier",
        "pos",
        "amount",
        "subtotal", 
        "item",
        "qty",
        "price", 
        "cash"
    ]

    pos_score = 0

    for k in pos_keywords:
        if k in text_all:
            pos_score += 1

    if pos_score >= 1:
        return "POS"

    # -----------------------------
    # UNKNOWN
    # -----------------------------
    return "UNKNOWN"