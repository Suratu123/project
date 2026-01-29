import cv2
import numpy as np
import pytesseract
from pytesseract import Output

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_sudoku_from_image(path):
    img = cv2.imread(path)
    if img is None:
        raise ValueError("Cannot load image")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV,
        11, 2
    )

    # Detect grid lines
    lines = cv2.HoughLinesP(
        thresh, 1, np.pi / 180,
        threshold=150,
        minLineLength=200,
        maxLineGap=10
    )

    if lines is None:
        raise ValueError("Grid not detected")

    xs, ys = [], []
    for l in lines:
        x1, y1, x2, y2 = l[0]
        xs.extend([x1, x2])
        ys.extend([y1, y2])

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    sudoku = gray[min_y:max_y, min_x:max_x]

    h, w = sudoku.shape
    cell_h, cell_w = h // 9, w // 9

    grid = [[0]*9 for _ in range(9)]
    confidence = [[0]*9 for _ in range(9)]

    for r in range(9):
        for c in range(9):
            cell = sudoku[
                r*cell_h:(r+1)*cell_h,
                c*cell_w:(c+1)*cell_w
            ]

            cell = cell[6:-6, 6:-6]
            cell = cv2.resize(cell, (40, 40))

            data = pytesseract.image_to_data(
                cell,
                config="--psm 10 -c tessedit_char_whitelist=123456789",
                output_type=Output.DICT
            )

            txt = data["text"][0].strip()
            conf = int(data["conf"][0])

            if txt.isdigit() and conf > 40:
                grid[r][c] = int(txt)
                confidence[r][c] = conf

    return grid, confidence
