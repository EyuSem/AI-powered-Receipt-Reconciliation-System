from paddleocr import PaddleOCR
from preprocess import preprocess_image
import cv2

# Load OCR model once
ocr = PaddleOCR(
    use_angle_cls=True,
    lang="en"
    #use_gpu=False,
    #enable_mkldnn=False
)

import os
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang="en")


def read_image_with_layout(image_path):

    result = ocr.ocr(image_path)

    lines = []

    for line in result[0]:

        bbox = line[0]
        text = line[1][0]
        confidence = line[1][1]

        lines.append({
            "text": text,
            "bbox": bbox,
            "confidence": confidence
        })

    return lines

def read_image(image_path):

    processed = preprocess_image(image_path)

    # Save temp processed image
    temp_path = image_path + "_processed.jpg"
    cv2.imwrite(temp_path, processed)

    result = ocr.ocr(temp_path)

    text_lines = []

    for line in result:
        for word in line:
            text = word[1][0]
            text_lines.append(text)

    text = "\n".join(text_lines)

    print("\n--- OCR TEXT ---\n")
    print(text)
    print("\n---------------\n")

    return text