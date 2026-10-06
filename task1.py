import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox



class FloodFillLineBased:
    def __init__(self, image_array):
        self.image = image_array.copy()
        self.height, self.width = image_array.shape[:2]
        if len(image_array.shape) == 3:
            self.channels = image_array.shape[2]
        else:
            self.channels = 1
    
    def get_pixel_color(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return tuple(self.image[y, x])
        return None
    
    def set_pixel_color(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.image[y, x] = color
    
    def pixels_match(self, color1, color2, tolerance=0):
        if color1 is None or color2 is None:
            return False
        if tolerance == 0:
            return color1 == color2
        for c1, c2 in zip(color1, color2):
            if abs(int(c1) - int(c2)) > tolerance:
                return False
        return True
    
    def find_line_left(self, x, y, target_color, tolerance=0):
        while x >= 0 and self.pixels_match(self.get_pixel_color(x, y), target_color, tolerance):
            x -= 1
        return x + 1
    
    def find_line_right(self, x, y, target_color, tolerance=0):
        while x < self.width and self.pixels_match(self.get_pixel_color(x, y), target_color, tolerance):
            x += 1
        return x - 1
    
    def fill_line(self, x, y, new_color, target_color, tolerance=0):
        left = self.find_line_left(x, y, target_color, tolerance)
        right = self.find_line_right(x, y, target_color, tolerance)
        
        for i in range(left, right + 1):
            self.set_pixel_color(i, y, new_color)
        
        return left, right
    
    def flood_fill_recursive(self, start_x, start_y, new_color, tolerance=0):
        target_color = self.get_pixel_color(start_x, start_y)
        
        if target_color is None:
            return
        
        if self.pixels_match(target_color, new_color, tolerance):
            return
        
        stack = [(start_x, start_y)]
        visited = set()
        
        while stack:
            x, y = stack.pop()
            
            if (x, y) in visited:
                continue
            
            current_color = self.get_pixel_color(x, y)
            if not self.pixels_match(current_color, target_color, tolerance):
                continue
            
            visited.add((x, y))
            
            left, right = self.fill_line(x, y, new_color, target_color, tolerance)
            
            for check_y in [y - 1, y + 1]:
                if 0 <= check_y < self.height:
                    for check_x in range(left, right + 1):
                        neighbor_color = self.get_pixel_color(check_x, check_y)
                        if self.pixels_match(neighbor_color, target_color, tolerance):
                            if (check_x, check_y) not in visited:
                                stack.append((check_x, check_y))
    
    def get_result(self):
        return self.image.copy()


class FloodFillWithPattern:
    def __init__(self, image_array, pattern_image):
        self.image = image_array.copy()
        self.pattern = pattern_image
        self.pattern_height, self.pattern_width = pattern_image.shape[:2]
        self.height, self.width = image_array.shape[:2]
    
    def get_pattern_pixel(self, x, y, cyclic=True):
        if cyclic:
            px = x % self.pattern_width
            py = y % self.pattern_height
        else:
            px = min(x, self.pattern_width - 1)
            py = min(y, self.pattern_height - 1)
        
        if 0 <= px < self.pattern_width and 0 <= py < self.pattern_height:
            return tuple(self.pattern[py, px])
        return (0, 0, 0)
    
    def flood_fill_with_pattern(self, start_x, start_y, cyclic=True, tolerance=0):
        target_color = self.get_pixel_color(start_x, start_y)
        
        if target_color is None:
            return
        
        stack = [(start_x, start_y)]
        visited = set()
        
        while stack:
            x, y = stack.pop()
            
            if (x, y) in visited:
                continue
            
            current_color = self.get_pixel_color(x, y)
            if not self.colors_match(current_color, target_color, tolerance):
                continue
            
            visited.add((x, y))
            
            pattern_color = self.get_pattern_pixel(x, y, cyclic)
            self.set_pixel_color(x, y, pattern_color)
            
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) not in visited:
                        stack.append((nx, ny))
    
    def get_pixel_color(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return tuple(self.image[y, x])
        return None
    
    def set_pixel_color(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.image[y, x] = color
    
    def colors_match(self, color1, color2, tolerance=0):
        if color1 is None or color2 is None:
            return False
        if tolerance == 0:
            return color1 == color2
        for c1, c2 in zip(color1, color2):
            if abs(int(c1) - int(c2)) > tolerance:
                return False
        return True
    
    def get_result(self):
        return self.image.copy()


class BoundaryTracer:
    def __init__(self, image_array):
        self.image = image_array.copy()
        self.height, self.width = image_array.shape[:2]
        self.boundary_points = []
    
    def get_pixel_color(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return tuple(self.image[y, x])
        return None
    
    def find_boundary_start(self, boundary_color, tolerance=0):
        for y in range(self.height):
            for x in range(self.width):
                pixel_color = self.get_pixel_color(x, y)
                if self.colors_match(pixel_color, boundary_color, tolerance):
                    return (x, y)
        return None
    
    def trace_boundary(self, start_x, start_y, boundary_color, tolerance=0):
        self.boundary_points = []
        visited = set()
        
        current_x, current_y = start_x, start_y
        direction = 0  
        
        directions = [
            (1, 0),   # вправо
            (1, 1),   # вправо-вниз
            (0, 1),   # вниз
            (-1, 1),  # влево-вниз
            (-1, 0),  # влево
            (-1, -1), # влево-вверх
            (0, -1),  # вверх
            (1, -1),  # вправо-вверх
        ]
        
        max_iterations = self.width * self.height * 4
        
        for iteration in range(max_iterations):
            point = (current_x, current_y)
            
            if point in visited and len(self.boundary_points) > 0:
                break
            
            visited.add(point)
            self.boundary_points.append(point)
            
            found_next = False
            for i in range(8):
                dir_idx = (direction + i) % 8
                dx, dy = directions[dir_idx]
                next_x = current_x + dx
                next_y = current_y + dy
                
                if 0 <= next_x < self.width and 0 <= next_y < self.height:
                    next_color = self.get_pixel_color(next_x, next_y)
                    if self.colors_match(next_color, boundary_color, tolerance):
                        if (next_x, next_y) not in visited:
                            current_x, current_y = next_x, next_y
                            direction = (dir_idx + 6) % 8
                            found_next = True
                            break
            
            if not found_next:
                break
        
        return self.boundary_points
    
    def colors_match(self, color1, color2, tolerance=0):
        if color1 is None or color2 is None:
            return False
        if tolerance == 0:
            return color1 == color2
        for c1, c2 in zip(color1, color2):
            if abs(int(c1) - int(c2)) > tolerance:
                return False
        return True
    
    def draw_boundary_on_image(self, draw_color=(255, 0, 0), thickness=2):
        result = self.image.copy()
        
        for i in range(len(self.boundary_points)):
            x, y = self.boundary_points[i]
            
            for dx in range(-thickness//2, thickness//2 + 1):
                for dy in range(-thickness//2, thickness//2 + 1):
                    px, py = x + dx, y + dy
                    if 0 <= px < self.width and 0 <= py < self.height:
                        result[py, px] = draw_color
        
        return result


class InteractiveApp:  
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Заливка и выделение границы")
        
        self.canvas_width = 800
        self.canvas_height = 600
        self.image_array = None
        self.current_tool = "draw"
        
        self.drawing = False
        self.last_x = None
        self.last_y = None
        self.draw_color = (0, 0, 0)
        self.fill_color = (255, 0, 0)
        
        self.pattern_image = None
        
        self.setup_ui()
    
    def setup_ui(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        tk.Button(button_frame, text="Новое изображение", command=self.new_image).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Загрузить изображение", command=self.load_image).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Сохранить", command=self.save_image).pack(side=tk.LEFT, padx=2)
        
        tk.Label(button_frame, text="|").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Рисовать", command=lambda: self.set_tool("draw")).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Точка заливки", command=lambda: self.set_tool("fill_point")).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Цвет заливки", command=self.choose_fill_color).pack(side=tk.LEFT, padx=2)
        
        tk.Label(button_frame, text="|").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Загрузить паттерн", command=self.load_pattern).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Заливка паттерном", command=lambda: self.set_tool("pattern")).pack(side=tk.LEFT, padx=2)
        
        tk.Label(button_frame, text="|").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Граница", command=lambda: self.set_tool("boundary")).pack(side=tk.LEFT, padx=2)
        
        tk.Label(button_frame, text="|").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Очистить", command=self.clear_canvas).pack(side=tk.LEFT, padx=2)
        
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg='white')
        self.canvas.pack(padx=5, pady=5)
        
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        self.new_image()
    
    def new_image(self):
        self.image_array = np.ones((self.canvas_height, self.canvas_width, 3), dtype=np.uint8) * 255
        self.update_display()
    
    def load_image(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if filename:
            img = Image.open(filename)
            img = img.resize((self.canvas_width, self.canvas_height))
            self.image_array = np.array(img)
            if len(self.image_array.shape) == 2:
                self.image_array = np.stack([self.image_array] * 3, axis=-1)
            self.update_display()
    
    def save_image(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")]
        )
        if filename:
            img = Image.fromarray(self.image_array)
            img.save(filename)
            messagebox.showinfo("Сохранено", f"Изображение сохранено в {filename}")
    
    def load_pattern(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.webp *.gif"), ("All files", "*.*")]
        )
        if filename:
            img = Image.open(filename)
            
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3]) 
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            self.pattern_image = np.array(img)
            
            h, w = self.pattern_image.shape[:2]
            cyclic_mode = "Циклический" if h < 100 and w < 100 else "Нециклический"
            messagebox.showinfo("Паттерн загружен", 
                              f"Размер: {w}x{h}\nРежим: {cyclic_mode}\nФормат: RGB")
    
    def choose_fill_color(self):
        from tkinter import colorchooser
        color = colorchooser.askcolor(title="Выберите цвет заливки")
        if color[1]:
            hex_color = color[1]
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            self.fill_color = (r, g, b)
            print(f"Цвет заливки изменен на RGB({r}, {g}, {b})")
    
    def set_tool(self, tool):
        self.current_tool = tool
        print(f"Выбран инструмент: {tool}")
    
    def clear_canvas(self):
        self.new_image()
    
    def update_display(self):
        img = Image.fromarray(self.image_array)
        photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.photo = photo  
    
    def on_click(self, event):
        x, y = event.x, event.y
        
        if self.current_tool == "draw":
            self.drawing = True
            self.last_x = x
            self.last_y = y
        elif self.current_tool == "fill_point":
            self.perform_flood_fill(x, y)
        elif self.current_tool == "pattern":
            self.perform_pattern_fill(x, y)
        elif self.current_tool == "boundary":
            self.trace_and_draw_boundary(x, y)
    
    def on_drag(self, event):
        if self.drawing and self.current_tool == "draw":
            x, y = event.x, event.y
            self.draw_line(self.last_x, self.last_y, x, y, self.draw_color)
            self.last_x = x
            self.last_y = y
    
    def on_release(self, event):
        self.drawing = False
    
    def draw_line(self, x1, y1, x2, y2, color):
        thickness = 2  
        steps = max(abs(x2 - x1), abs(y2 - y1))
        if steps == 0:
            steps = 1
        
        for i in range(steps + 1):
            t = i / steps
            cx = int(x1 + (x2 - x1) * t)
            cy = int(y1 + (y2 - y1) * t)
            
            half = thickness // 2
            for dx in range(-half, half + 1):
                for dy in range(-half, half + 1):
                    px = cx + dx
                    py = cy + dy
                    if 0 <= px < self.canvas_width and 0 <= py < self.canvas_height:
                        self.image_array[py, px] = color
        
        self.update_display()
    
    def perform_flood_fill(self, x, y):
        if 0 <= x < self.canvas_width and 0 <= y < self.canvas_height:
            filler = FloodFillLineBased(self.image_array)
            filler.flood_fill_recursive(x, y, self.fill_color, tolerance=30)
            self.image_array = filler.get_result()
            self.update_display()
            print(f"Заливка выполнена в точке ({x}, {y})")
    
    def perform_pattern_fill(self, x, y):
        if self.pattern_image is None:
            messagebox.showwarning("Внимание", "Сначала загрузите паттерн!")
            return
        
        if 0 <= x < self.canvas_width and 0 <= y < self.canvas_height:
            filler = FloodFillWithPattern(self.image_array, self.pattern_image)
            cyclic = self.pattern_image.shape[0] < 100 and self.pattern_image.shape[1] < 100
            filler.flood_fill_with_pattern(x, y, cyclic=cyclic, tolerance=30)
            self.image_array = filler.get_result()
            self.update_display()
            mode = "циклический" if cyclic else "нециклический"
            print(f"Заливка паттерном выполнена в точке ({x}, {y}), режим: {mode}")
    
    def trace_and_draw_boundary(self, x, y):
        if 0 <= x < self.canvas_width and 0 <= y < self.canvas_height:
            tracer = BoundaryTracer(self.image_array)
            boundary_color = tracer.get_pixel_color(x, y)
            
            if boundary_color is not None:
                points = tracer.trace_boundary(x, y, boundary_color)
                
                if len(points) > 0:
                    result = tracer.draw_boundary_on_image(draw_color=(255, 0, 0))
                    self.image_array = result
                    self.update_display()
                    print(f"Граница обведена: найдено {len(points)} точек")
                else:
                    print("Граница не найдена")
            else:
                print("Не удалось определить цвет границы")
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = InteractiveApp()
    app.run()