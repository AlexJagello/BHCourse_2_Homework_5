import pygame
import sys
import random
import numpy as np

class ArkanoidEnv:
    def __init__(self):
        # Инициализация Pygame
        pygame.init()
        
        # Настройки экрана
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Арканоид")
        
        # Цвета
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.COLORS = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255),
            (255, 255, 0), (255, 0, 255), (0, 255, 255)
        ]
        
        # Параметры платформы
        self.paddle_width = 150
        self.paddle_height = 15
        self.paddle_x = (self.WIDTH - self.paddle_width) // 2
        self.paddle_y = self.HEIGHT - 40
        self.paddle_speed = 15
        
        # Параметры мяча
        self.ball_radius = 20
        self.ball_x = self.WIDTH // 2
        self.ball_y = self.HEIGHT // 2
        self.ball_dx = 4 * random.choice([-1, 1])
        self.ball_dy = -4
        
        # Параметры кирпичей
        self.brick_width = 75
        self.brick_height = 30
        self.brick_rows = 1
        self.brick_cols = 10
        self.bricks = []
        self._init_bricks()
        
        # Игровые переменные
        self.score = 0

        self.game_over = False
        self.win = False
        self.clock = pygame.time.Clock()
        
        # Шрифт
        self.font = pygame.font.Font(None, 36)

        self.prev_action = 0
        
        self.steps = 0
        self.min_steps = 12000

        self.action_space = 3  # 0 влево, 1 стоять, 2 вправо
        self.observation_space = (8,) 
    
    # Инициализатор кирпичей
    def _init_bricks(self):
        self.bricks = []
        for row in range(self.brick_rows):
            for col in range(self.brick_cols):
                brick_x = col * (self.brick_width + 5) + 15
                brick_y = row * (self.brick_height + 5) + 50
                brick_color = random.choice(self.COLORS)
                self.bricks.append(pygame.Rect(brick_x, brick_y, self.brick_width, self.brick_height))
    
    # Возврат к изначальному состоянию
    def reset(self):
        self.paddle_x = (self.WIDTH - self.paddle_width) // 2
        self.ball_x = self.WIDTH // 2
        self.ball_y = self.HEIGHT // 2
        self.ball_dx = 4 * random.choice([-1, 1])
        self.ball_dy = -4
        self.score = 0
        self.steps = 0
        self.min_steps = 12000
        self.game_over = False
        self.win = False
        self._init_bricks()
        
        return self._get_state()
    
    def _get_state(self):
        # состояние: позиция мяча, направление, позиция платформы
      return np.array([
            self.ball_x / self.WIDTH,  # позиция мяча по X
            self.ball_y / self.HEIGHT,  # позиция мяча по Y
            self.ball_dx / 4,           # скорость по X
            self.ball_dy / 4,           # скорость по Y
            self.paddle_x / self.WIDTH, # позиция платформы
            len(self.bricks) / (self.brick_rows * self.brick_cols),  # оставшиеся кирпичи
            self.score / (self.brick_rows * self.brick_cols * 10)  # счет
        ])
    
    def step(self, action):
        reward = 0
        self.steps += 1

        if action == 0 and self.paddle_x > 0:
            self.paddle_x -= self.paddle_speed
        elif action == 2 and self.paddle_x < self.WIDTH - self.paddle_width:
            self.paddle_x += self.paddle_speed
        
        # Движение мяча
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        # Отскок от стен
        if self.ball_x + 2 <= self.ball_radius or self.ball_x +2 >= self.WIDTH - self.ball_radius:
            self.ball_dx = -self.ball_dx
        if self.ball_y <= self.ball_radius:
            self.ball_dy = -self.ball_dy
        
        # Проверка столкновения с платформой
        paddle_rect = pygame.Rect(self.paddle_x, self.paddle_y, self.paddle_width, self.paddle_height)
        if (self.ball_y + self.ball_radius >= self.paddle_y and 
            self.ball_x >= self.paddle_x and 
            self.ball_x <= self.paddle_x + self.paddle_width):
            self.ball_dy = -self.ball_dy
            # Изменение направления в зависимости от места удара
            self.ball_dx = (self.ball_x - (self.paddle_x + self.paddle_width // 2)) / 10
        

        
        # Проверка столкновения с кирпичами
        ball_rect = pygame.Rect(self.ball_x - self.ball_radius, self.ball_y - self.ball_radius, 
                               self.ball_radius * 2, self.ball_radius * 2)
        for brick in self.bricks[:]:
            if ball_rect.colliderect(brick):
                self.bricks.remove(brick)
                self.ball_dy = -self.ball_dy
                self.score += 10
                reward += 10
                 # Награда за разрушение кирпича
                break
        
        # Проверка победы
        done = False
        if len(self.bricks) == 0:
            self.win = True
            done = True
            reward += 100  # Награда за победу
            if self.min_steps > self.steps:
                reward += 100 # Награда если количество шагов меньше, чем полученное ранее
                self.min_steps = self.steps

        # Если шагов больше 12000, игру считаю проигранной
        if self.steps > 12000:
            self.game_over = True
            done = True
            reward += -30 #Штраф если шагов больше 12000

         # Проверка выхода за нижнюю границу
        if self.ball_y >= self.HEIGHT:
            self.game_over = True
            done = True
            reward += -50  # Штраф за поражение
        
        self.prev_action = action
        return self._get_state(), reward, done, {'score': self.score}
    
    def render(self):
        self.screen.fill(self.BLACK)
        
        # Отрисовка кирпичей
        for brick in self.bricks:
            pygame.draw.rect(self.screen, random.choice(self.COLORS), brick)
        
        # Отрисовка платформы
        pygame.draw.rect(self.screen, self.WHITE, 
                         (self.paddle_x, self.paddle_y, self.paddle_width, self.paddle_height))
        
        # Отрисовка мяча
        pygame.draw.circle(self.screen, self.WHITE, 
                           (int(self.ball_x), int(self.ball_y)), self.ball_radius)
        
        # Отрисовка счета и жизней
        score_text = self.font.render(f"Счет: {self.score}", True, self.WHITE)
        lives_text = self.font.render(f"Шаги: {self.steps}", True, self.WHITE)
        self.screen.blit(lives_text, (self.WIDTH - 150, 10))
        self.screen.blit(score_text, (10, 10))
        
        # Сообщения о победе или проигрыше
        if self.win:
            win_text = self.font.render("ПОБЕДА!", True, self.WHITE)
            self.screen.blit(win_text, (self.WIDTH // 2 - 50, self.HEIGHT // 2))
        
        if self.game_over and not self.win:
            lose_text = self.font.render("ИГРА ОКОНЧЕНА", True, self.WHITE)
            self.screen.blit(lose_text, (self.WIDTH // 2 - 100, self.HEIGHT // 2))
        
        pygame.display.flip()
        self.clock.tick(60)
    
    def close(self):
        pygame.quit()
        sys.exit()