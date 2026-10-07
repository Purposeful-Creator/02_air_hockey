"""
GameEngine: owns the puck, both paddles, and the computer AI, and runs
one frame's worth of game logic.

Starter version: the puck bounces around and paddles can hit it, but
there is no scoring, no match timer, and the reset that happens after
a goal is incomplete. That's what Tasks 2-4 fix/add.
"""

import random

from game.puck import Puck
from game.paddle import Paddle
from game.ai import ComputerAI
from game.collisions import handle_paddle_collision
from game.renderer import WIDTH, HEIGHT, MARGIN, GOAL_TOP, GOAL_BOTTOM
from game.scoring import Score


PLAYER_SPEED = 6
PUCK_RADIUS = 12
PADDLE_RADIUS = 28
INITIAL_PUCK_SPEED = 4.5
import time
MATCH_SECONDS = 30


class GameEngine:
    def __init__(self):
        self.puck = Puck(WIDTH / 2, HEIGHT / 2, PUCK_RADIUS)
        self._launch_puck()

        self.score = Score()
        self.winner = None
        self.start_time = time.monotonic()
        self.time_left = MATCH_SECONDS
        self.winner = None

        self.player = Paddle(
            x=WIDTH * 0.15, y=HEIGHT / 2, radius=PADDLE_RADIUS,
            min_x=MARGIN + PADDLE_RADIUS, max_x=WIDTH / 2 - PADDLE_RADIUS,
            min_y=MARGIN + PADDLE_RADIUS, max_y=HEIGHT - MARGIN - PADDLE_RADIUS,
        )
        self.computer = Paddle(
            x=WIDTH * 0.85, y=HEIGHT / 2, radius=PADDLE_RADIUS,
            min_x=WIDTH / 2 + PADDLE_RADIUS, max_x=WIDTH - MARGIN - PADDLE_RADIUS,
            min_y=MARGIN + PADDLE_RADIUS, max_y=HEIGHT - MARGIN - PADDLE_RADIUS,
        )
        self.ai = ComputerAI()

    def _launch_puck(self, direction=None):
        if direction is None:
            direction = random.choice([-1, 1])
        vy_factor = random.choice([0.3, 0.6, -0.3, -0.6])
        self.puck.vx = INITIAL_PUCK_SPEED * direction
        self.puck.vy = INITIAL_PUCK_SPEED * vy_factor

    def handle_input(self, keys_pressed):
        import pygame
        dx = dy = 0
        if keys_pressed[pygame.K_UP]:
            dy -= PLAYER_SPEED
        if keys_pressed[pygame.K_DOWN]:
            dy += PLAYER_SPEED
        if keys_pressed[pygame.K_LEFT]:
            dx -= PLAYER_SPEED
        if keys_pressed[pygame.K_RIGHT]:
            dx += PLAYER_SPEED
        self.player.move_by(dx, dy)

    def update(self):
        if self.winner:
            return
        self.time_left = max(0, MATCH_SECONDS - (time.monotonic() - self.start_time))
        if self.time_left == 0:
            self.winner = self.score.result()   # "player" / "computer" / "draw"
            return

        self.ai.update(self.computer, self.puck)

        self.puck.move()
        self.puck.bounce_off_walls(HEIGHT, MARGIN)

        handle_paddle_collision(self.puck, self.player)
        handle_paddle_collision(self.puck, self.computer)

        self._handle_goals()

    def _handle_goals(self):
        if self.puck.x - self.puck.radius < MARGIN:
            if GOAL_TOP < self.puck.y < GOAL_BOTTOM:
                self._goal_scored("computer")
            else:
                self.puck.x = MARGIN + self.puck.radius
                self.puck.vx = -self.puck.vx
        elif self.puck.x + self.puck.radius > WIDTH - MARGIN:
            if GOAL_TOP < self.puck.y < GOAL_BOTTOM:
                self._goal_scored("player") 
            else:
                self.puck.x = WIDTH - MARGIN - self.puck.radius
                self.puck.vx = -self.puck.vx

    def _goal_scored(self, scorer):
        self.score.add_point(scorer)
        self._reset_puck()
        self._reset_paddles()
        self.ai = ComputerAI()
        self._launch_puck(direction=1 if scorer == "player" else -1)

    def _reset_puck(self):
        self.puck.x, self.puck.y = WIDTH / 2, HEIGHT / 2
        self.puck.vx = 0
        self.puck.vy = 0

    def _reset_paddles(self):
        self.player.x, self.player.y = WIDTH * 0.15, HEIGHT / 2
        self.computer.x, self.computer.y = WIDTH * 0.85, HEIGHT / 2

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_table(surface)
        renderer.draw_paddle(surface, self.player, renderer.COLOR_PLAYER)
        renderer.draw_paddle(surface, self.computer, renderer.COLOR_COMPUTER)
        renderer.draw_puck(surface, self.puck)

        # scores
        renderer.draw_text(surface, font, str(self.score.player),
                        (WIDTH / 2 - 60, 30), renderer.COLOR_PLAYER)
        renderer.draw_text(surface, font, str(self.score.computer),
                        (WIDTH / 2 + 40, 30), renderer.COLOR_COMPUTER)

        # timer
        shown = int(self.time_left) + 1 if self.time_left else 0
        renderer.draw_text(surface, font, f"Time: {shown}", (WIDTH / 2 - 40, HEIGHT - 55))

        # result banner
        if self.winner:
            msg = {"player": "You win!", "computer": "Computer wins!", "draw": "Draw!"}[self.winner]
            renderer.draw_banner(surface, font, msg)
        
