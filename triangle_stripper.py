
import pygame
import time
import math
import sys
import random
from enum import IntEnum


class Mode(IntEnum):
    LACES = 0
    STRIP = 1
    BOTH = 2


class Demo:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(flags = pygame.FULLSCREEN | pygame.NOFRAME, vsync=True)
        pygame.display.set_caption("every triangle is a love triangle when you love triangles")

        self.w = self.screen.get_width()
        self.h = self.screen.get_height()

        self.y_margin = self.h * .4
        self.x_margin = self.h * .05
        self.x_span = self.w - (self.x_margin * 2)

        self.bg = (255, 255, 255) #(192, 192, 192)
        self.fg = (64, 64, 64)
        self.pt_color = (0, 0, 0)
        self.mode = Mode.STRIP

        self.radius = 1
        self.line_w = 1
        self.a_list = []
        self.b_list = []
        self.all_points = []
        self.dialation = []
        self.last_pick = (-1, -1)
        self.shape_colors = []

    def saturated_bg(self, hue):
        color = pygame.Color(*self.bg)
        sat = 100 #color.hsva[1] + 20
        val = color.hsva[2]
        color.hsva = (hue, sat, val, 100)
        return color

    def regen(self, size_a = None, size_b = None):
        def line_points(size, y):
            t_values = []
            if size > 1:
                scale = 1 / (size - 1)
                t_values = [n * scale for n in range(size)]
            elif size == 1:
                t_values = [0.5]

            return [(t * self.x_span + self.x_margin, y) for t in t_values]

        self.a_line = line_points(size_a, self.y_margin)
        self.b_line = line_points(size_b, self.h - self.y_margin)
        self.all_points = self.a_line + self.b_line

        self.radius = math.ceil(min(
            min(self.x_margin, self.y_margin) / 4,
            self.x_span / (max(len(self.a_line), len(self.b_line)) * 2)))
        self.line_w = max(1, round(self.radius * .5))

        a_indices = list(range(size_a))
        b_indices = list(range(size_b))

        dialated_size = len(self.a_line) * len(self.b_line)
        def dialate(point_list):
            stride = dialated_size // len(point_list)
            return [i // stride for i in range(dialated_size)]

        last = None
        pivot = dialated_size // 2
        self.dialation = []

        for index, pair in enumerate(zip(
            dialate(a_indices),
            dialate(b_indices))):

            if last is None:
                last = pair
                self.dialation.append(pair)
                continue

            if last != pair:
                a_eq = last[0] == pair[0]
                b_eq = last[1] == pair[1]

                if a_eq != b_eq:
                    # tri case
                    pass

                else:
                    # quad case
                    assert(not a_eq)
                    assert(not b_eq)

                    if index < pivot:# and len(self.a_line) < len(self.b_line):
                        self.dialation.append((pair[0], last[1]))
                    else:
                        self.dialation.append((last[0], pair[1]))

                last = pair
                self.dialation.append(pair)

        hue = random.randint(0, 360)
        step = 360 / len(self.dialation) * 2

        self.shape_colors = []
        for i in range(len(self.dialation)):
            self.shape_colors.append(self.saturated_bg(int(hue)))
            hue += step
            while hue > 360:
                hue -= 360

    def randomize(self):
        while True:
            a = random.randint(2, 20)
            b = random.randint(2, 20)
            maybe = (a, b)
            if maybe != self.last_pick:
                self.last_pick = maybe
                break
        self.regen(*self.last_pick)

    def draw(self):
        self.screen.fill(self.bg)

        if self.mode == Mode.STRIP or self.mode == Mode.BOTH:
            for i in range(len(self.dialation) - 1):
                a, b = self.dialation[i]
                c, d = self.dialation[i + 1]
                points = (
                    self.a_line[a],
                    self.b_line[b],
                    self.b_line[d],
                    self.a_line[c])
                pygame.draw.polygon(self.screen, self.shape_colors[i], points)

        if self.mode == Mode.STRIP:
            for line in [self.a_line, self.b_line]:
                if len(line) > 1:
                    pygame.draw.line(self.screen, self.bg, line[0], line[-1], 8)
            for lhs, rhs in self.dialation:
                a_pt = self.a_line[lhs]
                b_pt = self.b_line[rhs]
                pygame.draw.line(self.screen, self.bg, a_pt, b_pt, 8)

            for line in [self.a_line, self.b_line]:
                if len(line) > 1:
                    pygame.draw.line(self.screen, (0, 0, 0), line[0], line[-1], 2)
            for lhs, rhs in self.dialation:
                a_pt = self.a_line[lhs]
                b_pt = self.b_line[rhs]
                pygame.draw.line(self.screen, (0, 0, 0), a_pt, b_pt, 2)


        if self.mode == Mode.LACES or self.mode == Mode.BOTH:
            for pt in self.all_points:
                pygame.draw.circle(self.screen, self.pt_color, pt, self.radius)

            for lhs, rhs in self.dialation:
                a_pt = self.a_line[lhs]
                b_pt = self.b_line[rhs]
                pygame.draw.line(self.screen, self.fg, a_pt, b_pt, self.line_w)

        pygame.display.flip()
        time.sleep(1/60)

    def main(self, shuffle_mode=False):
        start_t = time.time()

        last_shuffle = -1

        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        raise KeyboardInterrupt
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.randomize()

                elapsed = int(time.time() - start_t)
                if shuffle_mode and elapsed != last_shuffle and elapsed % 3 == 0:
                    last_shuffle = elapsed
                    self.randomize()

                self.draw()
        except KeyboardInterrupt:
            return


if __name__ == "__main__":
    fnord = Demo()

    maybe_points = sys.argv[1:]
    if len(maybe_points) == 2:
        a, b = map(int, maybe_points)
        fnord.regen(a, b)
        fnord.main(False)
    else:
        fnord.main(True)
