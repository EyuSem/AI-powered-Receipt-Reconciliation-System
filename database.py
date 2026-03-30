import sqlite3
from config import DB_PATH


def init_db():

    import sqlite3

    conn = sqlite3.connect("transactions.db")

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        waiter TEXT,

        pos_amount REAL,

        payment_amount REAL,

        tip REAL,

        transaction_id TEXT,

        payment_date TEXT,

        status TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()

    conn.close()
    

def save_transaction(data):

    conn = sqlite3.connect("transactions.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO transactions
    (waiter, pos_amount, payment_amount, tip, transaction_id, payment_date, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data["waiter"],
        data["pos_amount"],
        data["payment_amount"],
        data["tip"],
        data["transaction_id"],
        data["payment_date"],
        data["status"]
    ))

    conn.commit()
    conn.close()
    
    print("Transaction saved:", data)


def get_daily_summary():

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
        SELECT 
            COUNT(*),
            SUM(pos_amount),
            SUM(payment_amount),
            SUM(tip)
        FROM transactions
        """)

        result = cursor.fetchone()

    return {
        "transactions": result[0] or 0,
        "pos_total": result[1] or 0,
        "payments_total": result[2] or 0,
        "tips_total": result[3] or 0
    }


def get_owner_summary():

    conn = sqlite3.connect("transactions.db")
    cursor = conn.cursor()

    # totals
    cursor.execute("""
        SELECT 
            COUNT(*),
            SUM(pos_amount),
            SUM(payment_amount),
            SUM(tip)
        FROM transactions
    """)

    result = cursor.fetchone()

    transactions = result[0] or 0
    pos_total = result[1] or 0
    payment_total = result[2] or 0
    tip_total = result[3] or 0

    # mismatches
    cursor.execute("""
        SELECT COUNT(*)
        FROM transactions
        WHERE status != 'OK'
    """)

    mismatch = cursor.fetchone()[0]

    # waiter performance
    cursor.execute("""
        SELECT waiter, COUNT(*)
        FROM transactions
        GROUP BY waiter
    """)

    waiters = cursor.fetchall()

    conn.close()

    return {
        "transactions": transactions,
        "pos_total": pos_total,
        "payment_total": payment_total,
        "tip_total": tip_total,
        "mismatch": mismatch,
        "waiters": waiters
    }
import sqlite3


# -----------------------------
# TODAY WAITER REPORT
# -----------------------------
def get_today_summary():

    conn = sqlite3.connect("transactions.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            COUNT(*),
            SUM(pos_amount),
            SUM(payment_amount),
            SUM(tip)
        FROM transactions
        WHERE DATE(created_at) = DATE('now')
    """)

    result = cursor.fetchone()

    conn.close()

    return {
        "transactions": result[0] or 0,
        "pos_total": result[1] or 0,
        "payment_total": result[2] or 0,
        "tip_total": result[3] or 0
    }


# -----------------------------
# TODAY OWNER REPORT
# -----------------------------
def get_today_owner_summary():

    conn = sqlite3.connect("transactions.db")
    cursor = conn.cursor()

    # totals
    cursor.execute("""
        SELECT 
            COUNT(*),
            SUM(pos_amount),
            SUM(payment_amount),
            SUM(tip)
        FROM transactions
        WHERE DATE(created_at) = DATE('now')
    """)

    result = cursor.fetchone()

    transactions = result[0] or 0
    pos_total = result[1] or 0
    payment_total = result[2] or 0
    tip_total = result[3] or 0

    # mismatches
    cursor.execute("""
        SELECT COUNT(*)
        FROM transactions
        WHERE status != 'OK'
        AND DATE(created_at) = DATE('now')
    """)

    mismatch = cursor.fetchone()[0]

    # waiter performance
    cursor.execute("""
        SELECT waiter, COUNT(*)
        FROM transactions
        WHERE DATE(created_at) = DATE('now')
        GROUP BY waiter
    """)

    waiters = cursor.fetchall()

    conn.close()

    return {
        "transactions": transactions,
        "pos_total": pos_total,
        "payment_total": payment_total,
        "tip_total": tip_total,
        "mismatch": mismatch,
        "waiters": waiters
    }

def get_today_transactions():

    import sqlite3

    conn = sqlite3.connect("transactions.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT waiter, pos_amount, payment_amount, tip, transaction_id, status, created_at
        FROM transactions
        WHERE DATE(created_at) = DATE('now')
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows