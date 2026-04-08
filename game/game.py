import pygame
import sys
import random
import os

# Инициализация
pygame.init()
pygame.mixer.init()

# Базовые константы (для расчетов)
BASE_WIDTH, BASE_HEIGHT = 400, 600
FPS = 60
FULLSCREEN = False

# Цвета
YELLOW = (255, 255, 0)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (135, 206, 235)

# Настройка экрана
screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

# Загрузка изображения птицы
try:
    bird_img_orig = pygame.image.load("bird.png").convert_alpha()
except:
    bird_img_orig = pygame.Surface((40, 30))
    bird_img_orig.fill((255, 255, 0))

# Загрузка звуков
try:
    sound_settings = pygame.mixer.Sound("sound_settings.mp3")
except:
    sound_settings = None

try:
    sound_death = pygame.mixer.Sound("sound_death.mp3")
except:
    sound_death = None


def get_screen_size():
    """Возвращает текущие размеры экрана"""
    return screen.get_width(), screen.get_height()


def scale_value(value, is_height=False):
    """Масштабирует значение относительно базового размера"""
    w, h = get_screen_size()
    if is_height:
        return int(value * h / BASE_HEIGHT)
    else:
        return int(value * w / BASE_WIDTH)


def get_scaled_font(base_size):
    """Возвращает шрифт нужного размера с учетом масштаба"""
    size = scale_value(base_size)
    return pygame.font.Font(None, size)


def toggle_fullscreen():
    """Переключает полноэкранный режим"""
    global screen, FULLSCREEN
    FULLSCREEN = not FULLSCREEN
    if FULLSCREEN:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)


def set_volume_max():
    """Пытается выставить громкость системы на 100% (Windows)"""
    try:
        if os.name == 'nt':
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(1.0, None)
    except Exception as e:
        print(f"Не удалось изменить громкость: {e}")


def draw_text(text, font, color, x, y, center=True):
    surface = font.render(text, True, color)
    if center:
        rect = surface.get_rect(center=(x, y))
    else:
        rect = surface.get_rect(topleft=(x, y))
    screen.blit(surface, rect)


