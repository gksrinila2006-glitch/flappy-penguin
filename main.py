import pygame
import sys
import random
import json
import os

# ==================== INITIALIZATION ====================
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 223, 0)
RED = (220, 20, 60)
GREEN = (34, 139, 34)
LIGHT_BLUE = (135, 206, 235)

# Physics constants
GRAVITY = 0.1
FLAP_STRENGTH = -4
PIPE_GAP = 160
PIPE_WIDTH = 52
PIPE_VELOCITY_START = -2.5

# Create display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🐧 FLAPPY PENGUIN - MASTER GAME 🐧")
clock = pygame.time.Clock()
font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 32)
font_tiny = pygame.font.Font(None, 24)

# Scores file
SCORES_FILE = "highscores.json"


# ==================== SCORE MANAGEMENT ====================
class ScoreManager:
    """Manages high scores storage and retrieval"""
    
    def __init__(self, filename):
        self.filename = filename
        self.scores = self.load_scores()
    
    def load_scores(self):
        """Load scores from file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_scores(self):
        """Save scores to file"""
        with open(self.filename, 'w') as f:
            json.dump(self.scores, f, indent=2)
    
    def add_score(self, name, score):
        """Add or update a player's score"""
        if name not in self.scores or score > self.scores[name]:
            self.scores[name] = score
            self.save_scores()
            return True
        return False
    
    def get_top_scores(self, limit=5):
        """Get top scores sorted"""
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores[:limit]


score_manager = ScoreManager(SCORES_FILE)


