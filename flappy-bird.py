import math
import random
import sys
import json
import os
from enum import Enum

import pygame

WIDTH, HEIGHT = (800, 600)
FPS = 60

SKY = (105, 190, 235)
GROUND = (145, 92, 45)
GROUND_TOP = (95, 155, 55)
PIPE_GREEN = (36, 165, 64)
PIPE_DARK = (22, 115, 45)
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
YELLOW = (245, 205, 55)
ORANGE = (230, 120, 35)

GROUND_HEIGHT = 80
BIRD_X = 190
PIPE_WIDTH = 82
PIPE_GAP = 185
PIPE_INTERVAL = 1450
PIPE_SPEED = 230
GRAVITY = 1450
FLAP_FORCE = -470

RESTART_DELAY = 0.7
HIGHSCORE_FILE = "highscore.json"
SOUNDS_DIR = "sounds"


class GameState(Enum):
    START = 1
    PLAYING = 2
    GAME_OVER = 3


class SoundManager:
    def __init__(self):
        self.enabled = False
        self.flap = None
        self.score = None
        self.hit = None

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            self.enabled = True

            self.flap = self.load_sound("flap.wav")
            self.score = self.load_sound("score.wav")
            self.hit = self.load_sound("hit.wav")

        except pygame.error:
            self.enabled = False

    def load_sound(self, filename):
        path = os.path.join(SOUNDS_DIR, filename)

        if not os.path.isfile(path):
            return None

        try:
            return pygame.mixer.Sound(path)
        except pygame.error:
            return None

    def play(self, sound):
        if self.enabled and sound:
            try:
                sound.play()
            except pygame.error:
                pass


