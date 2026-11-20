import asyncio
import math
import random
import sys
import json
import os
from enum import Enum

import pygame

WIDTH, HEIGHT = (800, 600)
WIDTH, HEIGHT = 800, 600
FPS = 60

SKY = (105, 190, 235)
@@ -66,6 +66,7 @@ def draw(self, surface):
        pygame.draw.ellipse(bird_surface, BLACK, body_rect, 2)

        wing_offset = math.sin(self.wing_timer) * 7

        wing_points = [
            (28, 31),
            (5, 24 + wing_offset),
@@ -79,13 +80,16 @@ def draw(self, surface):
        pygame.draw.circle(bird_surface, BLACK, (52, 24), 3)

        pygame.draw.polygon(
            bird_surface, ORANGE,
            bird_surface,
            ORANGE,
            [(58, 29), (74, 34), (58, 39)]
        )

        pygame.draw.polygon(
            bird_surface, BLACK,
            [(58, 29), (74, 34), (58, 39)], 2
            bird_surface,
            BLACK,
            [(58, 29), (74, 34), (58, 39)],
            2
        )

        rotated = pygame.transform.rotate(bird_surface, angle)
@@ -128,7 +132,7 @@ def draw(self, surface):
            HEIGHT - GROUND_HEIGHT - bottom_y
        )

        for rect in [top_rect, bottom_rect]:
        for rect in (top_rect, bottom_rect):
            pygame.draw.rect(surface, PIPE_GREEN, rect)
            pygame.draw.rect(surface, PIPE_DARK, rect, 4)

@@ -149,7 +153,7 @@ def draw(self, surface):
            cap_h
        )

        for rect in [top_cap, bottom_cap]:
        for rect in (top_cap, bottom_cap):
            pygame.draw.rect(surface, PIPE_GREEN, rect)
            pygame.draw.rect(surface, PIPE_DARK, rect, 4)

@@ -186,16 +190,11 @@ def __init__(self):

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
        self.font_big = pygame.font.SysFont("arial", 56, bold=True)
        self.font_mid = pygame.font.SysFont("arial", 32, bold=True)
        self.font_small = pygame.font.SysFont("arial", 24)

        self.running = True
        self.best_score = self.load_highscore()
        self.restart_timer = 0

@@ -215,21 +214,11 @@ def load_highscore(self):

            return max(0, int(data.get("highscore", 0)))

        except (
            OSError,
            ValueError,
            TypeError,
            AttributeError,
            OverflowError,
            json.JSONDecodeError
        ):
        except (OSError, ValueError, TypeError, OverflowError):
            return 0

    def save_highscore(self):
        data = {
            "highscore": self.best_score
        }

        data = {"highscore": self.best_score}
        temp_file = HIGHSCORE_FILE + ".tmp"

        try:
@@ -238,9 +227,7 @@ def save_highscore(self):

            os.replace(temp_file, HIGHSCORE_FILE)

        except OSError as error:
            print(f"Error while saving highscore: {error}")

        except OSError:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
@@ -272,37 +259,38 @@ def end_game(self):
    def spawn_pipe(self):
        self.pipes.append(PipePair(WIDTH + 40))

    def flap_or_start(self):
        if self.state == GameState.START:
            self.start_game()

        elif self.state == GameState.PLAYING:
            self.bird.flap()

        elif self.state == GameState.GAME_OVER:
            if self.restart_timer <= 0:
                self.start_game()

    def handle_events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                self.running = False

            if event.type == pygame.KEYDOWN:
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_SPACE:

                    if self.state == GameState.START:
                        self.start_game()
                    self.running = False

                    elif self.state == GameState.PLAYING:
                        self.bird.flap()
                elif event.key in (pygame.K_SPACE, pygame.K_UP):
                    self.flap_or_start()

                    elif (
                        self.state == GameState.GAME_OVER
                        and self.restart_timer <= 0
                    ):
                        self.start_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.flap_or_start()

    def update(self, dt):
        if self.state == GameState.GAME_OVER:
            self.restart_timer = max(
                0, self.restart_timer - dt
            )
            self.restart_timer = max(0, self.restart_timer - dt)
            return

        if self.state != GameState.PLAYING:
