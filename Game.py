import time
from pickle import FRAME

import sdl2.ext
import sdl2.sdlttf
import sdl2.sdlmixer
import cv2
import sys

import utils
from utils import MAX_TRIALS, Mode

sdl2.ext.init(sdl2.SDL_INIT_VIDEO)
sdl2.sdlttf.TTF_Init()
mode = sdl2.SDL_DisplayMode()
sdl2.SDL_GetCurrentDisplayMode(0, mode)
utils.SCREEN_W = mode.w
utils.SCREEN_H = mode.h
window = sdl2.ext.Window("HELLO!", size=(utils.SCREEN_W, utils.SCREEN_H), flags=sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP)
renderer = sdl2.ext.Renderer(window)

red = sdl2.ext.Color(255, 0, 0)
green = sdl2.ext.Color(0, 255, 0)
blue = sdl2.ext.Color(0, 0, 255)
black = sdl2.ext.Color(0, 0, 0)
white = sdl2.SDL_Color(255, 255, 255)

factory = sdl2.ext.SpriteFactory(renderer=renderer)
spriterenderer = factory.create_sprite_render_system(window)

font = sdl2.sdlttf.TTF_OpenFont(b"./fonts/Roboto-Regular.ttf", 500)

webcam = cv2.VideoCapture(0)
success, image = webcam.read()
if not success:
    sys.exit(-1)
height, width, channels = image.shape
webcam_texture = sdl2.SDL_CreateTexture(renderer.sdlrenderer, sdl2.SDL_PIXELFORMAT_RGB24, sdl2.SDL_TEXTUREACCESS_STATIC, width, height)
text_rect = sdl2.SDL_Rect(utils.SCREEN_W // 2 - 250, utils.SCREEN_H // 2 - 250, 500, 500)
timer_rect = sdl2.SDL_Rect(10, 10, 200, 200)
webcam_rect = sdl2.SDL_Rect(utils.SCREEN_W - 300, utils.SCREEN_H - 200, 300, 200)
image_rect = sdl2.SDL_Rect(utils.SCREEN_W // 2 - 400, utils.SCREEN_H // 2 - 400, 800, 800)
running: bool = True
trials: int = 0
game_mode: Mode = Mode.LOAD
step: int = 0
mode_seconds: int
time_displayed: int
renderer.color = black
prev_tick: int = utils.time_int()
for n in range(3, 0, -1):
    text_surface = sdl2.sdlttf.TTF_RenderUTF8_Blended(font, f"{n}".encode("utf-8"), white)
    texture = sdl2.SDL_CreateTextureFromSurface(renderer.sdlrenderer, text_surface)
    sdl2.SDL_FreeSurface(text_surface)
    for _ in range(60):
        renderer.clear()
        sdl2.SDL_RenderCopy(renderer.sdlrenderer, texture, None, text_rect)
        current_tick: int = utils.time_int()
        if (current_tick - prev_tick) * utils.FRAMERATE < 1000:
            time.sleep((1000 / utils.FRAMERATE - current_tick + prev_tick) / 1000)
        renderer.present()
        prev_tick = utils.time_int()
        if utils.should_close():
            running = False
            break
    sdl2.SDL_DestroyTexture(texture)
    if not running:
        break
text_surface = sdl2.sdlttf.TTF_RenderUTF8_Blended(font, b"3", white)
text_texture = sdl2.SDL_CreateTextureFromSurface(renderer.sdlrenderer, text_surface)
sdl2.SDL_FreeSurface(text_surface)
sprite_doge = factory.from_image("images/Doge.png")
sdl2.SDL_SetTextureBlendMode(sprite_doge.texture, sdl2.SDL_BLENDMODE_BLEND)
start_time: int = utils.time_int()
while running and trials < MAX_TRIALS:
    renderer.color = black
    renderer.clear()
    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            running = False
            break
        if event.type == sdl2.SDL_KEYUP:
            if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                running = False
                break
            if event.key.keysym.sym == sdl2.SDLK_w:
                enemies = []
                trials = MAX_TRIALS
                break

    success, image = webcam.read()
    if not success:
        continue
    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    sdl2.SDL_UpdateTexture(webcam_texture, None, image_rgb.ctypes.data, width * 3)
    sdl2.SDL_RenderClear(renderer.sdlrenderer)
    sdl2.SDL_RenderCopy(renderer.sdlrenderer, webcam_texture, None, webcam_rect)
    sdl2.SDL_RenderPresent(renderer.sdlrenderer)
    timestamp = utils.time_int()
    if game_mode == Mode.LOAD:
        step += 1
        if step >= 30:
            print(timestamp - start_time)
            start_time = timestamp
            game_mode = Mode.CHOICE
            mode_seconds = utils.CHOICE_SECONDS
            time_displayed = utils.CHOICE_SECONDS
            sdl2.SDL_RenderCopyEx(renderer.sdlrenderer, sprite_doge.texture, None, image_rect, 0.0, None, sdl2.SDL_FLIP_NONE)
        else:
            multiplicator: float = 1 / (30 - step)
            current_step_rect = sdl2.SDL_Rect(image_rect.x + int(400 * (1 - multiplicator)), image_rect.y + int(400 * (1 - multiplicator)),
                                              int(800 * multiplicator), int(800 * multiplicator))
            sdl2.SDL_RenderCopyEx(renderer.sdlrenderer, sprite_doge.texture, None, current_step_rect, 0.0, None, sdl2.SDL_FLIP_NONE)
    elif game_mode == Mode.CHOICE:
        if timestamp - start_time >= 1000:
            start_time = timestamp
            mode_seconds -= 1
            if mode_seconds > 0:
                sdl2.SDL_DestroyTexture(text_texture)
                text_surface = sdl2.sdlttf.TTF_RenderUTF8_Blended(font, f"{mode_seconds}".encode("utf-8"), white)
                text_texture = sdl2.SDL_CreateTextureFromSurface(renderer.sdlrenderer, text_surface)
                sdl2.SDL_FreeSurface(text_surface)
            else:
                sdl2.SDL_DestroyTexture(text_texture)
                game_mode = Mode.CONSEQUENCE
                start_time = timestamp
        sdl2.SDL_RenderCopy(renderer.sdlrenderer, text_texture, None, timer_rect)
        sdl2.SDL_RenderCopyEx(renderer.sdlrenderer, sprite_doge.texture, None, image_rect, 0.0, None, sdl2.SDL_FLIP_NONE)
    elif game_mode == Mode.CONSEQUENCE:
        sdl2.SDL_RenderCopyEx(renderer.sdlrenderer, sprite_doge.texture, None, image_rect, 0.0, None, sdl2.SDL_FLIP_HORIZONTAL)
    else:
        print("The fuck?")
        break
    current_tick: int = utils.time_int()
    if (current_tick - prev_tick) * utils.FRAMERATE < 1000:
        time.sleep((1000 / utils.FRAMERATE - current_tick + prev_tick) / 1000)
    renderer.present()
    prev_tick = utils.time_int()
