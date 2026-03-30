import csv
from datetime import datetime

try:
    from openpyxl import Workbook
    has_openpyxl = True
except ImportError:
    Workbook = None
    has_openpyxl = False


def export_daily_report(rows):
    today = datetime.now().strftime("%Y_%m_%d")

    if has_openpyxl and Workbook is not None:
        filename = f"daily_report_{today}.xlsx"

        wb = Workbook()
        ws = wb.active
        ws.title = "Daily Report"

        # Header
        ws.append([
            "Waiter",
            "POS Amount",
            "Payment Amount",
            "Tip",
            "Transaction ID",
            "Status",
            "Time"
        ])

        pos_total = 0
        payment_total = 0
        tip_total = 0

        for r in rows:
            waiter, pos, payment, tip, txn, status, time = r

            pos_total += pos or 0
            payment_total += payment or 0
            tip_total += tip or 0

            ws.append([
                waiter,
                pos,
                payment,
                tip,
                txn,
                status,
                time
            ])

        # totals row
        ws.append([])
        ws.append(["TOTAL", pos_total, payment_total, tip_total])

        wb.save(filename)

        return filename

    # fallback to CSV export
    filename = f"daily_report_{today}.csv"

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Waiter",
            "POS Amount",
            "Payment Amount",
            "Tip",
            "Transaction ID",
            "Status",
            "Time"
        ])

        pos_total = 0
        payment_total = 0
        tip_total = 0

        for r in rows:
            waiter, pos, payment, tip, txn, status, time = r

            pos_total += pos or 0
            payment_total += payment or 0
            tip_total += tip or 0

            writer.writerow([waiter, pos, payment, tip, txn, status, time])

        writer.writerow([])
        writer.writerow(["TOTAL", pos_total, payment_total, tip_total])

    return filename