# ==================== BIRD CLASS ====================
class Bird:
    """Handles bird object with gravity and flapping mechanics"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.width = 24
        self.height = 20
        self.alive = True
    
    def flap(self):
        """Make the bird jump upward"""
        self.velocity = FLAP_STRENGTH
    
    def update(self):
        """Update bird position with gravity"""
        self.velocity += GRAVITY
        self.y += self.velocity
        
        # Check if bird hits ground or ceiling
        if self.y + self.height >= SCREEN_HEIGHT - 50 or self.y <= 0:
            self.alive = False
    
    def draw(self, surface):
        """Draw the penguin"""
        # Penguin body (black)
        pygame.draw.ellipse(surface, BLACK, (self.x + 5, self.y + 3, 24, 18))
        
        # Penguin belly (white)
        pygame.draw.ellipse(surface, WHITE, (self.x + 8, self.y + 6, 18, 12))
        
        # Penguin head (black)
        pygame.draw.circle(surface, BLACK, (self.x + 17, self.y + 2), 7)
        
        # Penguin eyes (white circles)
        pygame.draw.circle(surface, WHITE, (self.x + 13, self.y), 3)
        pygame.draw.circle(surface, WHITE, (self.x + 21, self.y), 3)
        
        # Penguin pupils (black)
        pygame.draw.circle(surface, BLACK, (self.x + 13, self.y), 1)
        pygame.draw.circle(surface, BLACK, (self.x + 21, self.y), 1)
        
        # Penguin beak (orange)
        pygame.draw.polygon(surface, (255, 140, 0), [(self.x + 17, self.y + 4), (self.x + 20, self.y + 6), (self.x + 17, self.y + 8)])
        
        # Penguin feet (orange)
        pygame.draw.line(surface, (255, 140, 0), (self.x + 12, self.y + 21), (self.x + 12, self.y + 24), 2)
        pygame.draw.line(surface, (255, 140, 0), (self.x + 22, self.y + 21), (self.x + 22, self.y + 24), 2)


# ==================== PIPE CLASS ====================
class Pipe:
    """Handles pipe objects that the bird must avoid"""
    
    def __init__(self, x, pipe_velocity, reversed_gap=False):
        self.x = x
        self.width = PIPE_WIDTH
        self.gap = PIPE_GAP
        self.pipe_velocity = pipe_velocity
        self.reversed_gap = reversed_gap
        
        # Generate random gap position with guaranteed passable space
        # The gap is always PIPE_GAP pixels tall
        # Calculate valid range for gap start position
        min_gap_pos = 50
        max_gap_pos = SCREEN_HEIGHT - 50 - self.gap - 50
        gap_position = random.randint(min_gap_pos, max_gap_pos)
        
        if reversed_gap:
            # Reversed: larger portion on top, smaller on bottom (inverted pattern)
            # Create gap from bottom up
            self.bottom_pipe_height = gap_position
            self.gap_start = gap_position
            self.gap_end = gap_position + self.gap
            self.top_pipe_height = SCREEN_HEIGHT - 50 - self.gap_end
        else:
            # Normal: smaller portion on top, larger on bottom
            # Create gap in the middle
            self.top_pipe_height = gap_position
            self.gap_start = gap_position
            self.gap_end = gap_position + self.gap
            self.bottom_pipe_height = SCREEN_HEIGHT - 50 - self.gap_end
        
        self.scored = False  # Track if player has passed this pipe
    
    def update(self):
        """Move pipe to the left"""
        self.x += self.pipe_velocity
    
    def draw(self, surface):
        """Draw top and bottom pipes with guaranteed gap"""
        if self.reversed_gap:
            # Reversed: bottom pipe, gap, top pipe
            # Draw bottom pipe
            pygame.draw.rect(surface, GREEN, (self.x, SCREEN_HEIGHT - 50 - self.bottom_pipe_height, self.width, self.bottom_pipe_height))
            pygame.draw.rect(surface, (0, 100, 0), (self.x, SCREEN_HEIGHT - 50 - self.bottom_pipe_height, self.width, self.bottom_pipe_height), 3)
            
            # Draw top pipe
            pygame.draw.rect(surface, GREEN, (self.x, 0, self.width, self.top_pipe_height))
            pygame.draw.rect(surface, (0, 100, 0), (self.x, 0, self.width, self.top_pipe_height), 3)
        else:
            # Normal: top pipe, gap, bottom pipe
            # Draw top pipe
            pygame.draw.rect(surface, GREEN, (self.x, 0, self.width, self.top_pipe_height))
            pygame.draw.rect(surface, (0, 100, 0), (self.x, 0, self.width, self.top_pipe_height), 3)
            
            # Draw bottom pipe
            pygame.draw.rect(surface, GREEN, (self.x, self.gap_end, self.width, self.bottom_pipe_height))
            pygame.draw.rect(surface, (0, 100, 0), (self.x, self.gap_end, self.width, self.bottom_pipe_height), 3)
    
    def off_screen(self):
        """Check if pipe is off the left side of screen"""
        return self.x + self.width < 0
    
    def check_collision(self, bird):
        """Check if bird collides with pipe - improved accuracy"""
        # Make collision box tighter around the actual penguin sprite
        bird_rect = pygame.Rect(bird.x + 5, bird.y + 2, 20, 20)
        
        # Create pipe collision rectangles
        if self.reversed_gap:
            # Reversed: top and bottom portions
            top_pipe_rect = pygame.Rect(self.x, 0, self.width, self.top_pipe_height)
            bottom_pipe_rect = pygame.Rect(self.x, SCREEN_HEIGHT - 50 - self.bottom_pipe_height, self.width, self.bottom_pipe_height)
        else:
            # Normal: top and bottom portions
            top_pipe_rect = pygame.Rect(self.x, 0, self.width, self.top_pipe_height)
            bottom_pipe_rect = pygame.Rect(self.x, self.gap_end, self.width, self.bottom_pipe_height)
        
        # Check collision
        if bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect):
            return True
        return False


# ==================== GAME CLASS ====================
class Game:
    """Main game class to manage game state"""
    
    def __init__(self):
        self.player_name = ""
        self.lives = 3
        self.total_lives = 3
        self.game_ended = False
        self.heart_break_animation = False
        self.heart_break_timer = 0
        self.reset()
    
    def reset(self):
        """Reset game to initial state"""
        self.bird = Bird(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.game_started = False
        self.pipe_velocity = PIPE_VELOCITY_START
        self.pipe_spawn_timer = 0
        self.pipe_spawn_interval = 100  # Frames between pipe spawns
    
    def spawn_pipe(self):
        """Create a new pipe"""
        # Use reversed gap (more challenging) after 15 points
        reversed_gap = self.score >= 15 and random.random() < 0.6  # 60% chance of reversed pipes after 15
        pipe = Pipe(SCREEN_WIDTH, self.pipe_velocity, reversed_gap=reversed_gap)
        self.pipes.append(pipe)
    
    def live_lost(self):
        """Handle when a live is lost - with heart break animation"""
        self.lives -= 1
        self.heart_break_animation = True
        self.heart_break_timer = 30  # Animation frames
        if self.lives <= 0:
            self.game_ended = True
    
    def update(self):
        """Update game state"""
        if not self.game_started or self.game_over:
            return
        
        # Update bird
        self.bird.update()
        
        # Check if bird is alive
        if not self.bird.alive:
            self.game_over = True
            self.live_lost()
        
        # Spawn pipes
        self.pipe_spawn_timer += 1
        if self.pipe_spawn_timer >= self.pipe_spawn_interval:
            self.spawn_pipe()
            self.pipe_spawn_timer = 0
        
        # Update pipes
        for pipe in self.pipes:
            pipe.update()
            
            # Check collision
            if pipe.check_collision(self.bird):
                self.game_over = True
                self.live_lost()
            
            # Check if bird passed pipe
            if not pipe.scored and pipe.x + pipe.width < self.bird.x:
                pipe.scored = True
                self.score += 1
                
                # Increase difficulty
                if self.score < 15:
                    # Normal difficulty before 15 points
                    self.pipe_velocity -= 0.08
                else:
                    # MUCH TOUGHER difficulty after 15 points
                    # Significantly increase speed
                    self.pipe_velocity -= 0.25
                    
                    # Aggressively increase spawn rate for extra challenge
                    if self.pipe_spawn_interval > 60:
                        self.pipe_spawn_interval -= 2
        
        # Remove off-screen pipes
        self.pipes = [p for p in self.pipes if not p.off_screen()]
    
    def draw_heart(self, surface, x, y, size=30, is_broken=False):
        """Draw a pixel art heart shape like retro games"""
        # Pixel size for the heart
        pix = size // 8
        
        # Heart shape coordinates (8x8 pixel grid relative to x, y)
        # Black outline/shadow
        heart_pixels_black = [
            # Top
            (0, 1), (1, 0), (2, 0),
            (5, 0), (6, 0), (7, 1),
            # Upper middle
            (0, 2), (7, 2),
            # Middle
            (0, 3), (7, 3),
            # Lower middle
            (0, 4), (1, 4), (6, 4), (7, 4),
            # Bottom
            (1, 5), (2, 5), (5, 5), (6, 5),
            (2, 6), (3, 6), (4, 6), (5, 6),
            (3, 7), (4, 7),
        ]
        
        # Red fill
        heart_pixels_red = [
            # Top
            (1, 1), (2, 1), (3, 1),
            (4, 1), (5, 1), (6, 1),
            # Upper middle
            (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2),
            # Middle
            (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3),
            # Lower middle
            (2, 4), (3, 4), (4, 4), (5, 4),
            # Bottom
            (3, 5), (4, 5),
        ]
        
        # White center cross
        heart_pixels_white = [
            # Vertical line
            (3, 2), (4, 2),
            (3, 3), (4, 3),
            (3, 4), (4, 4),
        ]
        
        if is_broken:
            # Draw broken heart (X pattern)
            # Draw black outline
            for px, py in heart_pixels_black:
                pygame.draw.rect(surface, (100, 100, 100), (x + px * pix, y + py * pix, pix, pix))
            
            # Draw gray fill for broken look
            for px, py in heart_pixels_red:
                pygame.draw.rect(surface, (128, 128, 128), (x + px * pix, y + py * pix, pix, pix))
            
            # Draw X pattern
            line_width = 3
            heart_center_x = x + size // 2
            heart_center_y = y + size // 2
            pygame.draw.line(surface, RED, (x, y), (x + size, y + size), line_width)
            pygame.draw.line(surface, RED, (x + size, y), (x, y + size), line_width)
        else:
            # Draw normal heart
            # Draw black outline
            for px, py in heart_pixels_black:
                pygame.draw.rect(surface, (0, 0, 0), (x + px * pix, y + py * pix, pix, pix))
            
            # Draw red fill
            for px, py in heart_pixels_red:
                pygame.draw.rect(surface, RED, (x + px * pix, y + py * pix, pix, pix))
            
            # Draw white cross
            for px, py in heart_pixels_white:
                pygame.draw.rect(surface, WHITE, (x + px * pix, y + py * pix, pix, pix))
    
    def draw(self, surface):
        """Draw all game elements"""
        # Background
        surface.fill(LIGHT_BLUE)
        
        # Ground
        pygame.draw.rect(surface, (139, 69, 19), (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
        pygame.draw.line(surface, BLACK, (0, SCREEN_HEIGHT - 50), (SCREEN_WIDTH, SCREEN_HEIGHT - 50), 2)
        
        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(surface)
        
        # Draw bird
        self.bird.draw(surface)
        
        # Draw score
        score_text = font_medium.render(str(self.score), True, BLACK)
        surface.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 20))
        
        # Draw player name
        name_text = font_small.render(f"Player: {self.player_name}", True, BLACK)
        surface.blit(name_text, (10, 20))
        
        # Draw lives as hearts
        for i in range(self.total_lives):
            is_broken = i >= self.lives
            self.draw_heart(surface, SCREEN_WIDTH - 50 - (i * 40), 40, 30, is_broken=is_broken)
    
    def draw_name_input_screen(self, surface, input_text, cursor_visible):
        """Draw name input screen"""
        surface.fill(LIGHT_BLUE)
        
        # Title
        title = font_large.render("FLAPPY PENGUIN", True, RED)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        # Instructions
        instructions = font_medium.render("Enter Your Name:", True, BLACK)
        surface.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 150))
        
        # Input box
        input_box = pygame.Rect(SCREEN_WIDTH // 2 - 150, 250, 300, 50)
        pygame.draw.rect(surface, WHITE, input_box)
        pygame.draw.rect(surface, BLACK, input_box, 3)
        
        # Input text
        text_surf = font_medium.render(input_text, True, BLACK)
        surface.blit(text_surf, (input_box.x + 10, input_box.y + 10))
        
        # Cursor
        if cursor_visible:
            cursor_x = input_box.x + 10 + text_surf.get_width()
            pygame.draw.line(surface, BLACK, (cursor_x, input_box.y + 5), (cursor_x, input_box.y + 45), 2)
        
        # Instructions
        hint = font_small.render("Press ENTER to continue", True, (100, 100, 100))
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 350))
        
        pygame.display.flip()
    
    def draw_start_screen(self, surface):
        """Draw start screen with instructions and high scores"""
        surface.fill(LIGHT_BLUE)
        
        # Title
        title = font_large.render("FLAPPY PENGUIN", True, RED)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
        
        # Welcome message
        welcome = font_small.render(f"Welcome, {self.player_name}!", True, BLACK)
        surface.blit(welcome, (SCREEN_WIDTH // 2 - welcome.get_width() // 2, 90))
        
        # High scores
        scores_text = font_medium.render("HIGH SCORES", True, RED)
        surface.blit(scores_text, (SCREEN_WIDTH // 2 - scores_text.get_width() // 2, 140))
        
        top_scores = score_manager.get_top_scores(5)
        y = 190
        if top_scores:
            for i, (name, score) in enumerate(top_scores, 1):
                score_line = font_tiny.render(f"{i}. {name}: {score}", True, BLACK)
                surface.blit(score_line, (SCREEN_WIDTH // 2 - score_line.get_width() // 2, y))
                y += 30
        else:
            no_scores = font_tiny.render("No scores yet!", True, BLACK)
            surface.blit(no_scores, (SCREEN_WIDTH // 2 - no_scores.get_width() // 2, y))
        
        # Start instructions
        start_text = font_small.render("PRESS SPACE TO START", True, YELLOW)
        surface.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 480))
        
        # Other controls
        controls = [
            "R - Change Name",
            "ESC - Quit"
        ]
        y = 520
        for control in controls:
            ctrl_text = font_tiny.render(control, True, BLACK)
            surface.blit(ctrl_text, (SCREEN_WIDTH // 2 - ctrl_text.get_width() // 2, y))
            y += 25
        
        pygame.display.flip()
    
    def draw_game_over_screen(self, surface):
        """Draw game over screen with final score"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))
        
        # Game Over text
        game_over_text = font_large.render("GAME OVER", True, RED)
        surface.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 30))
        
        # Player name
        player_text = font_medium.render(f"Player: {self.player_name}", True, WHITE)
        surface.blit(player_text, (SCREEN_WIDTH // 2 - player_text.get_width() // 2, 100))
        
        # Final score
        score_text = font_medium.render(f"SCORE: {self.score}", True, WHITE)
        surface.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 155))
        
        # Show remaining lives or game ended
        if not self.game_ended:
            # Show broken hearts and remaining hearts
            broken_text = font_small.render("Lives Lost:", True, WHITE)
            surface.blit(broken_text, (SCREEN_WIDTH // 2 - 150, 220))
            for i in range(self.total_lives - self.lives):
                self.draw_heart(surface, SCREEN_WIDTH // 2 - 120 + (i * 45), 215, 25, is_broken=True)
            
            remaining_text = font_small.render("Lives Left:", True, YELLOW)
            surface.blit(remaining_text, (SCREEN_WIDTH // 2 - 150, 280))
            for i in range(self.lives):
                self.draw_heart(surface, SCREEN_WIDTH // 2 - 120 + (i * 45), 275, 25, is_broken=False)
            
            continue_text = font_small.render("Press SPACE to Continue", True, YELLOW)
            surface.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 340))
        else:
            # Game completely ended - show all hearts broken
            all_broken_text = font_small.render("All Lives Lost!", True, RED)
            surface.blit(all_broken_text, (SCREEN_WIDTH // 2 - all_broken_text.get_width() // 2, 220))
            
            # Show all broken hearts
            for i in range(self.total_lives):
                self.draw_heart(surface, SCREEN_WIDTH // 2 - 80 + (i * 50), 270, 30, is_broken=True)
            
            # High scores section
            high_scores_label = font_medium.render("HIGH SCORES", True, YELLOW)
            surface.blit(high_scores_label, (SCREEN_WIDTH // 2 - high_scores_label.get_width() // 2, 340))
            
            # Check if new high score and update
            is_high_score = score_manager.add_score(self.player_name, self.score)
            if is_high_score and self.score > 0:
                high_score_text = font_small.render("NEW HIGH SCORE! 🎉", True, YELLOW)
                surface.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, 390))
                y_offset = 430
            else:
                y_offset = 390
            
            # Show last high scores
            top_scores = score_manager.get_top_scores(3)
            for i, (name, score) in enumerate(top_scores):
                score_line = font_tiny.render(f"{i+1}. {name}: {score}", True, WHITE)
                surface.blit(score_line, (SCREEN_WIDTH // 2 - score_line.get_width() // 2, y_offset + (i * 25)))
            
            restart_text = font_small.render("Press R to Restart", True, YELLOW)
            surface.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 480))
        
        esc_text = font_small.render("Press ESC to Menu", True, YELLOW)
        surface.blit(esc_text, (SCREEN_WIDTH // 2 - esc_text.get_width() // 2, 550))


# ==================== MAIN GAME LOOP ====================
def main():
    """Main game loop"""
    game = Game()
    running = True
    state = "name_input"  # States: name_input, start_screen, playing, game_over
    input_text = ""
    cursor_blink = 0
    
    while running:
        clock.tick(FPS)
        cursor_visible = (cursor_blink // 10) % 2 == 0
        cursor_blink += 1
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                # Name input state
                if state == "name_input":
                    if event.key == pygame.K_RETURN:
                        if input_text.strip():
                            game.player_name = input_text.strip()
                            state = "start_screen"
                            input_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        if len(input_text) < 15 and event.unicode.isalnum():
                            input_text += event.unicode
                
                # Start screen state
                elif state == "start_screen":
                    if event.key == pygame.K_SPACE:
                        game.reset()
                        state = "playing"
                    elif event.key == pygame.K_r:
                        state = "name_input"
                        input_text = ""
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                
                # Playing state
                elif state == "playing":
                    if game.game_started and not game.game_over and event.key == pygame.K_SPACE:
                        game.bird.flap()
                    elif not game.game_started and event.key == pygame.K_SPACE:
                        game.game_started = True
                
                # Game over state
                if state == "game_over":
                    if event.key == pygame.K_SPACE and not game.game_ended:
                        # Continue with another life
                        game.bird = Bird(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
                        game.pipes = []
                        game.game_over = False
                        game.game_started = False
                        state = "playing"
                    elif event.key == pygame.K_r and game.game_ended:
                        game.lives = 3
                        game.game_ended = False
                        game.reset()
                        state = "start_screen"
                    elif event.key == pygame.K_ESCAPE:
                        state = "start_screen"
        
        # Update game
        game.update()
        
        # Check if game is over
        if game.game_over and state == "playing":
            state = "game_over"
        
        # Draw
        if state == "name_input":
            game.draw_name_input_screen(screen, input_text, cursor_visible)
        elif state == "start_screen":
            game.draw_start_screen(screen)
        elif state == "playing":
            game.draw(screen)
            pygame.display.flip()
        elif state == "game_over":
            game.draw(screen)
            game.draw_game_over_screen(screen)
            pygame.display.flip()
    
    pygame.quit()
    sys.exit()


# ==================== RUN GAME ====================
if __name__ == "__main__":
    main()
