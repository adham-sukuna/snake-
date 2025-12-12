"""
🚧 العوائق والأشياء المتحركة
"""

import pygame
import random
import math
from config import *

class Obstacle:
    """عائق أساسي"""
    def __init__(self, x, y, obstacle_type='wall'):
        self.x = x
        self.y = y
        self.obstacle_type = obstacle_type
        self.color = OBSTACLE_COLORS.get(obstacle_type, (128, 128, 128))
        self.size = GRID_SIZE
        self.active = True
        
    def update(self, dt):
        """تحديث العائق"""
        pass  # العوائق الأساسية ثابتة
    
    def draw(self, screen, camera):
        """رسم العائق"""
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        obstacle_size = self.size * camera.zoom
        
        if self.obstacle_type == 'wall':
            # جدار من الطوب
            pygame.draw.rect(screen, self.color,
                           (screen_x - obstacle_size//2,
                            screen_y - obstacle_size//2,
                            obstacle_size,
                            obstacle_size))
            
            # تفاصيل الطوب
            brick_size = obstacle_size / 4
            for i in range(4):
                for j in range(4):
                    brick_color = (
                        max(0, self.color[0] + (20 if (i+j) % 2 == 0 else -20)),
                        max(0, self.color[1] + (20 if (i+j) % 2 == 0 else -20)),
                        max(0, self.color[2] + (20 if (i+j) % 2 == 0 else -20))
                    )
                    pygame.draw.rect(screen, brick_color,
                                   (screen_x - obstacle_size//2 + i * brick_size,
                                    screen_y - obstacle_size//2 + j * brick_size,
                                    brick_size,
                                    brick_size), 1)
        
        elif self.obstacle_type == 'spike':
            # شوكة دوارة
            rotation = pygame.time.get_ticks() * 0.001 * 90  # 90 درجة في الثانية
            
            points = []
            for i in range(5):
                angle = math.radians(rotation + i * 72)  # 72 درجة بين كل رأس
                radius = obstacle_size * 0.5
                points.append((
                    screen_x + math.cos(angle) * radius,
                    screen_y + math.sin(angle) * radius
                ))
            pygame.draw.polygon(screen, self.color, points)
            
            # مركز الشوكة
            pygame.draw.circle(screen, (255, 255, 255),
                             (int(screen_x), int(screen_y)),
                             int(obstacle_size * 0.1))

class MovingObstacle(Obstacle):
    """عائق متحرك"""
    def __init__(self, start_x, start_y, end_x, end_y, speed=2.0):
        super().__init__(start_x, start_y, 'moving')
        self.start_pos = (start_x, start_y)
        self.end_pos = (end_x, end_y)
        self.speed = speed
        self.progress = 0.0
        self.direction = 1
        self.trail = []
        self.max_trail_length = 5
        
    def update(self, dt):
        """تحديث العائق المتحرك"""
        # تحريك العائق
        self.progress += self.direction * self.speed * dt
        if self.progress >= 1.0:
            self.progress = 1.0
            self.direction = -1
        elif self.progress <= 0.0:
            self.progress = 0.0
            self.direction = 1
        
        # حساب الموقع الحالي
        self.x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * self.progress
        self.y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * self.progress
        
        # تحديث الأثر
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
    
    def draw(self, screen, camera):
        """رسم العائق المتحرك"""
        super().draw(screen, camera)
        
        # رسم الأثر
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            trail_color = (*self.color[:3], alpha)
            screen_x, screen_y = camera.world_to_screen(trail_x, trail_y)
            trail_size = self.size * camera.zoom * 0.5
            
            trail_surface = pygame.Surface((trail_size*2, trail_size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, trail_color, 
                             (int(trail_size), int(trail_size)), int(trail_size))
            screen.blit(trail_surface, (screen_x - trail_size, screen_y - trail_size))

class ObstacleManager:
    """مدير العوائق"""
    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.obstacles = []
        self.moving_obstacles = []
        self.generate_obstacles()
    
    def generate_obstacles(self):
        """توليد العوائق"""
        # جدران الحدود
        for x in range(self.grid_width):
            self.obstacles.append(Obstacle(
                x * GRID_SIZE + GRID_SIZE // 2,
                0 + GRID_SIZE // 2,
                'wall'
            ))
            self.obstacles.append(Obstacle(
                x * GRID_SIZE + GRID_SIZE // 2,
                (self.grid_height - 1) * GRID_SIZE + GRID_SIZE // 2,
                'wall'
            ))
        
        for y in range(self.grid_height):
            self.obstacles.append(Obstacle(
                0 + GRID_SIZE // 2,
                y * GRID_SIZE + GRID_SIZE // 2,
                'wall'
            ))
            self.obstacles.append(Obstacle(
                (self.grid_width - 1) * GRID_SIZE + GRID_SIZE // 2,
                y * GRID_SIZE + GRID_SIZE // 2,
                'wall'
            ))
        
        # عوائق داخلية عشوائية
        num_obstacles = random.randint(8, 15)
        for _ in range(num_obstacles):
            x = random.randint(2, self.grid_width - 3)
            y = random.randint(2, self.grid_height - 3)
            obstacle_type = random.choice(['wall', 'spike'])
            
            self.obstacles.append(Obstacle(
                x * GRID_SIZE + GRID_SIZE // 2,
                y * GRID_SIZE + GRID_SIZE // 2,
                obstacle_type
            ))
        
        # عوائق متحركة
        num_moving = random.randint(2, 4)
        for _ in range(num_moving):
            start_x = random.randint(3, self.grid_width - 4)
            start_y = random.randint(3, self.grid_height - 4)
            end_x = start_x + random.choice([-2, 0, 2])
            end_y = start_y + random.choice([-2, 0, 2])
            
            # التأكد من أن النهاية داخل الشبكة
            end_x = max(2, min(self.grid_width - 3, end_x))
            end_y = max(2, min(self.grid_height - 3, end_y))
            
            moving_obstacle = MovingObstacle(
                start_x * GRID_SIZE + GRID_SIZE // 2,
                start_y * GRID_SIZE + GRID_SIZE // 2,
                end_x * GRID_SIZE + GRID_SIZE // 2,
                end_y * GRID_SIZE + GRID_SIZE // 2,
                speed=random.uniform(1.0, 3.0)
            )
            self.moving_obstacles.append(moving_obstacle)
    
    def update(self, dt):
        """تحديث كل العوائق"""
        for obstacle in self.moving_obstacles:
            obstacle.update(dt)
    
    def check_collision(self, x, y, radius, check_ghost=False):
        """التحقق من الاصطدام بالعوائق"""
        if check_ghost:
            return None
            
        for obstacle in self.obstacles + self.moving_obstacles:
            if not obstacle.active:
                continue
                
            distance = math.sqrt((x - obstacle.x)**2 + (y - obstacle.y)**2)
            if distance < radius + obstacle.size * 0.5:
                return obstacle.obstacle_type
        
        return None
    
    def get_obstacle_positions(self):
        """الحصول على مواقع كل العوائق"""
        positions = []
        for obstacle in self.obstacles + self.moving_obstacles:
            if obstacle.active:
                positions.append((obstacle.x, obstacle.y))
        return positions
    
    def draw(self, screen, camera):
        """رسم كل العوائق"""
        for obstacle in self.obstacles + self.moving_obstacles:
            if obstacle.active:
                obstacle.draw(screen, camera)
    
    def clear(self):
        """مسح كل العوائق"""
        self.obstacles.clear()
        self.moving_obstacles.clear()