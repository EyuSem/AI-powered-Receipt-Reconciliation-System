import os
import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)

from config import TELEGRAM_TOKEN, IMAGE_FOLDER, OWNER_USERNAME
from ocr import read_image_with_layout
from parser import extract_pos_amount, extract_payment
from receipt_detector import detect_receipt_type
from logic import reconcile
from database import init_db, save_transaction, get_today_summary, get_today_owner_summary, get_today_transactions
from qr_reader import read_qr_code, parse_qr_payment
from report_exporter import export_daily_report



# -----------------------------
# LOGGING
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# -----------------------------
# INIT DATABASE
# -----------------------------
init_db()


# -----------------------------
# CREATE IMAGE FOLDER
# -----------------------------
os.makedirs(IMAGE_FOLDER, exist_ok=True)


# -----------------------------
# USER SESSION MEMORY
# -----------------------------
session = {}


def format_money(value):
    if value is None:
        return "0.00"
    return f"{value:.2f}"


# ==============================
# IMAGE HANDLER
# ==============================
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        user = update.message.from_user.username or str(update.message.from_user.id)

        photo = update.message.photo[-1]

        file = await context.bot.get_file(photo.file_id)

        path = os.path.join(IMAGE_FOLDER, f"{photo.file_id}.jpg")

        await file.download_to_drive(path)

        logger.info(f"Image saved: {path}")

        # -----------------------------
        # OCR
        # -----------------------------
        layout = read_image_with_layout(path)

        text = "\n".join([line["text"] for line in layout])

        logger.info(f"OCR TEXT:\n{text}")

        # -----------------------------
        # RECEIPT TYPE DETECTION
        # -----------------------------
        receipt_type = detect_receipt_type(layout)

        if receipt_type == "UNKNOWN":
            await update.message.reply_text(
                "❌ This image is not a valid POS receipt or payment screenshot."
            )
            return

        # -----------------------------
        # QR DETECTION
        # -----------------------------
        qr_data = read_qr_code(path)

        qr_payment = None

        if qr_data:
            logger.info(f"QR DATA: {qr_data}")
            qr_payment = parse_qr_payment(qr_data)

        # -----------------------------
        # SESSION INIT
        # -----------------------------
        if user not in session:
            session[user] = {}

        # ==============================
        # STEP 1: POS RECEIPT
        # ==============================
        if "pos" not in session[user]:

            if receipt_type != "POS":

                await update.message.reply_text(
                    "⚠️ Please send the POS receipt first."
                )
                return

            pos_amount = extract_pos_amount(text)

            if pos_amount is None:
                await update.message.reply_text(
                    "⚠️ Could not detect POS total.\nPlease send a clearer POS receipt."
                )
                return

            session[user]["pos"] = pos_amount

            await update.message.reply_text(
                f"""
✅ POS receipt saved

POS Total: {format_money(pos_amount)}

Now send the payment screenshot.
"""
            )

            return

        # ==============================
        # STEP 2: PAYMENT SCREENSHOT
        # ==============================
        else:

            if receipt_type != "PAYMENT":

                await update.message.reply_text(
                    "⚠️ Please send a valid payment screenshot."
                )
                return

            payment = extract_payment(text)

            if payment is None:
                payment = {}

            # -----------------------------
            # QR VERIFICATION
            # -----------------------------
            if qr_payment and qr_payment.get("amount"):

                logger.info(f"QR PAYMENT AMOUNT: {qr_payment['amount']}")

                payment["amount"] = qr_payment["amount"]

                if qr_payment.get("transaction_id"):
                    payment["transaction_id"] = qr_payment["transaction_id"]

            if payment.get("amount") is None:

                await update.message.reply_text(
                    "⚠️ Could not detect payment amount.\nPlease send the payment screenshot again."
                )

                return

            pos_amount = session[user]["pos"]

            payment_amount = payment.get("amount")

            # -----------------------------
            # RECONCILIATION
            # -----------------------------
            status, tip = reconcile(
                pos_amount,
                payment_amount,
                payment.get("date")
            )

            # -----------------------------
            # SAVE DATA
            # -----------------------------
            data = {
                "waiter": user,
                "pos_amount": pos_amount,
                "payment_amount": payment_amount,
                "tip": tip,
                "transaction_id": payment.get("transaction_id"),
                "payment_date": payment.get("date"),
                "status": status
            }

            save_transaction(data)

            # Reset session
            session[user] = {}

            # -----------------------------
            # BOT RESPONSE
            # -----------------------------
            await update.message.reply_text(
                f"""
✅ Transaction Saved

Bank: {payment.get("bank", "Unknown")}

POS Total: {format_money(pos_amount)}
Payment: {format_money(payment_amount)}
Tip: {format_money(tip)}

Transaction ID: {payment.get("transaction_id")}
Date: {payment.get("date")}

Status: {status}
"""
            )

    except Exception as e:

        logger.error(f"Error processing image: {e}")

        await update.message.reply_text(
            "❌ Error processing the image. Please try again."
        )


# ==============================
# DAILY REPORT
# ==============================
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):

    summary = get_today_summary()

    await update.message.reply_text(
        f"""
📊 Today Report

Transactions: {summary["transactions"]}

💰 POS Total
{summary["pos_total"]:.2f} ETB

💳 Payments
{summary["payment_total"]:.2f} ETB

🎁 Tips
{summary["tip_total"]:.2f} ETB
"""
    )

async def report_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.username != OWNER_USERNAME:
        await update.message.reply_text("❌ Only the owner can access this report.")
        return

    summary = get_today_owner_summary()

    waiter_text = ""

    for waiter, count in summary["waiters"]:
        waiter_text += f"{waiter} → {count} transactions\n"

    await update.message.reply_text(
        f"""
👑 Owner Daily Report

Transactions: {summary["transactions"]}

💰 POS Sales
{summary["pos_total"]:.2f} ETB

💳 Payments
{summary["payment_total"]:.2f} ETB

🎁 Tips
{summary["tip_total"]:.2f} ETB

⚠️ Issues
Mismatched Transactions: {summary["mismatch"]}

👨‍🍳 Waiter Performance
{waiter_text}
"""
    )

async def close_day(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.username != OWNER_USERNAME:

        await update.message.reply_text(
            "❌ Only the owner can close the day."
        )

        return

    rows = get_today_transactions()

    if not rows:

        await update.message.reply_text(
            "⚠️ No transactions today."
        )

        return

    filename = export_daily_report(rows)

    await update.message.reply_document(
        document=open(filename, "rb"),
        filename=filename,
        caption="📦 Daily financial report"
    )
    
# ==============================
# START BOT
# ==============================
def main():

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("report", report))
    
    app.add_handler(CommandHandler("reportOwner", report_owner))
    
    app.add_handler(CommandHandler("closeDay", close_day))

    app.add_handler(MessageHandler(filters.PHOTO, handle_image))

    logger.info("🚀 Bot running...")

    app.run_polling()


if __name__ == "__main__":
    main()