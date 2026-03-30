# 🤖 AI-powered Receipt Reconciliation System

An intelligent, AI-driven system that automates restaurant payment verification by extracting, analyzing, and reconciling POS receipts and digital payment screenshots.

This project combines Optical Character Recognition (OCR), QR code detection, and transaction logic to reduce fraud, improve financial accuracy, and streamline daily restaurant operations.

---

## 📌 Overview

In many restaurants, payment verification is manual and error-prone. Staff may submit incorrect or even fake payment screenshots, leading to financial loss.

This system solves that problem by:

* Automatically extracting data from receipts and payment screenshots
* Verifying transaction consistency
* Detecting mismatches or suspicious activity
* Generating daily operational reports

---

## 🚀 Key Features

### 📄 Receipt Processing

* Extracts total amounts from POS receipts using OCR
* Handles noisy and low-quality images
* Supports multiple receipt formats

### 💳 Payment Verification

* Parses mobile banking and digital payment screenshots
* Detects transaction amount, ID, and date
* Supports Ethiopian payment systems (e.g., Telebirr, CBE)

### 🔍 QR Code Validation

* Reads QR codes from payment screenshots
* Extracts embedded transaction data
* Uses QR data to override unreliable OCR results

### ⚖️ Smart Reconciliation

* Compares POS amount vs payment amount
* Calculates tips automatically
* Detects mismatches and anomalies

### 📊 Reporting System

* Daily transaction summaries
* Owner-level(cashier) financial reports
* Waiter performance tracking

### 🤖 Telegram Bot Interface

* Easy-to-use chat-based interaction
* Real-time processing
* Works on any device via Telegram

---

## 🧠 System Architecture

```text
User (Telegram)
        ↓
   Image Upload
        ↓
   OCR Engine (PaddleOCR)
        ↓
   Receipt Type Detection
        ↓
   Data Extraction (POS / Payment)
        ↓
   QR Code Verification
        ↓
   Reconciliation Logic
        ↓
   Database Storage (SQLite)
        ↓
   Reports & Analytics
```

---

## 🛠️ Technologies Used

* **Python** – Core programming language
* **PaddleOCR** – AI-based text recognition
* **OpenCV** – Image preprocessing and enhancement
* **Pyzbar** – QR code detection
* **SQLite** – Lightweight database
* **python-telegram-bot** – Bot interaction layer

---

## 📂 Project Structure

```text
AI-powered-Receipt-Reconciliation-System/
│
├── bot.py                  # Telegram bot controller
├── parser.py               # Data extraction logic
├── ocr.py                  # OCR processing (PaddleOCR)
├── qr_reader.py            # QR code detection & parsing
├── receipt_detector.py     # Receipt classification (POS / Payment)
├── logic.py                # Reconciliation logic
├── database.py             # Database operations
├── report_exporter.py      # Excel/CSV report generation
├── config.py               # Environment configuration
├── requirements.txt        # Dependencies
├── assets/                 # Images, demo GIFs
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/EyuSem/AI-powered-Receipt-Reconciliation-System.git
cd AI-powered-Receipt-Reconciliation-System
```

---

### 2. Create Virtual Environment (Recommended)

```bash
conda create -n receiptAI python=3.10
conda activate receiptAI
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create a `.env` file:

```env
TELEGRAM_TOKEN=your_telegram_bot_token
OWNER_USERNAME=your_telegram_username
```
or edit the config.py file add token and username.

---

### 5. Run the Bot

```bash
python bot.py
```

---

## 📸 Example Workflow

1. User sends a POS receipt image
2. Bot extracts total amount
3. User sends payment screenshot
4. System verifies and reconciles
5. Bot returns result with status and tip

---

## 📈 Use Cases

* Restaurants and cafes
* Hotels and hospitality businesses
* Fraud detection systems
* Financial auditing automation

---

## 🔒 Security Considerations

* Sensitive data (tokens) stored via environment variables
* No private data uploaded to repository
* Local database storage for privacy

---

## 🌟 Future Improvements

* Web dashboard for real-time monitoring and ERP system integrations 
* Machine learning fraud detection model
* Multi-branch restaurant support
* Cloud deployment (AWS / GCP)
* Mobile app integration

---

## 👤 Author

**Eyuel Semeon**
email: eyuel.semeon@gmail.com

---

---

## 📜 License

This project is open-source and available under the MIT License.

---

## ⭐ Support

If you find this project useful, consider giving it a ⭐ on GitHub!

---
