import math
import random
import pygame
from pygame.constants import KEYDOWN, K_ESCAPE, K_SPACE, QUIT, K_UP, K_DOWN, K_LEFT, K_RIGHT

from sound_manager import SoundManager

# Configuration
SIZE = 40           # Taille d'une case (px)
WIDTH = 1000        # Largeur de la fenêtre
HEIGHT = 600        # Hauteur de la fenêtre

# Vitesse progressive
FPS_START      = 5
FPS_MAX        = 20  # Plafond de vitesse
FPS_STEP       = 1   # +1 FPS par palier
SCORE_PER_STEP = 3

# Couleurs du serpent (style néon vert)
SNAKE_BODY_COLOR = (50, 205, 50)
SNAKE_OUTLINE    = (0,   0,   0)
SNAKE_HEAD_COLOR = (34, 160,  34)
SNAKE_EYE_COLOR  = (255, 255, 255)
SNAKE_PUPIL      = (0,   0,   0)

BG_COLOR    = (30, 30, 30)
GRID_COLOR  = (40, 40, 40)
SCORE_COLOR = (220, 220, 220)

RADIUS = SIZE // 2 - 2


# Classe Apple
class Apple:
    def __init__(self, parent_screen):
        self.parent_screen = parent_screen
        self.use_image = False

        for path in ('ressources/apple.png', 'ressources/apple.jpg'):
            try:
                raw = pygame.image.load(path).convert_alpha()
                self.image = pygame.transform.smoothscale(raw, (SIZE, SIZE))
                self.use_image = True
                print(f"[Apple] Image chargée : {path}")
                break
            except Exception:
                continue

        self.x = SIZE * 3
        self.y = SIZE * 3

    def draw(self):
        if self.use_image:
            self.parent_screen.blit(self.image, (self.x, self.y))
        else:
            cx = self.x + SIZE // 2
            cy = self.y + SIZE // 2
            pygame.draw.circle(self.parent_screen, (220, 20, 60), (cx, cy), SIZE // 2 - 2)
            pygame.draw.circle(self.parent_screen, (255, 80, 80), (cx - 4, cy - 4), 6)

    def move(self, snake_positions: list):
        cols = WIDTH // SIZE
        rows = HEIGHT // SIZE
        occupied = set(snake_positions)
        while True:
            nx = random.randint(0, cols - 1) * SIZE
            ny = random.randint(0, rows - 1) * SIZE
            if (nx, ny) not in occupied:
                self.x, self.y = nx, ny
                break


# Classe Snake
class Snake:
    HEAD_ANGLES = {
        'down':  0,
        'up':    180,
        'left':  90,
        'right': 270,
    }

    def __init__(self, surface):
        self.parent_screen = surface

        self.head_image = None
        try:
            raw = pygame.image.load('ressources/head.png').convert_alpha()
            self.head_image = pygame.transform.smoothscale(raw, (SIZE, SIZE))
            print("[Snake] head.png chargée avec succès.")
        except Exception as e:
            print(f"[Snake] head.png non disponible, yeux pygame utilisés : {e}")

        # Position initiale
        start_x = (WIDTH  // SIZE // 2) * SIZE
        start_y = (HEIGHT // SIZE // 2) * SIZE
        self.x = [start_x, start_x, start_x]
        self.y = [start_y, start_y - SIZE, start_y - SIZE * 2]
        self.length = 3
        self.direction = 'down'

    # Dessin

    def _draw_segment(self, surface, cx, cy, color, radius):
        pygame.draw.circle(surface, SNAKE_OUTLINE, (cx, cy), radius + 2)
        pygame.draw.circle(surface, color, (cx, cy), radius)

    def _draw_link(self, surface, x1, y1, x2, y2, color, radius):
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        nx, ny = -dy / dist * radius, dx / dist * radius
        pts = [
            (x1 + nx, y1 + ny),
            (x1 - nx, y1 - ny),
            (x2 - nx, y2 - ny),
            (x2 + nx, y2 + ny),
        ]
        outline_pts = [
            (p[0] + math.copysign(2, p[0] - (x1 + x2) / 2),
             p[1] + math.copysign(2, p[1] - (y1 + y2) / 2)) for p in pts
        ]
        pygame.draw.polygon(surface, SNAKE_OUTLINE, outline_pts)
        pygame.draw.polygon(surface, color, pts)

    def _draw_eyes(self, surface, hx, hy):
        offsets = {
            'up':    [(-6, -6), (6, -6)],
            'down':  [(-6,  6), (6,  6)],
            'left':  [(-8, -5), (-8,  5)],
            'right': [( 8, -5), ( 8,  5)],
        }
        for ox, oy in offsets.get(self.direction, [(-6, -6), (6, -6)]):
            ex, ey = hx + ox, hy + oy
            pygame.draw.circle(surface, SNAKE_EYE_COLOR, (ex, ey), 5)
            pygame.draw.circle(surface, SNAKE_PUPIL, (ex, ey), 2)

    def draw(self):
        surface = self.parent_screen

        # Liaisons entre segments
        for i in range(self.length - 1, 0, -1):
            x1 = self.x[i]     + SIZE // 2
            y1 = self.y[i]     + SIZE // 2
            x2 = self.x[i - 1] + SIZE // 2
            y2 = self.y[i - 1] + SIZE // 2
            self._draw_link(surface, x1, y1, x2, y2, SNAKE_BODY_COLOR, RADIUS)

        #Cercles
        for i in range(self.length - 1, -1, -1):
            cx = self.x[i] + SIZE // 2
            cy = self.y[i] + SIZE // 2
            color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_BODY_COLOR
            self._draw_segment(surface, cx, cy, color, RADIUS)

        # Tête : image custom ou yeux dessinés
        hx = self.x[0] + SIZE // 2
        hy = self.y[0] + SIZE // 2

        if self.head_image:
            angle   = self.HEAD_ANGLES.get(self.direction, 0)
            rotated = pygame.transform.rotate(self.head_image, angle)
            rect    = rotated.get_rect(center=(hx, hy))
            surface.blit(rotated, rect)
        else:
            self._draw_eyes(surface, hx, hy)

    # Mouvement

    def walk(self):
        for i in range(self.length - 1, 0, -1):
            self.x[i] = self.x[i - 1]
            self.y[i] = self.y[i - 1]

        if self.direction == 'left':
            self.x[0] -= SIZE
        elif self.direction == 'right':
            self.x[0] += SIZE
        elif self.direction == 'up':
            self.y[0] -= SIZE
        elif self.direction == 'down':
            self.y[0] += SIZE

    def increase_length(self):
        self.length += 1
        self.x.append(self.x[-1])
        self.y.append(self.y[-1])

    def get_positions(self):
        return [(self.x[i], self.y[i]) for i in range(self.length)]


# Classe Game
class Game:
    STATE_PLAYING   = 'playing'
    STATE_GAME_OVER = 'game_over'

    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))

        try:
            icon = pygame.image.load('ressources/snaky.png')
            pygame.display.set_icon(icon)
        except Exception:
            pass

        pygame.display.set_caption("Snake Game")

        self.font_score    = pygame.font.SysFont('arial', 28, bold=True)
        self.font_title    = pygame.font.SysFont('arial', 72, bold=True)
        self.font_subtitle = pygame.font.SysFont('arial', 36)
        self.font_final    = pygame.font.SysFont('arial', 44, bold=True)
        self.font_level    = pygame.font.SysFont('arial', 22)

        try:
            self.bg = pygame.image.load('ressources/background.jpg').convert()
            self.bg = pygame.transform.smoothscale(self.bg, (WIDTH, HEIGHT))
        except Exception:
            self.bg = None

        self.sound      = SoundManager()
        self.clock      = pygame.time.Clock()
        self.high_score = 0
        self.state      = self.STATE_PLAYING
        self._reset()

    #  Réinitialisation

    def _reset(self):
        self.snake       = Snake(self.surface)
        self.apple       = Apple(self.surface)
        self.score       = 0
        self.current_fps = FPS_START

    # Vitesse dynamique

    def _update_fps(self):
        self.current_fps = min(
            FPS_START + (self.score // SCORE_PER_STEP) * FPS_STEP,
            FPS_MAX
        )

    # Collision

    def _is_collision(self, x1, y1, x2, y2):
        return x1 == x2 and y1 == y2

    # Rendu

    def _draw_background(self):
        if self.bg:
            self.surface.blit(self.bg, (0, 0))
        else:
            self.surface.fill(BG_COLOR)
            for col in range(0, WIDTH, SIZE):
                pygame.draw.line(self.surface, GRID_COLOR, (col, 0), (col, HEIGHT))
            for row in range(0, HEIGHT, SIZE):
                pygame.draw.line(self.surface, GRID_COLOR, (0, row), (WIDTH, row))

    def _draw_hud(self):
        # Score + meilleur score (coin haut droit)
        score_text = self.font_score.render(
            f"Score : {self.score}   |   Meilleur : {self.high_score}", True, SCORE_COLOR)
        pad  = 8
        rect = score_text.get_rect(topright=(WIDTH - 10, 10))
        bg_r = rect.inflate(pad * 2, pad * 2)
        bg_s = pygame.Surface(bg_r.size, pygame.SRCALPHA)
        bg_s.fill((0, 0, 0, 120))
        self.surface.blit(bg_s, bg_r.topleft)
        self.surface.blit(score_text, rect)

        # Niveau de vitesse (coin bas gauche)
        level     = self.score // SCORE_PER_STEP + 1
        level_txt = self.font_level.render(f"Niveau vitesse : {level}", True, (160, 160, 160))
        self.surface.blit(level_txt, (10, HEIGHT - 30))

    def _draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.surface.blit(overlay, (0, 0))

        cx = WIDTH // 2

        title = self.font_title.render("GAME OVER", True, (220, 50, 50))
        self.surface.blit(title, title.get_rect(center=(cx, HEIGHT // 2 - 100)))

        score_txt = self.font_final.render(f"Score : {self.score}", True, (255, 215, 0))
        self.surface.blit(score_txt, score_txt.get_rect(center=(cx, HEIGHT // 2 - 10)))

        if self.score > 0 and self.score >= self.high_score:
            hs_txt = self.font_subtitle.render("Nouveau record !", True, (50, 205, 50))
        else:
            hs_txt = self.font_subtitle.render(
                f"Meilleur score : {self.high_score}", True, SCORE_COLOR)
        self.surface.blit(hs_txt, hs_txt.get_rect(center=(cx, HEIGHT // 2 + 55)))

        hint = self.font_subtitle.render(
            "ESPACE pour rejouer  |  ECHAP pour quitter", True, (180, 180, 180))
        self.surface.blit(hint, hint.get_rect(center=(cx, HEIGHT // 2 + 120)))

    #  Logique de jeu -

    def _trigger_game_over(self):
        self.sound.play_crash()
        if self.score > self.high_score:
            self.high_score = self.score
        self.state = self.STATE_GAME_OVER

    def _play_frame(self):
        self._draw_background()
        self.snake.walk()
        self.apple.draw()
        self.snake.draw()
        self._draw_hud()

        hx, hy = self.snake.x[0], self.snake.y[0]

        # Collision pomme
        if self._is_collision(hx, hy, self.apple.x, self.apple.y):
            self.sound.play_ding()
            self.apple.move(self.snake.get_positions())
            self.snake.increase_length()
            self.score += 1
            self._update_fps()   # ← accélération progressive

        # Collision murs
        if hx < 0 or hx >= WIDTH or hy < 0 or hy >= HEIGHT:
            self._trigger_game_over()
            return

        # Collision propre corps (
        for i in range(3, self.snake.length):
            if self._is_collision(hx, hy, self.snake.x[i], self.snake.y[i]):
                self._trigger_game_over()
                return

    #  Boucle principale -

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False

                    if self.state == self.STATE_GAME_OVER and event.key == K_SPACE:
                        self._reset()
                        self.state = self.STATE_PLAYING

                    if self.state == self.STATE_PLAYING:
                        d = self.snake.direction
                        if event.key == K_UP    and d != 'down':
                            self.snake.direction = 'up'
                        if event.key == K_DOWN  and d != 'up':
                            self.snake.direction = 'down'
                        if event.key == K_LEFT  and d != 'right':
                            self.snake.direction = 'left'
                        if event.key == K_RIGHT and d != 'left':
                            self.snake.direction = 'right'

            if self.state == self.STATE_PLAYING:
                self._play_frame()
            elif self.state == self.STATE_GAME_OVER:
                self._draw_background()
                self.apple.draw()
                self.snake.draw()
                self._draw_hud()
                self._draw_game_over()

            pygame.display.flip()
            self.clock.tick(self.current_fps)

        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()