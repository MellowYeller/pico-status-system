import uasyncio as asyncio
import time
import random
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_P8 # type: ignore

class Ball:
    def __init__(self, x, y, r, dx, dy, pen):
        self.x = x
        self.y = y
        self.r = r
        self.dx = dx
        self.dy = dy
        self.pen = pen

class Image:
    display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2, pen_type=PEN_P8)
    WIDTH, HEIGHT = display.get_bounds()

    display.set_backlight(1.0)
    BG = display.create_pen(3, 7, 30)

    text_color = [253,240,213]
    text_pen = display.create_pen(text_color[0],text_color[1],text_color[2])

    bar_color = [87, 204, 153]
    bar_pen = display.create_pen(bar_color[0],bar_color[1],bar_color[2])

    bar_height = 48

    text = "Free :)"

    balls = []

    def __init__(self):
        self.init_balls()
    
    def set_text_color(self,r,g,b):
        self.text_color = [r,g,b]
        self.text_pen = self.display.create_pen(self.text_color[0], self.text_color[1], self.text_color[2])

    def set_bar_color(self,r,g,b):
        self.bar_color = [r,g,b]
        self.bar_pen = self.display.create_pen(self.bar_color[0], self.bar_color[1], self.bar_color[2])

    def set_bg_color(self,r,g,b):
        self.BG = self.display.create_pen(r, g, b)


    def init_balls(self):
        # initialise shapes
        self.display.clear()
        self.balls = []
        self.balls.clear
        for _i in range(10):
            r = random.randint(0, 10) + 3
            self.balls.append(
                Ball(
                    random.randint(r, r + (self.WIDTH - 2 * r)),
                    random.randint(r, r + (self.HEIGHT - 2 * r)),
                    r,
                    (14 - r) / 2,
                    (14 - r) / 2,
                    self.display.create_pen(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                )
            )

    def draw_text(self):
        self.display.set_pen(self.text_pen)
        self.display.set_font("sans")
        self.display.set_thickness(6)
        self.display.text(self.text, 0, 120, scale=2, fixed_width=1)

    def draw_bars(self):
        self.display.set_pen(self.bar_pen)
        self.display.rectangle(0, 0, self.WIDTH, self.bar_height)
        self.display.rectangle(0, self.HEIGHT-self.bar_height, self.WIDTH, self.bar_height)


    def draw_balls(self):
        for ball in self.balls:
            ball.x += ball.dx
            ball.y += ball.dy

            xmax = self.WIDTH - ball.r
            xmin = ball.r
            ymax = self.HEIGHT - ball.r
            ymin = ball.r

            if ball.x < xmin or ball.x > xmax:
                ball.dx *= -1

            if ball.y < ymin or ball.y > ymax:
                ball.dy *= -1

            self.display.set_pen(ball.pen)
            self.display.circle(int(ball.x), int(ball.y), int(ball.r))



    async def update_loop(self):
        while True:
            self.display.set_pen(self.BG)
            self.display.clear()

            self.draw_balls()
            self.draw_bars()
            self.draw_text()
            self.display.update()

            await asyncio.sleep(0.0667)

image = Image()