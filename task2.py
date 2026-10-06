import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact, IntText, RadioButtons, Button, Output, HBox, VBox
from IPython.display import display, clear_output


def bresenham(x0, y0, x1, y1, canvas_array, color=(255, 0, 0)):
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


def wu(x0, y0, x1, y1, canvas_array, color=(0, 255, 0)):
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

x0_widget = IntText(value=0, description='X0:', style={'description_width': 'initial'})
y0_widget = IntText(value=0, description='Y0:', style={'description_width': 'initial'})
x1_widget = IntText(value=400, description='X1:', style={'description_width': 'initial'})
y1_widget = IntText(value=400, description='Y1:', style={'description_width': 'initial'})

algorithm_widget = RadioButtons(
    options=['Брезенхем', 'Ву'],
    description='Алгоритм:',
    style={'description_width': 'initial'}
)

output = Output()

def draw_line(x0, y0, x1, y1, algorithm):
    canvas_width = 400
    canvas_height = 400
    
    canvas_array = np.ones((canvas_height, canvas_width, 3), dtype=np.uint8) * 255
    
    if algorithm == 'Брезенхем':
        bresenham(x0, y0, x1, y1, canvas_array, color=(255, 0, 0))
    else:
        wu(x0, y0, x1, y1, canvas_array, color=(255, 0, 0))
    
    with output:
        clear_output(wait=True)
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.imshow(canvas_array)
        ax.set_title(f'Алгоритм: {algorithm}')
        ax.axis('off')
        plt.tight_layout()
        plt.show()

button = Button(description="Нарисовать")
button.on_click(lambda b: draw_line(
    x0_widget.value, y0_widget.value, 
    x1_widget.value, y1_widget.value, 
    algorithm_widget.value
))

coords_box = HBox([x0_widget, y0_widget, x1_widget, y1_widget])
controls_box = VBox([coords_box, algorithm_widget, button])

display(controls_box)
display(output)