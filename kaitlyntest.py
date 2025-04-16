# THIS ONE WORKS
import pygame
import sys
import datetime
import random
import os
import time

# Setup driver settings (for systems using framebuffer; remove if not needed)
os.environ["SDL_VIDEODRIVERS"] = "fbcon"
os.environ["SDL_FBDEV"] = "/dev/fb1"

pygame.init()

# ----------------------
# Global Settings
# ----------------------
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 320
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Xi Smartwatch")

# Colors
BLACK      = (0, 0, 0)
WHITE      = (255, 255, 255)
GRAY       = (180, 180, 180)
RED        = (161, 73, 67)
GOLD       = (194, 148, 83)
DARK_GRAY  = (30, 30, 30)
BASE       = (107, 106, 105)
LIGHT_GRAY = (217, 217, 217)
BLUE       = (100, 149, 237)

# Touch calibration settings
SWAP_XY = True       # Set to True if X and Y axes are swapped
INVERT_X = False     # Set to True if X axis is inverted
INVERT_Y = False     # Set to True if Y axis is inverted

# ----------------------
# Fonts Initialization (make sure fonts are loaded after pygame.init())
# ----------------------
pygame.font.init()
font_time   = pygame.font.SysFont("Rubik", 88)
font_date   = pygame.font.SysFont("Rubik", 38)
font_button = pygame.font.SysFont("Rubik", 30)
app_font = pygame.font.SysFont(None, 30)
numgen_font       = pygame.font.SysFont(None, 36)
numgen_large_font = pygame.font.SysFont(None, 48)

# ----------------------
# Screen States
# ----------------------
HOME_SCREEN = 0
APP_SCREEN = 1
NUMGEN_SCREEN = 3
COMPLEX_APP_SCREEN = 4
TIMER_SCREEN = 5   # New state for the timer/stopwatch app

current_screen = HOME_SCREEN
transition_in_progress = False

# ----------------------
# Button settings for home screen
# ----------------------
button_width = 180
button_height = 70
button_x = (SCREEN_WIDTH - button_width) // 2
button_y = 200
button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

# ----------------------
# App Menu (scrollable) settings
# ----------------------
menu_items = ["Timer", "Number Generator", "Golden Pony"]
item_height = 65
spacing = 25
visible_items = 3
scroll_offset = 0
min_scroll = -(len(menu_items) - visible_items) * (item_height + spacing)
max_scroll = 0

# ----------------------
# Helper Functions for Main App
# ----------------------
def draw_rounded_rect(surface, rect, color, radius):
    """
    Draws a filled rectangle with rounded corners.
    """
    rect = pygame.Rect(rect)
    inner_rect = rect.inflate(-2 * radius, -2 * radius)
    pygame.draw.rect(surface, color, inner_rect)
    top_rect = pygame.Rect(rect.left + radius, rect.top, rect.width - 2 * radius, radius)
    bottom_rect = pygame.Rect(rect.left + radius, rect.bottom - radius, rect.width - 2 * radius, radius)
    left_rect = pygame.Rect(rect.left, rect.top + radius, radius, rect.height - 2 * radius)
    right_rect = pygame.Rect(rect.right - radius, rect.top + radius, radius, rect.height - 2 * radius)
    pygame.draw.rect(surface, color, top_rect)
    pygame.draw.rect(surface, color, bottom_rect)
    pygame.draw.rect(surface, color, left_rect)
    pygame.draw.rect(surface, color, right_rect)
    pygame.draw.circle(surface, color, (rect.left + radius, rect.top + radius), radius)
    pygame.draw.circle(surface, color, (rect.right - radius, rect.top + radius), radius)
    pygame.draw.circle(surface, color, (rect.left + radius, rect.bottom - radius), radius)
    pygame.draw.circle(surface, color, (rect.right - radius, rect.bottom - radius), radius)

def draw_rounded_rect_outline(surface, rect, color, radius, width):
    """
    Draws an outline of a rounded rectangle by drawing successive rounded rects.
    """
    for i in range(width):
        shrunk_rect = pygame.Rect(rect.left + i, rect.top + i, rect.width - 2 * i, rect.height - 2 * i)
        current_radius = max(0, radius - i)
        draw_rounded_rect(surface, shrunk_rect, color, current_radius)

def transform_coords(pos):
    """
    Transforms touch input coordinates based on calibration settings.
    """
    x, y = pos
    if SWAP_XY:
        x, y = y, x
    if INVERT_X:
        x = SCREEN_WIDTH - x
    if INVERT_Y:
        y = SCREEN_HEIGHT - y
    return (x, y)

