"""
🎮 حالات اللعبة المختلفة
"""

import math
import random
import pygame
from config import *

class GameState:
    """حالة اللعبة الأساسية"""
    def __init__(self):
        self.next_state = None
    
    def handle_events(self, events):
        """معالجة الأحداث"""
        pass
    
    def update(self, dt):
        """التحديث"""
        pass
    
    def draw(self, screen):
        """الرسم"""
        pass
    
    def get_next_state(self):
        """الحصول على الحالة التالية"""
        return self.next_state

class MainMenuState(GameState):
    """حالة القائمة الرئيسية"""
    def __init__(self, screen_width, screen_height):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        from ui import Menu
        self.menu = Menu(screen_width, screen_height)
        self.background_phase = 0
        
    def handle_events(self, events):
        """معالجة أحداث القائمة"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        keys = pygame.key.get_pressed()
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_clicked = True
        
        self.menu.update(mouse_pos, mouse_clicked, keys)
        
        # التحقق من تغيير الحالة
        result = self.menu.update(mouse_pos, mouse_clicked, keys)
        if result == "start_game":
            self.next_state = "playing"
        elif result == "exit":
            self.next_state = "quit"
    
    def update(self, dt):
        """تحديث القائمة"""
        self.background_phase += dt * 0.5
    
    def draw(self, screen):
        """رسم القائمة"""
        # خلفية متحركة
        screen.fill(BACKGROUND_COLOR)
        
        # رسم نمط خلفي
        for i in range(0, self.screen_width, 50):
            for j in range(0, self.screen_height, 50):
                x = i + math.sin(self.background_phase + i * 0.01) * 10
                y = j + math.cos(self.background_phase + j * 0.01) * 10
                
                color_val = 30 + abs(math.sin(self.background_phase + i * 0.02 + j * 0.01)) * 20
                color = (color_val, color_val + 10, color_val + 20)
                
                pygame.draw.rect(screen, color, (x, y, 45, 45), border_radius=8)
        
        # التعديل هنا: تمرير screen فقط بدون graphics
        self.menu.draw(screen)

class PlayingState(GameState):
    """حالة اللعب"""
    def __init__(self, screen_width, screen_height):
        super().__init__()
        from snake import Snake
        from food import FoodManager
        from grid import Grid, Camera
        from graphics import Graphics
        from score import ScoreManager
        from particles import ParticleSystem
        from obstacles import ObstacleManager
        from powerups import PowerUpManager
        from audio import AudioManager
        
        # تهيئة المكونات
        self.grid = Grid(screen_width, screen_height)
        self.camera = Camera(screen_width, screen_height)
        self.graphics = Graphics(pygame.Surface((1, 1)))  # سطح مؤقت
        self.graphics.set_camera(self.camera)
        
        # إدارة الكيانات
        self.snake = Snake(GRID_SIZE * 5, GRID_SIZE * 5)
        self.food_manager = FoodManager(GRID_WIDTH, GRID_HEIGHT)
        self.obstacle_manager = ObstacleManager(GRID_WIDTH, GRID_HEIGHT)
        self.powerup_manager = PowerUpManager(GRID_WIDTH, GRID_HEIGHT)
        self.score_manager = ScoreManager()
        self.particle_system = ParticleSystem()
        self.audio = AudioManager()
        
        # توليد الطعام الأولي
        self.food_manager.spawn_food(self.snake.get_body_positions())
        self.food_manager.spawn_food(self.snake.get_body_positions())
        
        # الحالة
        self.paused = False
        self.game_over = False
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.shake_intensity = 0
    
    def handle_events(self, events):
        """معالجة أحداث اللعب"""
        if self.game_over:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.next_state = "restart"
                    elif event.key == pygame.K_ESCAPE:
                        self.next_state = "menu"
            return
        
        if self.paused:
            from ui import PauseMenu
            pause_menu = PauseMenu(self.screen_width, self.screen_height)
            
            mouse_pos = pygame.mouse.get_pos()
            mouse_clicked = False
            
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_clicked = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = False
            
            pause_menu.update(mouse_pos, mouse_clicked)
            result = pause_menu.update(mouse_pos, mouse_clicked)
            
            if result == "resume":
                self.paused = False
            elif result == "restart":
                self.next_state = "restart"
            elif result == "main_menu":
                self.next_state = "menu"
            
            return
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = True
                elif event.key == pygame.K_UP:
                    self.snake.change_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    self.snake.change_direction((0, 1))
                elif event.key == pygame.K_LEFT:
                    self.snake.change_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    self.snake.change_direction((1, 0))
                elif event.key == pygame.K_w:
                    self.snake.change_direction((0, -1))
                elif event.key == pygame.K_s:
                    self.snake.change_direction((0, 1))
                elif event.key == pygame.K_a:
                    self.snake.change_direction((-1, 0))
                elif event.key == pygame.K_d:
                    self.snake.change_direction((1, 0))
    
    def update(self, dt):
        """تحديث حالة اللعب"""
        if self.paused or self.game_over:
            return
        
        # تحديث الثعبان
        self.snake.update(dt, self.food_manager.get_all_food_positions())
        
        # تحديث الطعام
        self.food_manager.update(dt, self.snake.get_body_positions())
        
        # تحديث العوائق
        self.obstacle_manager.update(dt)
        
        # تحديث المكافآت
        self.powerup_manager.update(dt, self.snake.get_body_positions())
        
        # تحديث النقاط
        self.score_manager.update(dt)
        
        # تحديث الجسيمات
        self.particle_system.update(dt)
        
        # تحديث الكاميرا لمتابعة الثعبان
        snake_head = self.snake.get_head_position()
        self.camera.follow(snake_head[0], snake_head[1])
        self.camera.update(dt)
        
        # التحقق من اصطدام الطعام
        eaten_foods, eaten_specials = self.food_manager.check_collisions(snake_head)
        
        for food in eaten_foods:
            # إضافة النقاط
            points = self.score_manager.add_food_score('normal')
            
            # تأثيرات
            self.particle_system.create_food_particles(food.position[0], food.position[1], 'normal')
            self.audio.play_eat()
            
            # توليد طعام جديد
            self.food_manager.spawn_food(self.snake.get_body_positions())
            
            # زيادة سرعة الثعبان كل 5 أطعمة
            if self.snake.length % 5 == 0:
                self.snake.speed = min(MAX_SPEED, self.snake.speed + SPEED_INCREMENT)
        
        for food in eaten_specials:
            # إضافة النقاط الخاصة
            points = self.score_manager.add_food_score(food.food_type)
            
            # تطبيق تأثير الطعام الخاص
            effect = food.properties['effect']
            if effect == 'speed_boost':
                self.snake.add_powerup('speed_boost', 8.0)
            elif effect == 'shield':
                self.snake.add_powerup('shield', 10.0)
            elif effect == 'magnet':
                self.snake.add_powerup('magnet', 12.0)
            
            # تأثيرات
            self.particle_system.create_food_particles(food.position[0], food.position[1], food.food_type)
            self.audio.play_special_eat(food.food_type)
        
        # التحقق من اصطدام المكافآت
        collected_powerups = self.powerup_manager.check_collisions(snake_head)
        
        for powerup in collected_powerups:
            effect = powerup.get_effect()
            
            # تطبيق التأثير
            if powerup.powerup_type == 'teleport':
                # الانتقال العشوائي
                new_x = random.randint(2, GRID_WIDTH - 3) * GRID_SIZE + GRID_SIZE // 2
                new_y = random.randint(2, GRID_HEIGHT - 3) * GRID_SIZE + GRID_SIZE // 2
                self.snake.head.x = new_x
                self.snake.head.y = new_y
            elif powerup.powerup_type == 'bomb':
                # تدمير العوائق القريبة
                bomb_radius = GRID_SIZE * 3
                obstacles = self.obstacle_manager.get_obstacle_positions()
                for obs_x, obs_y in obstacles:
                    distance = math.sqrt((obs_x - snake_head[0])**2 + (obs_y - snake_head[1])**2)
                    if distance < bomb_radius:
                        # يمكن إضافة منطق لإزالة العائق هنا
                        pass
                self.particle_system.create_explosion(snake_head[0], snake_head[1])
            else:
                self.snake.add_powerup(powerup.powerup_type, effect.get('duration', 10.0))
            
            # تأثيرات
            self.audio.play_powerup(powerup.powerup_type)
            self.particle_system.create_explosion(powerup.x, powerup.y, powerup.color)
        
        # التحقق من الاصطدام بالعوائق
        if not self.snake.powerups['invincible']:
            collision_type = self.obstacle_manager.check_collision(
                snake_head[0], snake_head[1], 
                GRID_SIZE * 0.5, 
                self.snake.powerups['ghost']
            )
            
            if collision_type:
                self.handle_collision(collision_type)
        
        # التحقق من الاصطدام بالنفس
        if self.snake.check_self_collision() and not self.snake.powerups['invincible']:
            self.handle_collision('self')
        
        # التحقق من خروج عن الحدود
        if self.snake.check_wall_collision(GRID_WIDTH, GRID_HEIGHT):
            self.handle_collision('wall')
        
        # تحديث اهتزاز الشاشة
        if self.shake_intensity > 0:
            self.shake_intensity -= dt * 10
    
    def handle_collision(self, collision_type):
        """معالجة الاصطدام"""
        if self.snake.powerups['shield']:
            # استخدام الدرع
            self.snake.remove_powerup('shield')
            self.shake_intensity = 5
            self.audio.play_collision()
            self.particle_system.create_explosion(
                self.snake.head.x, 
                self.snake.head.y,
                (100, 150, 255)  # لون درعي
            )
            return
        
        # نهاية اللعبة
        self.game_over = True
        self.snake.die()
        self.audio.play_game_over()
        self.particle_system.create_explosion(
            self.snake.head.x, 
            self.snake.head.y,
            (255, 50, 50)  # لون أحمر
        )
        
        # حفظ النقاط
        self.score_manager.save_high_score()
    
    def draw(self, screen):
        """رسم حالة اللعب"""
        # استخدام سطح مؤقت للاهتزاز
        if self.shake_intensity > 0:
            temp_surface = pygame.Surface((self.screen_width, self.screen_height))
            self.draw_game(temp_surface)
            
            # تطبيق الاهتزاز
            shake_x = random.uniform(-self.shake_intensity, self.shake_intensity)
            shake_y = random.uniform(-self.shake_intensity, self.shake_intensity)
            screen.blit(temp_surface, (shake_x, shake_y))
        else:
            self.draw_game(screen)
        
        # رسم واجهة الإيقاف المؤقت
        if self.paused:
            from ui import PauseMenu
            pause_menu = PauseMenu(self.screen_width, self.screen_height)
            pause_menu.draw(screen, self.graphics)
        
        # رسم واجهة نهاية اللعبة
        if self.game_over:
            self.graphics.draw_game_over(
                self.score_manager.score,
                self.score_manager.high_score,
                self.screen_width,
                self.screen_height
            )
    
    def draw_game(self, screen):
        """رسم عناصر اللعبة"""
        # تعيين السطح للرسومات
        self.graphics.screen = screen
        
        # مسح الشاشة
        self.graphics.clear_screen()
        
        # رسم الشبكة
        self.graphics.draw_grid()
        
        # رسم العوائق
        self.obstacle_manager.draw(screen, self.camera)
        
        # رسم الطعام
        self.food_manager.draw(screen, self.camera)
        
        # رسم المكافآت
        self.powerup_manager.draw(screen, self.camera)
        
        # رسم الثعبان
        self.graphics.draw_snake(self.snake)
        
        # رسم الجسيمات
        self.particle_system.draw(screen)
        
        # رسم النقاط والمعلومات
        self.graphics.draw_score(
            self.score_manager.score,
            self.score_manager.high_score,
            self.score_manager.level,
            self.screen_width
        )
        
        # رسم مؤشرات القدرات
        self.graphics.draw_powerup_indicators(self.snake, self.screen_width, self.screen_height)

class GameOverState(GameState):
    """حالة نهاية اللعبة"""
    def __init__(self, score, high_score, screen_width, screen_height):
        super().__init__()
        self.score = score
        self.high_score = high_score
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.timer = 0
        self.particles = []
        
        # إنشاء تأثيرات الجسيمات
        self.create_particles()
    
    def create_particles(self):
        """إنشاء جسيمات النهاية"""
        import random
        import math
        
        for _ in range(50):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            
            self.particles.append({
                'x': x,
                'y': y,
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-2, 2),
                'color': random.choice([
                    (255, 50, 50),    # أحمر
                    (255, 150, 50),   # برتقالي
                    (255, 255, 50),   # أصفر
                    (50, 255, 50),    # أخضر
                    (50, 150, 255),   # أزرق
                ]),
                'size': random.uniform(3, 8),
                'life': random.uniform(1, 3)
            })
    
    def handle_events(self, events):
        """معالجة أحداث نهاية اللعبة"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.next_state = "restart"
                elif event.key == pygame.K_ESCAPE:
                    self.next_state = "menu"
                elif event.key == pygame.K_r:
                    self.next_state = "restart"
    
    def update(self, dt):
        """تحديث حالة النهاية"""
        self.timer += dt
        
        # تحديث الجسيمات
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.1  # جاذبية
            particle['life'] -= dt
            
            # ارتداد من الحواف
            if particle['x'] < 0 or particle['x'] > self.screen_width:
                particle['vx'] *= -0.8
            if particle['y'] < 0 or particle['y'] > self.screen_height:
                particle['vy'] *= -0.8
            
            # إزالة الجسيمات الميتة
            if particle['life'] <= 0:
                self.particles.remove(particle)
                # إضافة جسيم جديد
                self.particles.append({
                    'x': random.randint(0, self.screen_width),
                    'y': 0,
                    'vx': random.uniform(-2, 2),
                    'vy': random.uniform(1, 3),
                    'color': random.choice([
                        (255, 50, 50),
                        (255, 150, 50),
                        (255, 255, 50),
                        (50, 255, 50),
                        (50, 150, 255),
                    ]),
                    'size': random.uniform(3, 8),
                    'life': random.uniform(1, 3)
                })
    
    def draw(self, screen):
        """رسم حالة النهاية"""
        # خلفية داكنة
        screen.fill((20, 20, 35))
        
        # رسم الجسيمات
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / 3))
            color_with_alpha = (*particle['color'], alpha)
            
            particle_surface = pygame.Surface((particle['size']*2, particle['size']*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color_with_alpha,
                             (particle['size'], particle['size']), particle['size'])
            screen.blit(particle_surface, 
                       (particle['x'] - particle['size'], particle['y'] - particle['size']))
        
        # نافذة النهاية
        game_over_rect = pygame.Rect(
            self.screen_width//2 - 250,
            self.screen_height//2 - 200,
            500, 400
        )
        
        # خلفية النافذة
        pygame.draw.rect(screen, (40, 40, 60), game_over_rect, border_radius=25)
        pygame.draw.rect(screen, (80, 200, 80), game_over_rect, 3, border_radius=25)
        
        # تأثير توهج
        glow_surface = pygame.Surface((520, 420), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (80, 200, 80, 50), 
                        glow_surface.get_rect(), border_radius=27)
        screen.blit(glow_surface, (game_over_rect.x - 10, game_over_rect.y - 10))
        
        # النصوص
        title_font = pygame.font.Font(None, 72)
        score_font = pygame.font.Font(None, 48)
        message_font = pygame.font.Font(None, 36)
        instruction_font = pygame.font.Font(None, 24)
        
        # العنوان
        title_text = title_font.render("GAME OVER", True, (255, 100, 100))
        screen.blit(title_text, 
                   (self.screen_width//2 - title_text.get_width()//2, 
                    game_over_rect.y + 30))
        
        # النقاط
        score_text = score_font.render(f"Score: {self.score}", True, (240, 240, 240))
        screen.blit(score_text, 
                   (self.screen_width//2 - score_text.get_width()//2, 
                    game_over_rect.y + 120))
        
        # أعلى نقاط
        high_score_text = score_font.render(f"High Score: {self.high_score}", True, (240, 240, 240))
        screen.blit(high_score_text, 
                   (self.screen_width//2 - high_score_text.get_width()//2, 
                    game_over_rect.y + 180))
        
        # رسالة خاصة لأعلى نقاط جديد
        if self.score >= self.high_score:
            record_text = message_font.render("🎉 NEW RECORD! 🎉", True, (255, 215, 0))
            screen.blit(record_text, 
                       (self.screen_width//2 - record_text.get_width()//2, 
                        game_over_rect.y + 240))
        
        # التعليمات
        instruction1 = instruction_font.render("Press SPACE to play again", True, (180, 180, 180))
        instruction2 = instruction_font.render("Press ESC for main menu", True, (180, 180, 180))
        
        screen.blit(instruction1, 
                   (self.screen_width//2 - instruction1.get_width()//2, 
                    game_over_rect.y + 300))
        screen.blit(instruction2, 
                   (self.screen_width//2 - instruction2.get_width()//2, 
                    game_over_rect.y + 330))