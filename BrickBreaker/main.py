import pygame
import sys

pygame.init()


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60


# Colors
BLACK = (20, 20, 20)
WHITE = (230, 230, 230)
RED = (255, 80, 80)
BLUE = (80, 150, 255)
GREEN = (80, 255, 80)
YELLOW = (255, 255, 80)
ORANGE = (255, 165, 0)
PURPLE = (160, 32, 240)
BRICK_COLOR =[GREEN, BLUE, YELLOW, ORANGE, PURPLE]

PADDLE_WIDTH = 100
PADDLE_HEIGHT = 20
PADDLE_Y_OFFSET = 40   # Distance from the top of the window
PADDLE_SPEED = 7

# Ball
BALL_RADIUS = 10
BALL_SPEED_X = 4
BALL_SPEED_Y = -4 # Starts moving upwards
trail_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
ball_trail = []
TRAIL_LENGTH = 10  # Length of the ball trail

# Bricks
BRICK_ROWS = 5
BRICK_COLS = 10
BRICK_WIDTH = 60
BRICK_HEIGHT = 20
BRICK_PADDING = 15
BRICK_OFFSET_TOP = 60
BRICK_OFFSET_LEFT = 35

# Set up window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("BrickBreaker")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)

# Game state
game_state = 'menu'
score = 0
start_time = 0

def reset_game():
    global paddle_x, paddle_y, ball_x, ball_y, ball_dx, ball_dy, score, start_time, ball_trail, bricks, game_state
    paddle_x = (WINDOW_WIDTH - PADDLE_WIDTH) // 2  # Initial paddle position
    paddle_y = WINDOW_HEIGHT - PADDLE_Y_OFFSET - PADDLE_HEIGHT
    # Ball initial position
    ball_x = paddle_x + PADDLE_WIDTH // 2
    ball_y = paddle_y - BALL_RADIUS
    ball_dx = BALL_SPEED_X
    ball_dy = BALL_SPEED_Y
    ball_trail = []  # Reset ball trail
    score = 0
    start_time = pygame.time.get_ticks()
    create_bricks()  # Initialize bricks

def create_bricks():
    global bricks
    bricks = []
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            x = BRICK_OFFSET_LEFT + col * (BRICK_WIDTH + BRICK_PADDING)
            y = BRICK_OFFSET_TOP + row * (BRICK_HEIGHT + BRICK_PADDING)
            health = BRICK_ROWS - row  # Top row = 5, bottom row = 1
            brick = {
                'rect': pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT),
                'health': health,
                'color': BRICK_COLOR[health - 1]  # Use color based on health
            }
            bricks.append(brick)

reset_game()  # Initialize game state

