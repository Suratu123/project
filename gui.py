import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import pytesseract
import threading

# ------------------ TESSERACT PATH ------------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

OCR_COLOR = "#1f4fd8"      # Dark blue (OCR digits)
SOLVED_COLOR = "#1e8449"   # Dark green (solved digits)
USER_COLOR = "black"

# ------------------ SUDOKU SOLVER ------------------
def is_valid(board, r, c, n):
    for i in range(9):
        if board[r][i] == n or board[i][c] == n:
            return False
    br, bc = (r // 3) * 3, (c // 3) * 3
    for i in range(3):
        for j in range(3):
            if board[br + i][bc + j] == n:
                return False
    return True


def solve(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                for n in range(1, 10):
                    if is_valid(board, r, c, n):
                        board[r][c] = n
                        if solve(board):
                            return True
                        board[r][c] = 0
                return False
    return True


# ------------------ OCR FUNCTIONS ------------------
def preprocess_cell(cell):
    gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV,
        11, 2
    )

    h, w = thresh.shape
    margin = int(min(h, w) * 0.15)
    thresh[:margin, :] = 0
    thresh[-margin:, :] = 0
    thresh[:, :margin] = 0
    thresh[:, -margin:] = 0

    return thresh


def extract_grid_from_image(path):
    img = cv2.imread(path)
    if img is None:
        raise ValueError("Image could not be loaded")

    img = cv2.resize(img, (450, 450))
    cell_h, cell_w = 50, 50
    grid = [[0] * 9 for _ in range(9)]

    for r in range(9):
        for c in range(9):
            cell = img[r * cell_h:(r + 1) * cell_h,
                       c * cell_w:(c + 1) * cell_w]
            proc = preprocess_cell(cell)
            text = pytesseract.image_to_string(
                proc,
                config="--psm 10 -c tessedit_char_whitelist=123456789"
            ).strip()
            if text.isdigit():
                grid[r][c] = int(text)

    return grid, img


# ------------------ GUI ------------------
class SudokuGUI:
    def __init__(self, root):
        self.root = root
        root.title("Sudoku Solver with OCR")
        root.geometry("1200x720")
        root.configure(bg="#f4f6f7")

        self.ocr_cells = [[False]*9 for _ in range(9)]

        tk.Label(
            root,
            text="Sudoku Solver",
            font=("Segoe UI", 26, "bold"),
            bg="#f4f6f7"
        ).pack(pady=15)

        main = tk.Frame(root, bg="#f4f6f7")
        main.pack(expand=True)

        # ===== GRID =====
       
        grid_frame = tk.Frame(main, bg="#f4f6f7")
        grid_frame.grid(row=0, column=0, padx=30)

        CELL = 36
        BOX_GAP = 6

        self.entries = [[None]*9 for _ in range(9)]

        for br in range(3):  # box row
            for bc in range(3):  # box column

                box = tk.Frame(
                    grid_frame,
                    bg="black",
                    padx=2,
                    pady=2
                )
                box.grid(
                    row=br,
                    column=bc,
                    padx=BOX_GAP,
                    pady=BOX_GAP
                )

                for r in range(3):
                    for c in range(3):
                        rr = br * 3 + r
                        cc = bc * 3 + c

                        cell_frame = tk.Frame(
                            box,
                            width=CELL,
                            height=CELL,
                            bg="black"
                        )
                        cell_frame.grid(row=r, column=c, padx=1, pady=1)
                        cell_frame.grid_propagate(False)

                        e = tk.Entry(
                            cell_frame,
                            font=("Segoe UI", 14, "bold"),
                            justify="center",
                            bd=0,
                            relief="flat"
                        )
                        e.place(
                            relx=0.5,
                            rely=0.5,
                            anchor="center",
                            width=CELL - 6,
                            height=CELL - 6
                        )

                        self.entries[rr][cc] = e


        # ===== IMAGE PREVIEW =====
        right = tk.Frame(main, bg="#f4f6f7")
        right.grid(row=0, column=1, padx=40)

        tk.Label(
            right,
            text="Image Preview",
            font=("Segoe UI", 15, "bold"),
            bg="#f4f6f7"
        ).pack(pady=6)

        box = tk.Frame(right, width=300, height=300, bg="#ddd", bd=2, relief="groove")
        box.pack()

        self.image_label = tk.Label(box, bg="#ddd")
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")

        self.status = tk.Label(
            right,
            text="",
            fg="#0066cc",
            bg="#f4f6f7",
            font=("Segoe UI", 11)
        )
        self.status.pack(pady=10)

        # ===== BUTTONS =====
        btns = tk.Frame(root, bg="#f4f6f7")
        btns.pack(pady=20)

        tk.Button(btns, text="Solve Puzzle", bg="#2ecc71", fg="white",
                  width=18, font=("Segoe UI", 11),
                  command=self.solve_manual).grid(row=0, column=0, padx=10)

        tk.Button(btns, text="Solve From Image", bg="#3498db", fg="white",
                  width=18, font=("Segoe UI", 11),
                  command=self.solve_from_image).grid(row=0, column=1, padx=10)

        tk.Button(btns, text="Clear Grid", bg="#e74c3c", fg="white",
                  width=18, font=("Segoe UI", 11),
                  command=self.clear).grid(row=0, column=2, padx=10)

    def clear(self):
        for r in range(9):
            for c in range(9):
                self.entries[r][c].delete(0, tk.END)
                self.entries[r][c].config(fg=USER_COLOR)
                self.ocr_cells[r][c] = False
        self.image_label.config(image="")
        self.status.config(text="")

    def solve_manual(self):
        board = self.get_board()
        if not solve(board):
            messagebox.showerror("Error", "No solution exists")
            return

        for r in range(9):
            for c in range(9):
                if self.entries[r][c].get() == "":
                    self.entries[r][c].insert(0, str(board[r][c]))
                    self.entries[r][c].config(fg=SOLVED_COLOR)

    def solve_from_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg")]
        )
        if not path:
            return
        self.status.config(text="Processing image...")
        threading.Thread(target=self._process_image, args=(path,), daemon=True).start()

    def _process_image(self, path):
        try:
            grid, img = extract_grid_from_image(path)
            self.root.after(0, self.display_image, img)
            self.root.after(0, self.fill_ocr, grid)
            self.root.after(0, lambda: self.status.config(
                text="Digits loaded (blue = OCR, green = solved)"
            ))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

    def fill_ocr(self, grid):
        for r in range(9):
            for c in range(9):
                if grid[r][c] != 0:
                    self.entries[r][c].delete(0, tk.END)
                    self.entries[r][c].insert(0, str(grid[r][c]))
                    self.entries[r][c].config(fg=OCR_COLOR)
                    self.ocr_cells[r][c] = True

    def display_image(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img).resize((300, 300))
        tk_img = ImageTk.PhotoImage(img)
        self.image_label.config(image=tk_img)
        self.image_label.image = tk_img

    def get_board(self):
        board = [[0] * 9 for _ in range(9)]
        for r in range(9):
            for c in range(9):
                val = self.entries[r][c].get()
                if val.isdigit():
                    board[r][c] = int(val)
        return board


if __name__ == "__main__":
    root = tk.Tk()
    SudokuGUI(root)
    root.mainloop()
