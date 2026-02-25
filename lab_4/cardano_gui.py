# Оконный интерфейс для шифра «Поворотная решётка» Кардано.
# Визуализация решётки 6×10: белые ячейки — вырезы, серые — закрытые.
# При шифровании показываются все 4 поворота и подсветка пустышек.

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from lab_4.cardano import trafar, encrypt_text, decrypt_text, encrypt_text_with_details

CELL_SIZE = 36
CELL_SIZE_SMALL = 22   # для окна с поворотами
GRID_ROWS = 6
GRID_COLS = 10
COLOR_CUTOUT = "#ffffff"   # вырез (белый)
COLOR_CLOSED = "#808080"   # закрытая ячейка (серый)
COLOR_PADDING = "#fff3cd"  # пустышка (светло-жёлтый)
COLOR_PADDING_TEXT = "#856404"
BORDER_COLOR = "#333333"


def _draw_grille_block(parent, block, block_index, title_prefix=""):
    """Рисует один блок: 4 решётки (повороты) + общая матрица. Возвращает frame."""
    matrix = block["matrix"]
    is_padding = block["is_padding"]
    rot_positions = block["rotation_positions"]
    sz = CELL_SIZE_SMALL
    labels = ["Положение 1 (исходное)", "Положение 2 (поворот 1)", "Положение 3 (поворот 2)", "Положение 4 (поворот 3)"]
    frame = ttk.LabelFrame(parent, text=f"{title_prefix}Блок {block_index + 1}", padding=6)
    row0 = ttk.Frame(frame)
    row0.pack(fill=tk.X)
    for r in range(4):
        cell_cutouts = set(rot_positions[r])
        col_frame = ttk.Frame(row0)
        col_frame.pack(side=tk.LEFT, padx=8, pady=4)
        ttk.Label(col_frame, text=labels[r], font=("Segoe UI", 8)).pack()
        canv = tk.Canvas(col_frame, width=GRID_COLS * sz + 2, height=GRID_ROWS * sz + 2,
                         highlightthickness=1, highlightbackground=BORDER_COLOR, bg="#f0f0f0")
        canv.pack()
        for i in range(GRID_ROWS):
            for j in range(GRID_COLS):
                x1, y1 = j * sz + 1, i * sz + 1
                x2, y2 = x1 + sz, y1 + sz
                if (i, j) in cell_cutouts:
                    is_pad = is_padding[i][j]
                    fill = COLOR_PADDING if is_pad else COLOR_CUTOUT
                    canv.create_rectangle(x1, y1, x2, y2, fill=fill, outline=BORDER_COLOR, width=1)
                    ch = matrix[i][j]
                    if ch:
                        color = COLOR_PADDING_TEXT if is_pad else "black"
                        canv.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=ch.upper(), font=("Consolas", 9), fill=color)
                else:
                    canv.create_rectangle(x1, y1, x2, y2, fill=COLOR_CLOSED, outline=BORDER_COLOR, width=1)
    # Общая заполненная матрица (все 60 ячеек)
    mat_frame = ttk.Frame(frame)
    mat_frame.pack(pady=(8, 0))
    ttk.Label(mat_frame, text="Итоговая матрица (шифртекст построчно):", font=("Segoe UI", 9)).pack(anchor="w")
    mat_canv = tk.Canvas(mat_frame, width=GRID_COLS * sz + 2, height=GRID_ROWS * sz + 2,
                         highlightthickness=1, highlightbackground=BORDER_COLOR, bg="#f0f0f0")
    mat_canv.pack()
    for i in range(GRID_ROWS):
        for j in range(GRID_COLS):
            x1, y1 = j * sz + 1, i * sz + 1
            x2, y2 = x1 + sz, y1 + sz
            is_pad = is_padding[i][j]
            fill = COLOR_PADDING if is_pad else COLOR_CUTOUT
            mat_canv.create_rectangle(x1, y1, x2, y2, fill=fill, outline=BORDER_COLOR, width=1)
            ch = matrix[i][j]
            if ch:
                color = COLOR_PADDING_TEXT if is_pad else "black"
                mat_canv.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=ch.upper(), font=("Consolas", 9), fill=color)
    return frame


def show_encrypt_details(cipher_result, orig_len, blocks, parent):
    """Открывает окно с визуализацией: 4 поворота решётки и пустышки (жёлтым)."""
    win = tk.Toplevel(parent)
    win.title("Заполнение решётки при шифровании")
    win.resizable(True, True)
    ttk.Label(win, text="Белые ячейки — текст сообщения, жёлтые — пустышки (добавлены до кратности 60).",
              font=("Segoe UI", 10)).pack(pady=(8, 4))
    for idx, block in enumerate(blocks):
        _draw_grille_block(win, block, idx).pack(fill=tk.X, padx=8, pady=6)
    ttk.Label(win, text=f"Длина исходного текста (для расшифровки): {orig_len}", font=("Segoe UI", 9)).pack(pady=8)


def run():
    root = tk.Tk()
    root.title("Шифр «Поворотная решётка» Кардано")
    root.resizable(True, True)

    # Заголовок
    ttk.Label(root, text="Трафарет решётки (белое — вырез, серое — закрыто)", font=("Segoe UI", 10)).pack(pady=(8, 4))

    # Рамка с решёткой
    frame_grille = ttk.Frame(root, padding=8)
    frame_grille.pack()

    canvas = tk.Canvas(
        frame_grille,
        width=GRID_COLS * CELL_SIZE + 2,
        height=GRID_ROWS * CELL_SIZE + 2,
        highlightthickness=1,
        highlightbackground=BORDER_COLOR,
        bg="#f0f0f0"
    )
    canvas.pack()

    for i in range(GRID_ROWS):
        for j in range(GRID_COLS):
            x1, y1 = j * CELL_SIZE + 1, i * CELL_SIZE + 1
            x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
            color = COLOR_CUTOUT if trafar[i][j] == 0 else COLOR_CLOSED
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=BORDER_COLOR, width=1)

    # Текст и кнопки
    ttk.Label(root, text="Текст:", font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(12, 2))
    text_in = scrolledtext.ScrolledText(root, height=4, width=50, font=("Consolas", 10), wrap=tk.WORD)
    text_in.pack(fill=tk.X, padx=12, pady=(0, 8))

    def do_encrypt():
        t = text_in.get("1.0", tk.END).strip()
        if not t:
            messagebox.showinfo("Ввод", "Введите текст для шифрования.")
            return
        try:
            result, orig_len, blocks = encrypt_text_with_details(t)
            text_in.delete("1.0", tk.END)
            text_in.insert(tk.END, result)
            show_encrypt_details(result, orig_len, blocks, root)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def do_decrypt():
        t = text_in.get("1.0", tk.END).strip()
        if not t:
            messagebox.showinfo("Ввод", "Введите текст для расшифрования.")
            return
        try:
            result = decrypt_text(t)
            text_in.delete("1.0", tk.END)
            text_in.insert(tk.END, result)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    btn_frame = ttk.Frame(root, padding=8)
    btn_frame.pack()
    ttk.Button(btn_frame, text="Зашифровать", command=do_encrypt).pack(side=tk.LEFT, padx=4)
    ttk.Button(btn_frame, text="Расшифровать", command=do_decrypt).pack(side=tk.LEFT, padx=4)

    root.mainloop()