@@ -348,24 +336,30 @@ def draw_background(self):

        for x in range(0, WIDTH, 95):
            pygame.draw.circle(
                self.screen, (135, 210, 245),
                (x + 35, 90), 24
                self.screen,
                (135, 210, 245),
                (x + 35, 90),
                24
            )

            pygame.draw.circle(
                self.screen, (135, 210, 245),
                (x + 65, 88), 18
                self.screen,
                (135, 210, 245),
                (x + 65, 88),
                18
            )

        ground_y = HEIGHT - GROUND_HEIGHT

        pygame.draw.rect(
            self.screen, GROUND_TOP,
            self.screen,
            GROUND_TOP,
            (0, ground_y, WIDTH, 14)
        )

        pygame.draw.rect(
            self.screen, GROUND,
            self.screen,
            GROUND,
            (0, ground_y + 14, WIDTH, GROUND_HEIGHT - 14)
        )

@@ -380,66 +374,62 @@ def draw_text_right(self, text, font, y, color=WHITE):
        self.screen.blit(rendered, rect)

    def draw_score(self):
        score = self.font_big.render(
            str(self.score), True, WHITE
        )

        shadow = self.font_big.render(
            str(self.score), True, BLACK
        )
        score = self.font_big.render(str(self.score), True, WHITE)
        shadow = self.font_big.render(str(self.score), True, BLACK)

        rect = score.get_rect(center=(WIDTH // 2, 58))

        self.screen.blit(shadow, rect.move(3, 3))
        self.screen.blit(score, rect)

    def draw_start_screen(self):
        self.draw_text_center(
            "Flappy Bird!", self.font_big, 180
        )
        self.draw_text_center("Flappy Bird!", self.font_big, 180)

        self.draw_text_center(
            "Space = start / jump", self.font_mid, 260
            "Space / Click = Start",
            self.font_mid,
            260
        )

        self.draw_text_right(
            "(Made by David_Lachtan)", self.font_small, 215
            "(Made by David_Lachtan)",
            self.font_small,
            215
        )

        self.draw_text_center(
            "ESC = exit", self.font_small, 330
            "ESC = Exit",
            self.font_small,
            330
        )

    def draw_game_over_screen(self):
        overlay = pygame.Surface(
            (WIDTH, HEIGHT), pygame.SRCALPHA
        )

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 95))
        self.screen.blit(overlay, (0, 0))

        self.draw_text_center(
            "Game Over!", self.font_big, 190
        )
        self.draw_text_center("Game Over!", self.font_big, 190)

        self.draw_text_center(
            f"Score: {self.score}", self.font_mid, 260
            f"Score: {self.score}",
            self.font_mid,
            260
        )

        self.draw_text_center(
            f"High Score: {self.best_score}",
            self.font_mid, 305
            self.font_mid,
            305
        )

        if self.restart_timer <= 0:
            self.draw_text_center(
                "Space = Restart",
                self.font_small, 365
                "Space / Click = Restart",
                self.font_small,
                365
            )

        self.draw_text_center(
            "ESC = exit", self.font_small, 405
        )
        self.draw_text_center("ESC = Exit", self.font_small, 405)

    def draw(self):
        self.draw_background()
@@ -461,14 +451,24 @@ def draw(self):

        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 800
    async def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000, 0.05)

            self.handle_events()
            self.update(dt)
            self.draw()

            # Allows Pygbag / browser to process other tasks.
            await asyncio.sleep(0)

        pygame.quit()


async def main():
    game = Game()
    await game.run()


if __name__ == "__main__":
    Game().run()
    asyncio.run(main())
