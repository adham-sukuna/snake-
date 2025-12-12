"""
🎨 الرسومات والرسم والتأثيرات البصرية
"""

import pygame
import math
from config import *

class Graphics:
    """فئة الرسومات الرئيسية"""
    def __init__(self, screen):
        self.screen = screen
        self.load_fonts()
        self.load_textures()
        self.camera = None
        self.effects = []
        
    def load_fonts(self):
        """تحميل الخطوط"""
        try:
            self.title_font = pygame.font.Font(None, TITLE_FONT_SIZE)
            self.menu_font = pygame.font.Font(None, MENU_FONT_SIZE)
            self.score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
            self.game_font = pygame.font.Font(None, GAME_FONT_SIZE)
            self.small_font = pygame.font.Font(None, SMALL_FONT_SIZE)
        except:
            self.title_font = pygame.font.SysFont('arial', TITLE_FONT_SIZE, bold=True)
            self.menu_font = pygame.font.SysFont('arial', MENU_FONT_SIZE, bold=True)
            self.score_font = pygame.font.SysFont('arial', SCORE_FONT_SIZE)
            self.game_font = pygame.font.SysFont('arial', GAME_FONT_SIZE)
            self.small_font = pygame.font.SysFont('arial', SMALL_FONT_SIZE)
    
    def load_textures(self):
        """تحميل القوام (يمكن إضافة صور حقيقية لاحقاً)"""
        self.textures = {
            'snake_head': self.create_snake_head_texture(),
            'food': self.create_food_texture(),
            'obstacle': self.create_obstacle_texture(),
        }
    
    def create_snake_head_texture(self):
        """إنشاء قوام رأس الثعبان"""
        size = GRID_SIZE
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # رسم رأس الثعبان
        pygame.draw.circle(surface, SNAKE_HEAD_COLOR, (size//2, size//2), size//2)
        
        # العيون
        eye_size = size // 5
        pygame.draw.circle(surface, SNAKE_EYE_COLOR, (size//3, size//3), eye_size)
        pygame.draw.circle(surface, SNAKE_EYE_COLOR, (2*size//3, size//3), eye_size)
        
        # بؤبؤ العين
        pupil_size = eye_size // 2
        pygame.draw.circle(surface, SNAKE_PUPIL_COLOR, (size//3, size//3), pupil_size)
        pygame.draw.circle(surface, SNAKE_PUPIL_COLOR, (2*size//3, size//3), pupil_size)
        
        return surface
    
    def create_food_texture(self):
        """إنشاء قوام الطعام"""
        size = int(GRID_SIZE * 0.8)
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # التفاحة
        pygame.draw.circle(surface, FOOD_COLOR, (size//2, size//2), size//2)
        
        # الساق
        pygame.draw.rect(surface, (139, 69, 19), 
                        (size//2 - 2, 2, 4, size//4))
        
        # الورقة
        leaf_points = [
            (size//2, size//4),
            (size//2 + size//3, size//5),
            (size//2 + size//4, size//3)
        ]
        pygame.draw.polygon(surface, (34, 139, 34), leaf_points)
        
        return surface
    
    def create_obstacle_texture(self):
        """إنشاء قوام العوائق"""
        size = GRID_SIZE
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # جدار من الطوب
        brick_color = (150, 150, 150)
        for i in range(0, size, 4):
            for j in range(0, size, 8):
                offset = 0 if (j//8) % 2 == 0 else 2
                pygame.draw.rect(surface, brick_color, 
                               (i + offset, j, 4, 4))
        
        return surface
    
    def set_camera(self, camera):
        """ضبط الكاميرا"""
        self.camera = camera
    
    def clear_screen(self):
        """مسح الشاشة"""
        self.screen.fill(BACKGROUND_COLOR)
    
    def draw_grid(self):
        """رسم الشبكة"""
        if not self.camera:
            return
            
        # خطوط أفقية
        for y in range(0, GRID_HEIGHT * GRID_SIZE, GRID_SIZE):
            start_world = (0, y)
            end_world = (GRID_WIDTH * GRID_SIZE, y)
            start_screen = self.camera.world_to_screen(*start_world)
            end_screen = self.camera.world_to_screen(*end_world)
            pygame.draw.line(self.screen, GRID_LINE_COLOR, start_screen, end_screen, 1)
        
        # خطوط رأسية
        for x in range(0, GRID_WIDTH * GRID_SIZE, GRID_SIZE):
            start_world = (x, 0)
            end_world = (x, GRID_HEIGHT * GRID_SIZE)
            start_screen = self.camera.world_to_screen(*start_world)
            end_screen = self.camera.world_to_screen(*end_world)
            pygame.draw.line(self.screen, GRID_LINE_COLOR, start_screen, end_screen, 1)
    
    def draw_snake(self, snake):
        """رسم الثعبان"""
        if not self.camera:
            return
        
        # الرأس
        head_x, head_y = snake.head.x, snake.head.y
        screen_x, screen_y = self.camera.world_to_screen(head_x, head_y)
        head_size = GRID_SIZE * self.camera.zoom * 0.9
        
        # تأثيرات خاصة للرأس
        head_color = snake.head.color
        if snake.powerups['invincible']:
            # وميض للمناعة
            pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 0.5
            head_color = (
                int(255 * pulse),
                int(255 * pulse),
                int(255 * pulse)
            )
        
        # رسم الرأس
        pygame.draw.circle(self.screen, head_color, 
                          (int(screen_x), int(screen_y)), 
                          int(head_size // 2))
        
        # العيون (تتجه باتجاه الحركة)
        angle = math.atan2(snake.direction[1], snake.direction[0])
        eye_distance = head_size * 0.3
        
        left_eye_x = screen_x + math.cos(angle - 0.3) * eye_distance
        left_eye_y = screen_y + math.sin(angle - 0.3) * eye_distance
        right_eye_x = screen_x + math.cos(angle + 0.3) * eye_distance
        right_eye_y = screen_y + math.sin(angle + 0.3) * eye_distance
        
        eye_size = head_size * 0.15
        pygame.draw.circle(self.screen, SNAKE_EYE_COLOR, 
                          (int(left_eye_x), int(left_eye_y)), 
                          int(eye_size))
        pygame.draw.circle(self.screen, SNAKE_EYE_COLOR, 
                          (int(right_eye_x), int(right_eye_y)), 
                          int(eye_size))
        
        # اللسان (للسان أطول عندما يكون سريعاً)
        if snake.speed > INITIAL_SPEED * 1.2:
            tongue_length = head_size * 0.8
            tongue_x = screen_x + math.cos(angle) * tongue_length
            tongue_y = screen_y + math.sin(angle) * tongue_length
            pygame.draw.line(self.screen, SNAKE_TONGUE_COLOR,
                           (screen_x, screen_y),
                           (tongue_x, tongue_y), 3)
        
        # الجسم
        for i, segment in enumerate(snake.body):
            seg_x, seg_y = segment.x, segment.y
            screen_x, screen_y = self.camera.world_to_screen(seg_x, seg_y)
            segment_size = GRID_SIZE * self.camera.zoom * 0.8
            
            # تدرج اللون من الرأس إلى الذيل
            color_ratio = i / max(1, len(snake.body))
            body_color = (
                int(SNAKE_BODY_COLOR[0] * (1 - color_ratio * 0.3)),
                int(SNAKE_BODY_COLOR[1] * (1 - color_ratio * 0.3)),
                int(SNAKE_BODY_COLOR[2] * (1 - color_ratio * 0.3))
            )
            
            # تأثير تموج الجسم
            wobble = math.sin(snake.wobble_phase + i * 0.5) * 0.1
            wobble_size = segment_size * (1 + wobble)
            
            pygame.draw.circle(self.screen, body_color,
                             (int(screen_x), int(screen_y)),
                             int(wobble_size // 2))
    
    def draw_food(self, food_manager):
        """رسم الطعام"""
        if not self.camera:
            return
        
        # الطعام العادي
        for food in food_manager.foods:
            screen_x, screen_y = self.camera.world_to_screen(food.position[0], food.position[1])
            food_size = food.size * self.camera.zoom
            
            # توهج
            glow_size = food_size * (1 + food.glow_intensity * 0.3)
            glow_surface = pygame.Surface((int(glow_size*2), int(glow_size*2)), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*FOOD_GLOW_COLOR[:3], int(100 * food.glow_intensity)),
                             (int(glow_size), int(glow_size)), int(glow_size))
            self.screen.blit(glow_surface, (screen_x - glow_size, screen_y - glow_size))
            
            # التفاحة
            pygame.draw.circle(self.screen, food.color,
                             (int(screen_x), int(screen_y)),
                             int(food_size // 2))
            
            # دوران
            rotated_food = pygame.transform.rotate(
                pygame.Surface((int(food_size), int(food_size)), pygame.SRCALPHA),
                food.rotation
            )
            food_rect = rotated_food.get_rect(center=(int(screen_x), int(screen_y)))
            temp_surface = pygame.Surface((int(food_size), int(food_size)), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, food.color,
                             (int(food_size//2), int(food_size//2)),
                             int(food_size//2))
            rotated_food = pygame.transform.rotate(temp_surface, food.rotation)
            self.screen.blit(rotated_food, food_rect)
        
        # الطعام الخاص
        for food in food_manager.special_foods:
            screen_x, screen_y = self.camera.world_to_screen(food.position[0], food.position[1])
            food_size = food.size * self.camera.zoom
            
            # توهج قوي
            glow_size = food_size * (1 + food.glow_intensity * 0.5)
            for i in range(3):
                glow_radius = glow_size * (1 + i * 0.2)
                glow_alpha = int(50 * food.glow_intensity * (1 - i * 0.3))
                glow_surface = pygame.Surface((int(glow_radius*2), int(glow_radius*2)), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*food.color, glow_alpha),
                                 (int(glow_radius), int(glow_radius)), int(glow_radius))
                self.screen.blit(glow_surface, (screen_x - glow_radius, screen_y - glow_radius))
            
            # رمز خاص حسب النوع
            pygame.draw.circle(self.screen, food.color,
                             (int(screen_x), int(screen_y)),
                             int(food_size // 2))
            
            # رسم رمز داخلي
            symbol_size = food_size * 0.5
            if food.food_type == 'golden':
                # نجمة
                self.draw_star(screen_x, screen_y, symbol_size, (255, 255, 200))
            elif food.food_type == 'speed':
                # سهم
                self.draw_arrow(screen_x, screen_y, symbol_size, (255, 255, 255))
            elif food.food_type == 'shield':
                # درع
                self.draw_shield(screen_x, screen_y, symbol_size, (255, 255, 255))
    
    def draw_obstacles(self, grid):
        """رسم العوائق"""
        if not self.camera:
            return
        
        for obstacle in grid.obstacles:
            world_x = obstacle['x'] * GRID_SIZE + GRID_SIZE // 2
            world_y = obstacle['y'] * GRID_SIZE + GRID_SIZE // 2
            screen_x, screen_y = self.camera.world_to_screen(world_x, world_y)
            obstacle_size = GRID_SIZE * self.camera.zoom
            
            color = OBSTACLE_COLORS.get(obstacle['type'], OBSTACLE_COLORS['wall'])
            
            if obstacle['type'] == 'wall':
                # جدار
                pygame.draw.rect(self.screen, color,
                               (int(screen_x - obstacle_size//2),
                                int(screen_y - obstacle_size//2),
                                int(obstacle_size),
                                int(obstacle_size)))
                
                # نسيج الطوب
                brick_size = obstacle_size / 4
                for i in range(4):
                    for j in range(4):
                        brick_color = (
                            max(0, color[0] + (20 if (i+j) % 2 == 0 else -20)),
                            max(0, color[1] + (20 if (i+j) % 2 == 0 else -20)),
                            max(0, color[2] + (20 if (i+j) % 2 == 0 else -20))
                        )
                        pygame.draw.rect(self.screen, brick_color,
                                       (int(screen_x - obstacle_size//2 + i * brick_size),
                                        int(screen_y - obstacle_size//2 + j * brick_size),
                                        int(brick_size),
                                        int(brick_size)), 1)
            
            elif obstacle['type'] == 'spike':
                # شوكة
                points = []
                for i in range(5):
                    angle = i * 2 * math.pi / 5
                    radius = obstacle_size * 0.5 if i % 2 == 0 else obstacle_size * 0.3
                    points.append((
                        screen_x + math.cos(angle) * radius,
                        screen_y + math.sin(angle) * radius
                    ))
                pygame.draw.polygon(self.screen, color, points)
    
    def draw_star(self, x, y, size, color):
        """رسم نجمة"""
        points = []
        for i in range(10):
            angle = i * math.pi / 5
            radius = size if i % 2 == 0 else size * 0.4
            points.append((
                x + math.cos(angle) * radius,
                y + math.sin(angle) * radius
            ))
        pygame.draw.polygon(self.screen, color, points)
    
    def draw_arrow(self, x, y, size, color):
        """رسم سهم"""
        # جسم السهم
        pygame.draw.polygon(self.screen, color, [
            (x - size//2, y - size//4),
            (x + size//2, y),
            (x - size//2, y + size//4)
        ])
    
    def draw_shield(self, x, y, size, color):
        """رسم درع"""
        # دائرة خارجية
        pygame.draw.circle(self.screen, color, (int(x), int(y)), int(size//2), 3)
        # دائرة داخلية
        pygame.draw.circle(self.screen, color, (int(x), int(y)), int(size//3), 2)
        # صليب
        pygame.draw.line(self.screen, color,
                        (x - size//4, y),
                        (x + size//4, y), 3)
        pygame.draw.line(self.screen, color,
                        (x, y - size//4),
                        (x, y + size//4), 3)
    
    def draw_powerup_indicators(self, snake, screen_width, screen_height):
        """رسم مؤشرات القدرات الخاصة"""
        if not snake.powerups:
            return
        
        y_pos = screen_height - 40
        x_start = 20
        icon_size = 30
        spacing = 10
        
        active_powerups = [p for p, active in snake.powerups.items() if active]
        
        for i, powerup in enumerate(active_powerups):
            x = x_start + i * (icon_size + spacing)
            
            # خلفية المؤشر
            pygame.draw.rect(self.screen, UI_BACKGROUND,
                           (x - 5, y_pos - 5, icon_size + 10, icon_size + 10),
                           border_radius=5)
            
            # الرمز
            color = POWERUP_COLORS.get(powerup, (255, 255, 255))
            if powerup == 'shield':
                self.draw_shield(x + icon_size//2, y_pos + icon_size//2, icon_size, color)
            elif powerup == 'speed_boost':
                self.draw_arrow(x + icon_size//2, y_pos + icon_size//2, icon_size, color)
            elif powerup == 'invincible':
                pygame.draw.circle(self.screen, color,
                                 (x + icon_size//2, y_pos + icon_size//2),
                                 icon_size//2)
            elif powerup == 'double_points':
                self.draw_star(x + icon_size//2, y_pos + icon_size//2, icon_size//2, color)
            
            # مؤقت القدرة
            if powerup in snake.powerup_timers:
                timer = snake.powerup_timers[powerup]
                timer_text = self.small_font.render(f"{timer:.1f}s", True, UI_TEXT_COLOR)
                self.screen.blit(timer_text, (x, y_pos + icon_size + 5))
    
    def draw_score(self, score, high_score, level, screen_width):
        """رسم النقاط والمستوى"""
        # خلفية النقاط
        score_bg = pygame.Rect(20, 20, 300, 80)
        pygame.draw.rect(self.screen, UI_BACKGROUND, score_bg, border_radius=10)
        pygame.draw.rect(self.screen, UI_ACCENT_COLOR, score_bg, 2, border_radius=10)
        
        # النقاط الحالية
        score_text = self.score_font.render(f"Score: {score}", True, UI_TEXT_COLOR)
        self.screen.blit(score_text, (40, 30))
        
        # أعلى نقاط
        high_score_text = self.score_font.render(f"High Score: {high_score}", True, UI_TEXT_COLOR)
        self.screen.blit(high_score_text, (40, 60))
        
        # المستوى
        level_text = self.game_font.render(f"Level: {level}", True, UI_ACCENT_COLOR)
        level_rect = level_text.get_rect(topright=(screen_width - 40, 30))
        self.screen.blit(level_text, level_rect)
    
    def draw_game_over(self, score, high_score, screen_width, screen_height):
        """رسم شاشة انتهاء اللعبة"""
        # طبقة شفافة
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # نافذة النهاية
        game_over_rect = pygame.Rect(screen_width//2 - 200, screen_height//2 - 150, 400, 300)
        pygame.draw.rect(self.screen, (40, 40, 60), game_over_rect, border_radius=20)
        pygame.draw.rect(self.screen, UI_ACCENT_COLOR, game_over_rect, 3, border_radius=20)
        
        # العنوان
        title = self.title_font.render("Game Over", True, (255, 100, 100))
        self.screen.blit(title, (screen_width//2 - title.get_width()//2, game_over_rect.y + 30))
        
        # النقاط النهائية
        score_text = self.menu_font.render(f"Final Score: {score}", True, UI_TEXT_COLOR)
        self.screen.blit(score_text, (screen_width//2 - score_text.get_width()//2, game_over_rect.y + 100))
        
        # أعلى نقاط
        high_score_text = self.menu_font.render(f"High Score: {high_score}", True, UI_TEXT_COLOR)
        self.screen.blit(high_score_text, (screen_width//2 - high_score_text.get_width()//2, game_over_rect.y + 150))
        
        # رسالة
        if score == high_score:
            message = self.menu_font.render("🎉 New Record! 🎉", True, (255, 215, 0))
            self.screen.blit(message, (screen_width//2 - message.get_width()//2, game_over_rect.y + 200))
        else:
            message = self.score_font.render("Press SPACE to play again", True, (200, 200, 200))
            self.screen.blit(message, (screen_width//2 - message.get_width()//2, game_over_rect.y + 220))

    def draw_controls_hint(self, screen, screen_width, screen_height):
        """رسم تلميح التحكم"""
        controls_text = self.small_font.render(
            "Use arrow keys to move | U: Undo | R: Reset | ESC: Pause | H: Hint",
            True, (150, 150, 150)
        )
        screen.blit(controls_text, 
                   (screen_width//2 - controls_text.get_width()//2, 
                    screen_height - 30))