class Bird:
    def __init__(self):
        self.x = BIRD_X
        self.y = HEIGHT // 2
        self.radius_x = 24
        self.radius_y = 18
        self.velocity = 0
        self.wing_timer = 0

    def flap(self):
        self.velocity = FLAP_FORCE

    def update(self, dt):
        self.velocity += GRAVITY * dt
        self.y += self.velocity * dt
        self.wing_timer += dt * 12

    def draw(self, surface):
        angle = max(-28, min(70, -self.velocity * 0.08))

        bird_surface = pygame.Surface((76, 58), pygame.SRCALPHA)
        body_rect = pygame.Rect(14, 14, 44, 34)

        pygame.draw.ellipse(bird_surface, YELLOW, body_rect)
        pygame.draw.ellipse(bird_surface, BLACK, body_rect, 2)

        wing_offset = math.sin(self.wing_timer) * 7
        wing_points = [
            (28, 31),
            (5, 24 + wing_offset),
            (25, 42)
        ]

        pygame.draw.polygon(bird_surface, ORANGE, wing_points)
        pygame.draw.polygon(bird_surface, BLACK, wing_points, 2)

        pygame.draw.circle(bird_surface, WHITE, (50, 23), 7)
        pygame.draw.circle(bird_surface, BLACK, (52, 24), 3)

        pygame.draw.polygon(
            bird_surface, ORANGE,
            [(58, 29), (74, 34), (58, 39)]
        )

        pygame.draw.polygon(
            bird_surface, BLACK,
            [(58, 29), (74, 34), (58, 39)], 2
        )

        rotated = pygame.transform.rotate(bird_surface, angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        surface.blit(rotated, rect)

    @property
    def rect(self):
        return pygame.Rect(
            self.x - self.radius_x,
            self.y - self.radius_y,
            self.radius_x * 2,
            self.radius_y * 2
        )


class PipePair:
    def __init__(self, x):
        min_top = 80
        max_top = HEIGHT - GROUND_HEIGHT - PIPE_GAP - 80

        self.x = x
        self.top_height = random.randint(min_top, max_top)
        self.passed = False

    def update(self, dt):
        self.x -= PIPE_SPEED * dt

    def draw(self, surface):
        top_rect = pygame.Rect(
            self.x, 0, PIPE_WIDTH, self.top_height
        )

        bottom_y = self.top_height + PIPE_GAP

        bottom_rect = pygame.Rect(
            self.x,
            bottom_y,
            PIPE_WIDTH,
            HEIGHT - GROUND_HEIGHT - bottom_y
        )

        for rect in [top_rect, bottom_rect]:
            pygame.draw.rect(surface, PIPE_GREEN, rect)
            pygame.draw.rect(surface, PIPE_DARK, rect, 4)

        cap_h = 26
        cap_pad = 8

        top_cap = pygame.Rect(
            self.x - cap_pad,
            self.top_height - cap_h,
            PIPE_WIDTH + cap_pad * 2,
            cap_h
        )

        bottom_cap = pygame.Rect(
            self.x - cap_pad,
            bottom_y,
            PIPE_WIDTH + cap_pad * 2,
            cap_h
        )

        for rect in [top_cap, bottom_cap]:
            pygame.draw.rect(surface, PIPE_GREEN, rect)
            pygame.draw.rect(surface, PIPE_DARK, rect, 4)

    def collides_with(self, bird_rect):
        top_rect = pygame.Rect(
            self.x, 0, PIPE_WIDTH, self.top_height
        )

        bottom_y = self.top_height + PIPE_GAP

        bottom_rect = pygame.Rect(
            self.x,
            bottom_y,
            PIPE_WIDTH,
            HEIGHT - GROUND_HEIGHT - bottom_y
        )

        return (
            bird_rect.colliderect(top_rect)
            or bird_rect.colliderect(bottom_rect)
        )

    @property
    def off_screen(self):
        return self.x + PIPE_WIDTH < 0


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Flappy Bird")

        self.clock = pygame.time.Clock()

        self.font_big = pygame.font.SysFont(
            "arial", 56, bold=True
        )
        self.font_mid = pygame.font.SysFont(
            "arial", 32, bold=True
        )
        self.font_small = pygame.font.SysFont(
            "arial", 24
        )

        self.sounds = SoundManager()

        self.best_score = self.load_highscore()
        self.restart_timer = 0

        self.state = GameState.START
        self.reset()

    def load_highscore(self):
        try:
            if not os.path.exists(HIGHSCORE_FILE):
                return 0

            with open(HIGHSCORE_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, dict):
                return 0

            return max(0, int(data.get("highscore", 0)))

        except (
            OSError,
            ValueError,
            TypeError,
            AttributeError,
            OverflowError,
            json.JSONDecodeError
        ):
            return 0

    def save_highscore(self):
        data = {
            "highscore": self.best_score
        }

        temp_file = HIGHSCORE_FILE + ".tmp"

        try:
            with open(temp_file, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

            os.replace(temp_file, HIGHSCORE_FILE)

        except OSError as error:
            print(f"Error while saving highscore: {error}")

            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except OSError:
                pass

    def reset(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.spawn_timer = PIPE_INTERVAL

    def start_game(self):
        self.reset()
        self.state = GameState.PLAYING
        self.bird.flap()

    def end_game(self):
        if self.state != GameState.PLAYING:
            return

        if self.score > self.best_score:
            self.best_score = self.score
            self.save_highscore()

        self.state = GameState.GAME_OVER
        self.restart_timer = RESTART_DELAY

        self.sounds.play(self.sounds.hit)

    def spawn_pipe(self):
        self.pipes.append(PipePair(WIDTH + 40))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_SPACE:

                    if self.state == GameState.START:
                        self.start_game()

                    elif self.state == GameState.PLAYING:
                        self.bird.flap()
                        self.sounds.play(self.sounds.flap)

                    elif (
                        self.state == GameState.GAME_OVER
                        and self.restart_timer <= 0
                    ):
                        self.start_game()

    def update(self, dt):
        if self.state == GameState.GAME_OVER:
            self.restart_timer = max(
                0, self.restart_timer - dt
            )
            return

        if self.state != GameState.PLAYING:
            return

        self.bird.update(dt)

        self.spawn_timer += dt * 1000

        if self.spawn_timer >= PIPE_INTERVAL:
            self.spawn_timer = 0
            self.spawn_pipe()

        for pipe in self.pipes:
            pipe.update(dt)

            if not pipe.passed and pipe.x + PIPE_WIDTH < self.bird.x:
                pipe.passed = True
                self.score += 1
                self.sounds.play(self.sounds.score)

        self.pipes = [
            pipe for pipe in self.pipes
            if not pipe.off_screen
        ]

        self.check_collisions()

    def check_collisions(self):
        bird_rect = self.bird.rect

        if (
            bird_rect.top <= 0
            or bird_rect.bottom >= HEIGHT - GROUND_HEIGHT
        ):
            self.end_game()
            return

        if any(pipe.collides_with(bird_rect) for pipe in self.pipes):
            self.end_game()

    def draw_background(self):
        self.screen.fill(SKY)

        for x in range(0, WIDTH, 95):
            pygame.draw.circle(
                self.screen, (135, 210, 245),
                (x + 35, 90), 24
            )

            pygame.draw.circle(
                self.screen, (135, 210, 245),
                (x + 65, 88), 18
            )

        ground_y = HEIGHT - GROUND_HEIGHT

        pygame.draw.rect(
            self.screen, GROUND_TOP,
            (0, ground_y, WIDTH, 14)
        )

        pygame.draw.rect(
            self.screen, GROUND,
            (0, ground_y + 14, WIDTH, GROUND_HEIGHT - 14)
        )

    def draw_text_center(self, text, font, y, color=WHITE):
        rendered = font.render(text, True, color)
        rect = rendered.get_rect(center=(WIDTH // 2, y))
        self.screen.blit(rendered, rect)

    def draw_text_right(self, text, font, y, color=WHITE):
        rendered = font.render(text, True, color)
        rect = rendered.get_rect(topright=(WIDTH - 15, y))
        self.screen.blit(rendered, rect)

    def draw_score(self):
        score = self.font_big.render(
            str(self.score), True, WHITE
        )

        shadow = self.font_big.render(
            str(self.score), True, BLACK
        )

        rect = score.get_rect(center=(WIDTH // 2, 58))

        self.screen.blit(shadow, rect.move(3, 3))
        self.screen.blit(score, rect)

    def draw_start_screen(self):
        self.draw_text_center(
            "Flappy Bird!", self.font_big, 180
        )

        self.draw_text_center(
            "Space = start / jump", self.font_mid, 260
        )

        self.draw_text_right(
            "(Made by David_Lachtan)", self.font_small, 215
        )

        self.draw_text_center(
            "ESC = exit", self.font_small, 330
        )

    def draw_game_over_screen(self):
        overlay = pygame.Surface(
            (WIDTH, HEIGHT), pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 95))
        self.screen.blit(overlay, (0, 0))

        self.draw_text_center(
            "Game Over!", self.font_big, 190
        )

        self.draw_text_center(
            f"Score: {self.score}", self.font_mid, 260
        )

        self.draw_text_center(
            f"High Score: {self.best_score}",
            self.font_mid, 305
        )

        if self.restart_timer <= 0:
            self.draw_text_center(
                "Space = Restart",
                self.font_small, 365
            )

        self.draw_text_center(
            "ESC = exit", self.font_small, 405
        )

    def draw(self):
        self.draw_background()

        for pipe in self.pipes:
            pipe.draw(self.screen)

        self.bird.draw(self.screen)

        if self.state == GameState.START:
            self.draw_start_screen()

        elif self.state == GameState.PLAYING:
            self.draw_score()

        elif self.state == GameState.GAME_OVER:
            self.draw_score()
            self.draw_game_over_screen()

        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 800

            self.handle_events()
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    Game().run()
