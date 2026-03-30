import re


# -----------------------------
# OCR TEXT CLEANING
# -----------------------------
def clean_ocr_text(text):

    text = text.replace(";", ",")
    text = text.replace(":", "")
    text = text.replace("O", "0")
    text = text.replace("|", "1")

    text = text.replace("ETB0", "ETB 0")

    return text


# -----------------------------
# AMOUNT NORMALIZATION
# -----------------------------
def normalize_amount(value):

    value = value.replace("$", "").replace("ETB", "").strip()

    if "," in value and "." not in value:
        value = value.replace(",", ".")

    value = value.replace(",", "")

    try:
        return float(value)
    except:
        return None


# -----------------------------
# BANK DETECTION
# -----------------------------
def detect_bank(text):

    text_lower = text.lower()

    if "commercial bank of ethiopia" in text_lower:
        return "CBE"

    if "telebirr" in text_lower:
        return "Telebirr"

    if "awash" in text_lower:
        return "Awash Bank"

    return "Unknown"


# -----------------------------
# POS RECEIPT AMOUNT
# -----------------------------
def extract_pos_amount(text):

    lines = text.split("\n")

    for i, line in enumerate(lines):

        if "total" in line.lower():

            matches = re.findall(r"\d+[.,]\d{2}", line)

            if matches:
                return normalize_amount(matches[-1])

            if i + 1 < len(lines):

                matches = re.findall(r"\d+[.,]\d{2}", lines[i + 1])

                if matches:
                    return normalize_amount(matches[-1])

    matches = re.findall(r"\d+[.,]\d{2}", text)

    values = [normalize_amount(m) for m in matches if normalize_amount(m)]

    if values:
        return max(values)

    return None


# -----------------------------
# PAYMENT AMOUNT
# -----------------------------
def extract_payment_amount(text):

    lines = text.split("\n")

    keywords = [
        "debited",
        "paid",
        "amount",
        "total",
        "transaction amount"
    ]

    amounts = []

    for i, line in enumerate(lines):

        line_lower = line.lower()

        if any(k in line_lower for k in keywords):

            # 1️⃣ Check same line
            matches = re.findall(r"\d+[.,]?\d*\.\d{2}", line)

            for m in matches:
                value = normalize_amount(m)
                if value:
                    amounts.append(value)

            # 2️⃣ Check next line (important for Telebirr)
            if i + 1 < len(lines):

                next_line = lines[i + 1]

                matches = re.findall(r"\d+[.,]?\d*\.\d{2}", next_line)

                for m in matches:
                    value = normalize_amount(m)
                    if value:
                        amounts.append(value)

    if amounts:
        return max(amounts)

    return None


# -----------------------------
# SENDER & RECEIVER
# -----------------------------
def extract_people(text):

    sender = None
    receiver = None

    sender_match = re.search(
        r"debited\s+from\s+([A-Z\s]+)",
        text,
        re.IGNORECASE
    )

    if sender_match:
        sender = sender_match.group(1).strip()

    receiver_match = re.search(
        r"for\s+([A-Z\s]+)",
        text,
        re.IGNORECASE
    )

    if receiver_match:
        receiver = receiver_match.group(1).strip()

    return sender, receiver


# -----------------------------
# TRANSACTION ID
# -----------------------------
def extract_transaction_id(text):

    match = re.search(
        r"(transaction\s*(id|number))[:\s]*([A-Z0-9]+)",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(3)

    return None


# -----------------------------
# DATE
# -----------------------------
def extract_date(text):

    match = re.search(
        r"\d{4}/\d{2}/\d{2}",
        text
    )

    if match:
        return match.group()

    # fallback
    match = re.search(
        r"\d{2}-[A-Za-z]{3}-\d{4}",
        text
    )

    if match:
        return match.group()

    return None


# -----------------------------
# MAIN PAYMENT PARSER
# -----------------------------
def extract_payment(text):

    text = clean_ocr_text(text)

    sender, receiver = extract_people(text)

    payment = {
        "bank": detect_bank(text),
        "amount": extract_payment_amount(text),
        "sender": sender,
        "receiver": receiver,
        "transaction_id": extract_transaction_id(text),
        "date": extract_date(text)
    }

    return payment


# -----------------------------
# QR PAYMENT PARSER
# -----------------------------

def parse_qr_payment(qr_data):

    result = {
        "amount": None,
        "transaction_id": None
    }

    amount_match = re.search(r"\d+\.\d{2}", qr_data)

    if amount_match:
        result["amount"] = float(amount_match.group())

    txn_match = re.search(r"[A-Z0-9]{8,}", qr_data)

    if txn_match:
        result["transaction_id"] = txn_match.group()

    return result