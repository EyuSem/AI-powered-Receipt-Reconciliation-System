import cv2
import re
from pyzbar.pyzbar import decode


# -----------------------------
# IMAGE PREPROCESSING
# -----------------------------
def preprocess_image(img):
    """
    Improve image quality for QR detection
    """

    # convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # CLAHE for local contrast enhancement
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    gray = clahe.apply(gray)

    # noise reduction
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    return gray


# -----------------------------
# ROTATE IMAGE
# -----------------------------
def rotate_image(image, angle):

    (h, w) = image.shape[:2]

    center = (w // 2, h // 2)

    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    rotated = cv2.warpAffine(image, matrix, (w, h))

    return rotated


# -----------------------------
# OPENCV QR DETECTOR
# -----------------------------
def detect_qr_opencv(img):

    detector = cv2.QRCodeDetector()

    data, bbox, _ = detector.detectAndDecode(img)

    if bbox is not None and data:
        return data

    return None


# -----------------------------
# PYZBAR QR DETECTOR
# -----------------------------
def detect_qr_pyzbar(img):

    decoded_objects = decode(img)

    for obj in decoded_objects:

        try:
            return obj.data.decode("utf-8")
        except:
            continue

    return None


# -----------------------------
# MAIN QR READER
# -----------------------------
def read_qr_code(image_path):

    img = cv2.imread(image_path)

    if img is None:
        return None

    # enlarge image (helps detect small QR)
    img = cv2.resize(img, None, fx=1.5, fy=1.5)

    processed = preprocess_image(img)

    # 1️⃣ Try pyzbar first (handles distortion better)
    data = detect_qr_pyzbar(processed)

    if data:
        return data

    # 2️⃣ Try OpenCV detector
    data = detect_qr_opencv(processed)
       
    if data:
        return data

    # 3️⃣ Try rotated images
    for angle in [90, 180, 270]:

        rotated = rotate_image(processed, angle)

        data = detect_qr_opencv(rotated)

        if data:
            return data

        data = detect_qr_pyzbar(rotated)

        if data:
            return data

    return None


# -----------------------------
# PARSE QR PAYMENT DATA
# -----------------------------
def parse_qr_payment(qr_data):

    result = {
        "amount": None,
        "transaction_id": None
    }

    if not qr_data:
        return result

    # -----------------------------
    # Extract amount
    # -----------------------------
    amount_match = re.search(r"\d+\.\d{2}", qr_data)

    if amount_match:
        try:
            result["amount"] = float(amount_match.group())
        except:
            pass

    # -----------------------------
    # Extract transaction id
    # -----------------------------
    txn_match = re.search(r"[A-Z0-9]{8,}", qr_data)

    if txn_match:
        result["transaction_id"] = txn_match.group()

    return result