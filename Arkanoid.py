#Игра сгенерирована при помощи DeepSeek

import pygame
import sys
import random

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Арканоид")

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255),
    (255, 255, 0), (255, 0, 255), (0, 255, 255)
]

# Параметры платформы
paddle_width = 100
paddle_height = 15
paddle_x = (WIDTH - paddle_width) // 2
paddle_y = HEIGHT - 40
paddle_speed = 8

# Параметры мяча
ball_radius = 10
ball_x = WIDTH // 2
ball_y = HEIGHT // 2
ball_dx = 4 * random.choice([-1, 1])
ball_dy = -4

# Параметры кирпичей
brick_width = 75
brick_height = 30
brick_rows = 5
brick_cols = 10
bricks = []

# Создание кирпичей
for row in range(brick_rows):
    for col in range(brick_cols):
        brick_x = col * (brick_width + 5) + 15
        brick_y = row * (brick_height + 5) + 50
        brick_color = random.choice(COLORS)
        bricks.append(pygame.Rect(brick_x, brick_y, brick_width, brick_height))

# Игровые переменные
score = 0
lives = 3
game_over = False
win = False

# Шрифт
font = pygame.font.Font(None, 36)

# Основной игровой цикл
clock = pygame.time.Clock()
while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    if not win and lives > 0:
        # Управление платформой
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle_x > 0:
            paddle_x -= paddle_speed
        if keys[pygame.K_RIGHT] and paddle_x < WIDTH - paddle_width:
            paddle_x += paddle_speed
        
        # Движение мяча
        ball_x += ball_dx
        ball_y += ball_dy
        
        # Отскок от стен
        if ball_x <= ball_radius or ball_x >= WIDTH - ball_radius:
            ball_dx = -ball_dx
        if ball_y <= ball_radius:
            ball_dy = -ball_dy
        
        # Проверка столкновения с платформой
        paddle_rect = pygame.Rect(paddle_x, paddle_y, paddle_width, paddle_height)
        if (ball_y + ball_radius >= paddle_y and 
            ball_x >= paddle_x and 
            ball_x <= paddle_x + paddle_width):
            ball_dy = -ball_dy
            # Изменение направления в зависимости от места удара
            ball_dx = (ball_x - (paddle_x + paddle_width // 2)) / 10
        
        # Проверка выхода за нижнюю границу
        if ball_y >= HEIGHT:
            lives -= 1
            if lives > 0:
                # Перезапуск мяча
                ball_x = WIDTH // 2
                ball_y = HEIGHT // 2
                ball_dx = 4 * random.choice([-1, 1])
                ball_dy = -4
                paddle_x = (WIDTH - paddle_width) // 2
        
        # Проверка столкновения с кирпичами
        ball_rect = pygame.Rect(ball_x - ball_radius, ball_y - ball_radius, 
                               ball_radius * 2, ball_radius * 2)
        for brick in bricks[:]:
            if ball_rect.colliderect(brick):
                bricks.remove(brick)
                ball_dy = -ball_dy
                score += 10
                break
        
        # Проверка победы
        if len(bricks) == 0:
            win = True
    
    # Отрисовка
    screen.fill(BLACK)
    
    # Отрисовка кирпичей
    for brick in bricks:
        pygame.draw.rect(screen, random.choice(COLORS), brick)
    
    # Отрисовка платформы
    pygame.draw.rect(screen, WHITE, (paddle_x, paddle_y, paddle_width, paddle_height))
    
    # Отрисовка мяча
    pygame.draw.circle(screen, WHITE, (int(ball_x), int(ball_y)), ball_radius)
    
    # Отрисовка счета и жизней
    score_text = font.render(f"Счет: {score}", True, WHITE)
    lives_text = font.render(f"Жизни: {lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (WIDTH - 150, 10))
    
    # Сообщения о победе или проигрыше
    if win:
        win_text = font.render("ПОБЕДА! Нажмите ESC для выхода", True, WHITE)
        screen.blit(win_text, (WIDTH // 2 - 200, HEIGHT // 2))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            game_over = True
    
    if lives <= 0:
        lose_text = font.render("ИГРА ОКОНЧЕНА! Нажмите ESC для выхода", True, WHITE)
        screen.blit(lose_text, (WIDTH // 2 - 200, HEIGHT // 2))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            game_over = True
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()