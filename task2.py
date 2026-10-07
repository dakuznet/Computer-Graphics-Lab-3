import tkinter as tk
from tkinter import messagebox
import numpy as np
from PIL import Image, ImageTk


def bresenham_line(x0, y0, x1, y1, canvas_array, color=(255, 0, 0)):
    """Целочисленный алгоритм Брезенхема"""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        if 0 <= x0 < canvas_array.shape[1] and 0 <= y0 < canvas_array.shape[0]:
            canvas_array[y0, x0] = color

        if x0 == x1 and y0 == y1:
            break

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def wu_line(x0, y0, x1, y1, canvas_array, color=(0, 255, 0)):
    """Алгоритм Ву с антиалиасингом"""
    def ipart(x):
        return int(np.floor(x))

    def round_val(x):
        return int(np.round(x))

    def fpart(x):
        return x - np.floor(x)

    def rfpart(x):
        return 1 - fpart(x)

    def set_pixel(x, y, intensity):
        if 0 <= x < canvas_array.shape[1] and 0 <= y < canvas_array.shape[0]:
            canvas_array[y, x] = [int(c * intensity) for c in color]

    steep = abs(y1 - y0) > abs(x1 - x0)

    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x0

    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = y1 - y0
    gradient = dy / dx if dx != 0 else 1.0

    xend = round_val(x0)
    yend = y0 + gradient * (xend - x0)
    xgap = rfpart(x0 + 0.5)
    xpxl1 = xend
    ypxl1 = ipart(yend)

    if steep:
        set_pixel(ypxl1, xpxl1, rfpart(yend) * xgap)
        set_pixel(ypxl1 + 1, xpxl1, fpart(yend) * xgap)
    else:
        set_pixel(xpxl1, ypxl1, rfpart(yend) * xgap)
        set_pixel(xpxl1, ypxl1 + 1, fpart(yend) * xgap)

    intery = yend + gradient

    xend = round_val(x1)
    yend = y1 + gradient * (xend - x1)
    xgap = fpart(x1 + 0.5)
    xpxl2 = xend
    ypxl2 = ipart(yend)

    if steep:
        set_pixel(ypxl2, xpxl2, rfpart(yend) * xgap)
        set_pixel(ypxl2 + 1, xpxl2, fpart(yend) * xgap)
    else:
        set_pixel(xpxl2, ypxl2, rfpart(yend) * xgap)
        set_pixel(xpxl2, ypxl2 + 1, fpart(yend) * xgap)

    for x in range(xpxl1 + 1, xpxl2):
        y = ipart(intery)
        if steep:
            set_pixel(y, x, rfpart(intery))
            set_pixel(y + 1, x, fpart(intery))
        else:
            set_pixel(x, y, rfpart(intery))
            set_pixel(x, y + 1, fpart(intery))
        intery += gradient


class LineDrawerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Растровые алгоритмы: Брезенхем и Ву")
        self.root.resizable(False, False)

        control_frame = tk.Frame(root, padx=10, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Label(control_frame, text="X0:").grid(row=0, column=0, padx=5)
        tk.Label(control_frame, text="Y0:").grid(row=0, column=2, padx=5)
        tk.Label(control_frame, text="X1:").grid(row=0, column=4, padx=5)
        tk.Label(control_frame, text="Y1:").grid(row=0, column=6, padx=5)

        self.txt_x0 = tk.Entry(control_frame, width=8)
        self.txt_x0.insert(0, "0")
        self.txt_x0.grid(row=0, column=1, padx=5)

        self.txt_y0 = tk.Entry(control_frame, width=8)
        self.txt_y0.insert(0, "0")
        self.txt_y0.grid(row=0, column=3, padx=5)

        self.txt_x1 = tk.Entry(control_frame, width=8)
        self.txt_x1.insert(0, "400")
        self.txt_x1.grid(row=0, column=5, padx=5)

        self.txt_y1 = tk.Entry(control_frame, width=8)
        self.txt_y1.insert(0, "400")
        self.txt_y1.grid(row=0, column=7, padx=5)

        self.algorithm = tk.StringVar(value="bresenham")
        tk.Radiobutton(control_frame, text="Брезенхем", variable=self.algorithm,
                       value="bresenham").grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=5)
        tk.Radiobutton(control_frame, text="Ву (с антиалиасингом)", variable=self.algorithm,
                       value="wu").grid(row=1, column=4, columnspan=4, sticky=tk.W, pady=5)

        btn_draw = tk.Button(control_frame, text="Нарисовать", command=self.draw_line,
                             width=15, height=2, bg="#4CAF50", fg="white")
        btn_draw.grid(row=0, column=8, rowspan=2, padx=15)

        self.canvas_width = 600
        self.canvas_height = 500

        self.canvas_frame = tk.Frame(root, bd=2, relief=tk.SUNKEN)
        self.canvas_frame.pack(padx=10, pady=10)

        self.canvas = tk.Canvas(self.canvas_frame, width=self.canvas_width,
                                height=self.canvas_height, bg='white')
        self.canvas.pack()

        self._photo = None

    def draw_line(self):
        try:
            x0 = int(self.txt_x0.get())
            y0 = int(self.txt_y0.get())
            x1 = int(self.txt_x1.get())
            y1 = int(self.txt_y1.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные целые числа!")
            return

        canvas_array = np.ones((self.canvas_height, self.canvas_width, 3), dtype=np.uint8) * 255

        if self.algorithm.get() == "bresenham":
            bresenham_line(x0, y0, x1, y1, canvas_array, color=(255, 0, 0))
        else:
            wu_line(x0, y0, x1, y1, canvas_array, color=(0, 255, 0))

        img = Image.fromarray(canvas_array)
        self._photo = ImageTk.PhotoImage(img)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self._photo)


if __name__ == "__main__":
    root = tk.Tk()
    app = LineDrawerApp(root)
    root.mainloop()
