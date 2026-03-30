from datetime import datetime


def fix_pos_amount(amount):

    if amount is None:
        return None

    # If OCR reads 49530 instead of 495.30
    if amount > 10000:
        amount = amount / 100

    return amount


def reconcile(pos_amount, payment_amount, payment_date):

    pos_amount = fix_pos_amount(pos_amount)

    if pos_amount is None:
        return "POS_NOT_FOUND ❌ ", 0

    if payment_amount is None:
        return "PAYMENT_NOT_FOUND ❌ ", 0

    if payment_amount < pos_amount:
        return "UNDERPAID ❌ ", 0

    tip = payment_amount - pos_amount

    today = datetime.today().strftime("%d-%b-%Y")

    if payment_date and payment_date != today:
        return "DATE_MISMATCH ❌", tip

    return "OK", tip