def button(text, x, y, w, h, action=None):
    """Адаптивная кнопка"""
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    # Масштабируем координаты и размеры
    sw, sh = get_screen_size()
    scaled_x = int(x * sw / BASE_WIDTH)
    scaled_y = int(y * sh / BASE_HEIGHT)
    scaled_w = int(w * sw / BASE_WIDTH)
    scaled_h = int(h * sh / BASE_HEIGHT)
    
    rect = pygame.Rect(scaled_x - scaled_w//2, scaled_y - scaled_h//2, scaled_w, scaled_h)
    
    # Шрифт масштабируем
    font = get_scaled_font(40)
    
    if rect.collidepoint(mouse):
        color = (0, 150, 0)
        if click[0] == 1 and action is not None:
            return action
    else:
        color = GREEN
        
    pygame.draw.rect(screen, color, rect, border_radius=scale_value(10))
    pygame.draw.rect(screen, BLACK, rect, scale_value(3), border_radius=scale_value(10))
    draw_text(text, font, BLACK, scaled_x, scaled_y)
    return None


def settings_screen():
    """Экран настроек с предупреждением и звуком"""
    global screen
    set_volume_max()
    if sound_settings:
        sound_settings.play()
        sound_length = sound_settings.get_length() * 1000
    else:
        sound_length = 2000
    
    start_time = pygame.time.get_ticks()
    
    while pygame.time.get_ticks() - start_time < sound_length:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        
        screen.fill(YELLOW)
        
        sw, sh = get_screen_size()
        font = get_scaled_font(30)
        draw_text("НЕ ТЫКАЙ ЛИШНИЕ КНОПКИ!", font, BLACK, sw//2, sh//2)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    return "menu"


class Bird:
    def __init__(self):
        self.reset()
        
    def reset(self):
        sw, sh = get_screen_size()
        self.y = sh // 2
        self.velocity = 0
        self.gravity = 0.5 * (sh / BASE_HEIGHT)  # Масштабируем гравитацию
        self.lift = -10 * (sh / BASE_HEIGHT)     # Масштабируем подъем
        
    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity
        
    def flap(self):
        self.velocity = self.lift
        
    def draw(self):
        sw, sh = get_screen_size()
        # Масштабируем птицу
        bird_width = int(40 * sw / BASE_WIDTH)
        bird_height = int(30 * sh / BASE_HEIGHT)
        scaled_bird = pygame.transform.scale(bird_img_orig, (bird_width, bird_height))
        
        bird_x = int(50 * sw / BASE_WIDTH)
        screen.blit(scaled_bird, (bird_x, int(self.y)))
        
    def get_rect(self):
        sw, sh = get_screen_size()
        bird_width = int(40 * sw / BASE_WIDTH)
        bird_height = int(30 * sh / BASE_HEIGHT)
        bird_x = int(50 * sw / BASE_WIDTH)
        return pygame.Rect(bird_x, self.y, bird_width, bird_height)


class Pipe:
    def __init__(self, x):
        sw, sh = get_screen_size()
        self.x = x
        self.width = int(60 * sw / BASE_WIDTH)
        self.gap = int(150 * sh / BASE_HEIGHT)
        self.top = random.randint(int(50 * sh / BASE_HEIGHT), sh - self.gap - int(50 * sh / BASE_HEIGHT))
        self.bottom = self.top + self.gap
        self.speed = 4 * (sw / BASE_WIDTH)  # Масштабируем скорость
        self.passed = False
        
    def update(self):
        self.x -= self.speed
        
    def draw(self):
        sw, sh = get_screen_size()
        pygame.draw.rect(screen, GREEN, (self.x, 0, self.width, self.top))
        pygame.draw.rect(screen, GREEN, (self.x, self.bottom, self.width, sh - self.bottom))
        
    def offscreen(self):
        return self.x < -self.width
    
    def collide(self, bird_rect):
        top_rect = pygame.Rect(self.x, 0, self.width, self.top)
        bottom_rect = pygame.Rect(self.x, self.bottom, self.width, screen.get_height() - self.bottom)
        return bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect)


def game_screen():
    """Игровой процесс Flappy Bird"""
    global screen
    sw, sh = get_screen_size()
    
    bird = Bird()
    pipes = []
    pipe_timer = 0
    score = 0
    ground_y = sh - int(50 * sh / BASE_HEIGHT)
    
    running = True
    while running:
        clock.tick(FPS)
        
        sw, sh = get_screen_size()
        ground_y = sh - int(50 * sh / BASE_HEIGHT)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.flap()
                elif event.key == pygame.K_F11:
                    toggle_fullscreen()
                    sw, sh = get_screen_size()
                    ground_y = sh - int(50 * sh / BASE_HEIGHT)
            if event.type == pygame.MOUSEBUTTONDOWN:
                bird.flap()
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                sw, sh = event.w, event.h
                ground_y = sh - int(50 * sh / BASE_HEIGHT)
        
        bird.update()
        
        pipe_timer += 1
        if pipe_timer > 90:
            pipes.append(Pipe(sw))
            pipe_timer = 0
            
        for pipe in pipes[:]:
            pipe.update()
            if pipe.offscreen():
                pipes.remove(pipe)
                
        bird_rect = bird.get_rect()
        
        for pipe in pipes:
            if pipe.collide(bird_rect):
                if sound_death:
                    sound_death.play()
                return "menu"
                
        if bird.y <= 0 or bird.y + bird_rect.height >= ground_y:
            if sound_death:
                sound_death.play()
            return "menu"
        
        screen.fill(BLUE)
        
        for pipe in pipes:
            pipe.draw()
        
        # Земля
        ground_height = sh - ground_y
        pygame.draw.rect(screen, (0, 100, 0), (0, ground_y, sw, ground_height))
        pygame.draw.rect(screen, BLACK, (0, ground_y, sw, 3))
        
        bird.draw()
        
        for pipe in pipes:
            if not pipe.passed and pipe.x + pipe.width < bird_rect.x:
                pipe.passed = True
                score += 1
        
        font = get_scaled_font(40)
        draw_text(str(score), font, WHITE, sw//2, int(50 * sh / BASE_HEIGHT))
        
        pygame.display.flip()
    
    return "menu"


def main_menu():
    """Главное меню"""
    global screen
    while True:
        sw, sh = get_screen_size()
        screen.fill(YELLOW)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        
        # Кнопки с адаптивными координатами
        btn_width = 200
        btn_height = 60
        spacing = 80
        
        if button("ИГРАТЬ", BASE_WIDTH//2, BASE_HEIGHT//2 - spacing, btn_width, btn_height, "game"):
            return "game"
        if button("НАСТРОЙКИ", BASE_WIDTH//2, BASE_HEIGHT//2, btn_width, btn_height, "settings"):
            return "settings"
        if button("ВЫХОД", BASE_WIDTH//2, BASE_HEIGHT//2 + spacing, btn_width, btn_height, "exit"):
            pygame.quit()
            sys.exit()
            
        pygame.display.flip()
        clock.tick(FPS)


current_screen = "menu"

while True:
    if current_screen == "menu":
        current_screen = main_menu()
    elif current_screen == "settings":
        current_screen = settings_screen()
    elif current_screen == "game":
        current_screen = game_screen()