# Main loop
running = True
while running:
    screen.fill(BLACK)  # Clear the screen with black

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Paddle movement
    keys = pygame.key.get_pressed()

    # MENU STATE
    if game_state == 'menu':
        title = font.render("BrickBreaker", True, WHITE)
        prompt = font.render("Press SPACE to Start", True, WHITE)
        screen.blit(title, ((WINDOW_WIDTH - title.get_width()) // 2, 200))
        screen.blit(prompt, ((WINDOW_WIDTH - prompt.get_width()) // 2, 300))

        if keys[pygame.K_SPACE]:
            reset_game()
            game_state = 'playing'  # Change to playing state

    # PLAYING STATE
    elif game_state == 'playing':
        if keys[pygame.K_LEFT]:
            paddle_x -= PADDLE_SPEED
        if keys[pygame.K_RIGHT]:
            paddle_x += PADDLE_SPEED
        # Clamp paddle
        paddle_x = max(0, min(WINDOW_WIDTH - PADDLE_WIDTH, paddle_x))
            

        # Ball movement
        ball_x += ball_dx
        ball_y += ball_dy

        # Bounce the ball off the left and right walls
        if ball_x - BALL_RADIUS <= 0 or ball_x + BALL_RADIUS >= WINDOW_WIDTH:
            ball_dx *= -1  # Reverse the horizontal direction
        # Bounce the ball off the top
        if ball_y - BALL_RADIUS <= 0:
            ball_dy *= -1

        # Paddle collision
        paddle_rect = pygame.Rect(paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT)
        ball_rect = pygame.Rect(ball_x - BALL_RADIUS, ball_y - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
        if ball_rect.colliderect(paddle_rect) and ball_dy > 0:
            paddle_center = paddle_x + PADDLE_WIDTH / 2
            hit_pos = (ball_x - paddle_center) / (PADDLE_WIDTH / 2)  # Normalized hit position
            ball_dx = hit_pos * 5  # Adjust ball speed based on where it hits the paddle
            ball_dy *= -1
        
        # Brick collision
        for i, brick in enumerate(bricks):
            if ball_rect.colliderect(brick['rect']):
                brick['health'] -= 1
                ball_dy *= -1  # Bounce back
                
                # Remove brick if health reaches 0
                if brick['health'] <= 0:
                    bricks.pop(i)
                    score += 100
                else:
                    # Update color based on remaining health
                    brick['color'] = BRICK_COLOR[brick['health'] - 1]
                break

        # Check if the ball falls below off bottom of the screen
        if ball_y - BALL_RADIUS > WINDOW_HEIGHT:
            game_state = 'game_over'  # Change to game over state

       
        ball_trail.append((int(ball_x), int(ball_y)))
        if len(ball_trail) > TRAIL_LENGTH:
            ball_trail.pop(0)  # Keep the trail length fixed
        
        trail_surface.fill((0, 0, 0, 0))  # Clear the trail surface

        for i in range(len(ball_trail) - 1, -1, -1):  # Draw trail in reverse order for fading effect
            pos = ball_trail[i]
            age = len(ball_trail) - 1 - i # Trail age

            radius = int(BALL_RADIUS * (1 - age / TRAIL_LENGTH))  # Decrease radius for fading effect
            radius = max(1, radius)  # Ensure radius is at least 1

            alpha = int(255 * (1 - age / TRAIL_LENGTH))  # Fade effect
            trail_color = (*RED[:3], alpha)
            pygame.draw.circle(trail_surface, trail_color, pos, radius)
        screen.blit(trail_surface, (0, 0))  # Draw the trail surface
         # drawing
        pygame.draw.rect(screen, WHITE, paddle_rect, border_radius=5)  # Draw the paddle
        pygame.draw.circle(screen, RED, (int(ball_x), int(ball_y)), BALL_RADIUS)  # Draw the ball

        for brick in bricks:
            pygame.draw.rect(screen, brick['color'], brick['rect'])  # Draw each brick with its color
        if not bricks:
            elapsed_time = (pygame.time.get_ticks() - start_time) / 1000  # Convert to seconds
            bonus = max(0, 1000 - elapsed_time * 10)  # Bonus for time taken
            score += bonus
            game_state = 'game_over'

    # GAME OVER STATE
    elif game_state == 'game_over':
        if bricks:
            end_text = font.render("Game Over", True, RED)
        else:
            end_text = font.render("You Win!", True, GREEN)

        restart_text = font.render("Press R to Restart", True, WHITE)
        final_score_text = font.render(f"Final Score: {score}", True, WHITE)

        screen.blit(end_text, ((WINDOW_WIDTH - end_text.get_width()) // 2, 200))
        screen.blit(final_score_text, ((WINDOW_WIDTH - final_score_text.get_width()) // 2, 260))
        screen.blit(restart_text, ((WINDOW_WIDTH - restart_text.get_width()) // 2, 320))

        if keys[pygame.K_r]:
            reset_game()
            game_state = 'playing'  # Restart the game

    # Refresh the display
    if game_state == 'playing':
        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000  # Convert to seconds
        small_font = pygame.font.SysFont(None, 28)

        score_text = small_font.render(f"Score: {score}", True, WHITE)
        time_text = small_font.render(f"Time: {elapsed_time:.1f}s", True, WHITE)
        bricks_text = small_font.render(f"Bricks: {len(bricks)}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(time_text, (10, 40))
        screen.blit(bricks_text, (10, 70))

    pygame.display.flip()
    clock.tick(FPS)  # Maintain the frame rate

# Clean up
pygame.quit()
sys.exit()