def run_app_menu(surface):
    global scroll_offset
    clock = pygame.time.Clock()
    running = True
    dragging = False
    scroll_area = pygame.Rect(20, 20, SCREEN_WIDTH - 40, SCREEN_HEIGHT - 40)
    while running:
        surface.fill(BASE)
        layer_rect = pygame.Rect(10, 10, SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)
        draw_rounded_rect(surface, layer_rect, LIGHT_GRAY, 15)
        scroll_surface = surface.subsurface(scroll_area).copy()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        adjusted_mouse_y = mouse_y - scroll_area.y
        for i, item in enumerate(menu_items):
            y_pos = 10 + i * (item_height + spacing) + scroll_offset
            if 0 <= y_pos <= scroll_area.height - item_height:
                container_rect = pygame.Rect(0, y_pos, scroll_area.width, item_height)
                if container_rect.collidepoint(mouse_x - scroll_area.x, adjusted_mouse_y):
                    draw_rounded_rect(scroll_surface, container_rect, GOLD, 10)
                    text = app_font.render(item, True, RED)
                else:
                    draw_rounded_rect(scroll_surface, container_rect, RED, 10)
                    text = app_font.render(item, True, GOLD)
                text_rect = text.get_rect(center=container_rect.center)
                scroll_surface.blit(text, text_rect)
        surface.blit(scroll_surface, scroll_area.topleft)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if scroll_area.collidepoint(event.pos):
                    dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
                for i, item in enumerate(menu_items):
                    y_pos = 10 + i * (item_height + spacing) + scroll_offset
                    container_rect = pygame.Rect(0, y_pos, scroll_area.width, item_height)
                    if container_rect.collidepoint(event.pos[0] - scroll_area.x, event.pos[1] - scroll_area.y):
                        return item.lower().replace(" ", "")
            elif event.type == pygame.MOUSEMOTION and dragging:
                scroll_offset += event.rel[1]
                scroll_offset = max(min_scroll, min(scroll_offset, max_scroll))
        clock.tick(30)

# ----------------------
# Number Generator Functions
# ----------------------
slider_x = 50
slider_y = 150
slider_width = 400
slider_height = 5
knob_radius = 10
min_val = 1
max_val = 100

def get_value(knob_x):
    ratio = (knob_x - slider_x) / slider_width
    return int(min_val + ratio * (max_val - min_val))

