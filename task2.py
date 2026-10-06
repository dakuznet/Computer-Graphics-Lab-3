import sys
import pygame

class Canvas:
    def __init__(self, width, height, bg_color=(255, 255, 255)):
        self.width = width
        self.height = height
        self.pixels = [[bg_color for _ in range(width)] for _ in range(height)]

    def get(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.pixels[y][x]
        return None

    def set(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = color

    def to_surface(self):
        surface = pygame.Surface((self.width, self.height))
        px = pygame.surfarray.pixels2d(surface)
        for y in range(self.height):
            for x in range(self.width):
                c = self.pixels[y][x]
                px[x, y] = (c[0] << 16) + (c[1] << 8) + c[2]
        del px
        return surface

def draw_gradient_triangle(canvas, v0, v1, v2):
    verts = sorted([v0, v1, v2], key=lambda v: v[1])
    v0, v1, v2 = verts

    def interp(v_start, v_end, y):
        if v_start[1] == v_end[1]:
            return v_start
        t = (y - v_start[1]) / (v_end[1] - v_start[1])
        return (
            v_start[0] + t * (v_end[0] - v_start[0]),
            y,
            v_start[2] + t * (v_end[2] - v_start[2]),
            v_start[3] + t * (v_end[3] - v_start[3]),
            v_start[4] + t * (v_end[4] - v_start[4]),
        )

    for y in range(int(v0[1]), int(v2[1]) + 1):
        if y < v1[1]:
            left = interp(v0, v1, y)
            right = interp(v0, v2, y)
        else:
            left = interp(v1, v2, y)
            right = interp(v0, v2, y)

        if left[0] > right[0]:
            left, right = right, left

        for x in range(int(left[0]), int(right[0]) + 1):
            t = 0 if left[0] == right[0] else (x - left[0]) / (right[0] - left[0])
            r = left[2] + t * (right[2] - left[2])
            g = left[3] + t * (right[3] - left[3])
            b = left[4] + t * (right[4] - left[4])
            canvas.set(x, y, (int(r), int(g), int(b)))

def main():
    pygame.init()
    W, H = 1000, 1000
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Задание 3 — Градиентный треугольник (произвольный)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 16)

    canvas = Canvas(W, H)

    vertices = []  
    colors = [
        (255, 0, 0),    
        (0, 255, 0),    
        (0, 0, 255),   
    ]
    color_names = ["красную", "зелёную", "синюю"]

    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_c:
                    canvas = Canvas(W, H)
                    vertices = []

            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos

                if len(vertices) < 3:
                    vertices.append((mx, my))
                    if len(vertices) == 3:
                        v0 = vertices[0] + colors[0] 
                        v1 = vertices[1] + colors[1]
                        v2 = vertices[2] + colors[2]
                        draw_gradient_triangle(canvas, v0, v1, v2)

        screen.blit(canvas.to_surface(), (0, 0))

        for i, (vx, vy) in enumerate(vertices):
            pygame.draw.circle(screen, colors[i], (vx, vy), 6)
            pygame.draw.circle(screen, (0, 0, 0), (vx, vy), 6, 1)

        if len(vertices) >= 2:
            pygame.draw.line(screen, (100, 100, 100), vertices[0], vertices[1], 1)
        if len(vertices) >= 3:
            pygame.draw.line(screen, (100, 100, 100), vertices[1], vertices[2], 1)
            pygame.draw.line(screen, (100, 100, 100), vertices[2], vertices[0], 1)
        if len(vertices) < 3:
            hint = f"Кликните {color_names[len(vertices)]} вершину ({len(vertices) + 1}/3)"
        else:
            hint = "Треугольник построен"
            if len(vertices) == 3:
                pass

        screen.blit(font.render(hint, True, (80, 80, 80)), (10, 10))
        screen.blit(font.render("C — очистить", True, (80, 80, 80)), (10, 30))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()