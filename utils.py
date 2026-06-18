import math
import time
from enum import Enum, auto
import sdl2
import sdl2.ext

SCREEN_W: int = 1920
SCREEN_H: int = 1080
FRAMERATE: int = 60
MAX_TRIALS: int = 20
LOAD_TIME: int = 30
CHOICE_SECONDS: int = 3


class Mode(Enum):
    LOAD = auto()
    CHOICE = auto()
    CONSEQUENCE = auto()


def draw_rect(renderer, center, w, h, color):
    rect = sdl2.SDL_Rect(center[0] - int(w / 2), center[1] - int(h / 2), w, h)
    renderer.fill(rect, color=color)


def draw_circle(renderer, center, radius, color, thickness):
    renderer.color = color
    for tick in range(0, thickness):
        for angle in range(0, 360):
            rad = math.radians(angle)
            x = int(center[0] + (radius + tick) * math.cos(rad))
            y = int(center[1] + (radius + tick) * math.sin(rad))
            renderer.draw_point([x, y])


def should_close() -> bool:
    events = sdl2.ext.get_events()
    for event in events:
        if (event.type == sdl2.SDL_QUIT or
                (event.type == sdl2.SDL_KEYUP and (event.key.keysym.sym == sdl2.SDLK_ESCAPE or event.key.keysym.sym == sdl2.SDLK_w))):
            return True
    return False


def time_int() -> int:
    return time.time_ns() // int(1e6)