def draw_slider(surface, knob_x):
    pygame.draw.rect(surface, WHITE, (slider_x, slider_y - slider_height // 2, slider_width, slider_height))
    pygame.draw.circle(surface, GOLD, (knob_x, slider_y), knob_radius)

def draw_button(surface, rect, text, hover):
    bg_color = GOLD if hover else RED
    text_color = RED if hover else GOLD
    draw_rounded_rect(surface, rect, bg_color, 10)
    txt = numgen_font.render(text, True, text_color)
    surface.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

def run_slider_screen(surface):
    knob_x = slider_x
    dragging = False
    generate_button = pygame.Rect(SCREEN_WIDTH // 2 - 75, 220, 150, 40)
    back_button = pygame.Rect(SCREEN_WIDTH // 2 - 30, 5, 80, 20)
    clock = pygame.time.Clock()
    while True:
        mouse_pos = pygame.mouse.get_pos()
        generate_hover = generate_button.collidepoint(mouse_pos)
        back_hover = back_button.collidepoint(mouse_pos)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if (knob_x - mx)**2 + (slider_y - my)**2 < (knob_radius * 2)**2:
                    dragging = True
                if generate_button.collidepoint(event.pos):
                    return get_value(knob_x)
                if back_button.collidepoint(event.pos):
                    return "back_to_app"
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
            elif event.type == pygame.MOUSEMOTION and dragging:
                mx, _ = event.pos
                knob_x = max(slider_x, min(slider_x + slider_width, mx))
        surface.fill(BASE)
        inner_rect = pygame.Rect(10, 10, SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)
        draw_rounded_rect(surface, inner_rect, LIGHT_GRAY, 15)
        draw_slider(surface, knob_x)
        value = get_value(knob_x)
        text = numgen_font.render(f"Max: {value}", True, WHITE)
        surface.blit(text, (knob_x - text.get_width() // 2, slider_y - 40))
        draw_button(surface, generate_button, "Generate", generate_hover)
        draw_button(surface, back_button, "Reset", back_hover)
        pygame.display.flip()
        clock.tick(60)

def run_num_gen_screen(surface):
    while True:
        max_number = run_slider_screen(surface)
        if max_number == "back_to_app":
            return "back_to_app"
        number = random.randint(1, max_number)
        back_button = pygame.Rect(SCREEN_WIDTH // 2 - 40, 5, 80, 30)
        clock = pygame.time.Clock()
        while True:
            mouse_pos = pygame.mouse.get_pos()
            back_hover = back_button.collidepoint(mouse_pos)
            surface.fill(BASE)
            inner_rect = pygame.Rect(10, 10, SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)
            draw_rounded_rect(surface, inner_rect, LIGHT_GRAY, 15)
            text = numgen_large_font.render(f"Number: {number}", True, GOLD)
            surface.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2,
                                SCREEN_HEIGHT // 2 - text.get_height() // 2))
            draw_button(surface, back_button, "Back", back_hover)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.collidepoint(event.pos):
                        return "back_to_slider"
            pygame.display.flip()
            clock.tick(60)

def run_complex_app_screen(surface):
    clock = pygame.time.Clock()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        surface.fill(DARK_GRAY)
        placeholder_text = font_button.render("Complex App Placeholder - Press any key", True, WHITE)
        rect = placeholder_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        surface.blit(placeholder_text, rect)
        pygame.display.flip()
        clock.tick(30)
    return True

# ----------------------
# Timer & Stopwatch App (Integrated from timer.py)
# ----------------------
# Note: This Button class (and its methods) is used only in the timer/stopwatch app.
class Button:
    def __init__(self, rect, text, image=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.image = image

    def draw(self):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        bg_color = GOLD if is_hovered else RED
        text_color = RED if is_hovered else GOLD
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        if self.image:
            image_rect = self.image.get_rect(center=self.rect.center)
            screen.blit(self.image, image_rect)
        else:
            text_surface = pygame.font.SysFont(None, 32).render(self.text, True, text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def is_pressed(self, pos):
        return self.rect.collidepoint(pos)

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{secs:02}"

def run_timer_app():
    mode = None
    running = False
    start_time = 0
    elapsed = 0
    timer_seconds = 0
    timer_display_value = 0

    default_timer_display_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 20, 200, 35)
    center_timer_display_rect = pygame.Rect(SCREEN_WIDTH // 2 - 190, SCREEN_HEIGHT // 2 - 60, 380, 120)
    timer_display_rect = default_timer_display_rect

    timer_btn = Button((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 60, 200, 50), "Timer")
    sw_btn = Button((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 10, 200, 50), "Stopwatch")

    start_btn = Button((40, 260, 120, 40), "Start")
    stop_btn = Button((180, 260, 120, 40), "Stop")
    reset_btn = Button((320, 260, 120, 40), "Restart")

    try:
        home_icon = pygame.image.load("home_icon.png")
        home_icon = pygame.transform.scale(home_icon, (24, 24))
    except Exception as e:
        print("home_icon.png not found; using text for Home button.")
        home_icon = None
    nav_btn_width = 80
    nav_btn = Button(((SCREEN_WIDTH - nav_btn_width) // 2, 5, nav_btn_width, 30), "Back", image=home_icon)

    x_center = SCREEN_WIDTH // 2
    y_start = 70
    column_width = 100
    row_height = 45

    time_labels = [
        ("+5h", "+5m", "+5s"),
        ("+1h", "+1m", "+1s"),
        ("-1h", "-1m", "-1s"),
        ("-5h", "-5m", "-5s")
    ]

    time_buttons = []
    for row_idx, row in enumerate(time_labels):
        for col_idx, label in enumerate(row):
            x = x_center + (col_idx - 1) * column_width - 35
            y = y_start + row_idx * row_height
            time_buttons.append(Button((x, y, 70, 40), label))

    clock = pygame.time.Clock()
    while True:
        screen.fill(LIGHT_GRAY)
        layer_rect = pygame.Rect(10, 10, SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)
        pygame.draw.rect(screen, LIGHT_GRAY, layer_rect, border_radius=15)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if nav_btn.is_pressed(pos):
                    # Exit timer app and return to main app
                    return "back_to_app"
                else:
                    if mode is None:
                        if timer_btn.is_pressed(pos):
                            mode = "Timer"
                            timer_display_value = timer_seconds
                            timer_display_rect = default_timer_display_rect
                        elif sw_btn.is_pressed(pos):
                            mode = "Stopwatch"
                            elapsed = 0
                            timer_display_value = 0
                            running = False
                    else:
                        if reset_btn.is_pressed(pos):
                            running = False
                            elapsed = 0
                            timer_seconds = 0
                            timer_display_value = 0
                            timer_display_rect = default_timer_display_rect
                            mode = None
                        elif start_btn.is_pressed(pos):
                            if not running:
                                start_time = time.time()
                                running = True
                                if mode == "Stopwatch":
                                    start_time -= elapsed
                                elif mode == "Timer":
                                    elapsed = 0
                                    timer_display_rect = center_timer_display_rect
                        elif stop_btn.is_pressed(pos):
                            if running:
                                elapsed = time.time() - start_time
                                running = False
                                if mode == "Timer":
                                    timer_display_value = max(0, timer_seconds - elapsed)
                                    timer_display_rect = default_timer_display_rect
                                elif mode == "Stopwatch":
                                    timer_display_value = elapsed
                        if mode == "Timer" and not running:
                            for b in time_buttons:
                                if b.is_pressed(pos):
                                    label = b.text
                                    val = int(label[1:-1])
                                    if label.startswith("+"):
                                        if "h" in label:
                                            timer_seconds += val * 3600
                                        elif "m" in label:
                                            timer_seconds += val * 60
                                        elif "s" in label:
                                            timer_seconds += val
                                    elif label.startswith("-"):
                                        if "h" in label:
                                            timer_seconds = max(0, timer_seconds - val * 3600)
                                        elif "m" in label:
                                            timer_seconds = max(0, timer_seconds - val * 60)
                                        elif "s" in label:
                                            timer_seconds = max(0, timer_seconds - val)
                                    timer_display_value = timer_seconds
        if mode == "Timer":
            if running:
                elapsed = time.time() - start_time
                timer_display_value = max(0, timer_seconds - elapsed)
        elif mode == "Stopwatch":
            if running:
                timer_display_value = time.time() - start_time

        if mode is not None:
            if mode == "Stopwatch":
                display_rect = center_timer_display_rect
                font_to_use = pygame.font.SysFont(None, 72)
            else:
                display_rect = timer_display_rect
                font_to_use = pygame.font.SysFont(None, 32) if not running else pygame.font.SysFont(None, 72)
            pygame.draw.rect(screen, RED, display_rect, border_radius=12)
            time_surface = font_to_use.render(format_time(timer_display_value), True, GOLD)
            time_rect = time_surface.get_rect(center=display_rect.center)
            screen.blit(time_surface, time_rect)
            start_btn.draw()
            stop_btn.draw()
            reset_btn.draw()
            if mode == "Timer" and not running:
                for b in time_buttons:
                    b.draw()
        else:
            timer_btn.draw()
            sw_btn.draw()
            nav_btn.draw()
        pygame.display.flip()
        clock.tick(30)

# ----------------------
# Main Loop for Smartwatch
# ----------------------
def main():
    global current_screen, transition_in_progress, scroll_offset
    clock = pygame.time.Clock()
    running = True
    while running:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and not transition_in_progress:
                transformed_pos = transform_coords((mouse_x, mouse_y))
                if current_screen == HOME_SCREEN and button_rect.collidepoint(transformed_pos):
                    transition_in_progress = True
                    current_screen = APP_SCREEN
        screen.fill(BASE)
        if current_screen == HOME_SCREEN:
            outer_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
            draw_rounded_rect_outline(screen, outer_rect, BASE, 15, 4)
            inner_rect = pygame.Rect(10, 10, SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)
            draw_rounded_rect(screen, inner_rect, LIGHT_GRAY, 15)
            now = datetime.datetime.now()
            time_str = now.strftime("%I:%M")
            date_str = now.strftime("%A, %B %d").lstrip("0").replace(" 0", " ")
            time_surface = font_time.render(time_str, True, GOLD)
            time_rect = time_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
            screen.blit(time_surface, time_rect)
            date_surface = font_date.render(date_str, True, GOLD)
            date_rect = date_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
            screen.blit(date_surface, date_rect)
            if button_rect.collidepoint(mouse_x, mouse_y):
                button_color = GOLD
                text_color = RED
            else:
                button_color = RED
                text_color = GOLD
            draw_rounded_rect(screen, button_rect, button_color, 10)
            button_text_surface = font_button.render("ENTER", True, text_color)
            button_text_rect = button_text_surface.get_rect(center=button_rect.center)
            screen.blit(button_text_surface, button_text_rect)
        elif current_screen == APP_SCREEN:
            selected_app = run_app_menu(screen)
            transition_in_progress = True
            if selected_app == "timer":
                current_screen = TIMER_SCREEN
            elif selected_app == "numbergenerator":
                current_screen = NUMGEN_SCREEN
                transition_in_progress = True
            elif selected_app == "fitnesstracker":
                current_screen = HOME_SCREEN
        elif current_screen == TIMER_SCREEN:
            back_to_app = run_timer_app()
            if back_to_app == "back_to_app":
                current_screen = APP_SCREEN
                transition_in_progress = True
        elif current_screen == NUMGEN_SCREEN:
            back_to_app = run_num_gen_screen(screen)
            if back_to_app == "back_to_slider":
                current_screen = APP_SCREEN
                transition_in_progress = True
        elif current_screen == COMPLEX_APP_SCREEN:
            back_to_app = run_complex_app_screen(screen)
            if back_to_app:
                current_screen = APP_SCREEN
                transition_in_progress = True
        pygame.display.flip()
        clock.tick(30)
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
