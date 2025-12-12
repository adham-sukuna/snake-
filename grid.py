"""
🔳 الشبكة والفيزياء والاصطدامات
"""

import pygame
import random
import math
from config import *

class Grid:
    """فئة الشبكة والفيزياء"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid_width = GRID_WIDTH
        self.grid_height = GRID_HEIGHT
        self.obstacles = []
        self.generate_obstacles()
        
    def generate_obstacles(self):
        """توليد عوائق عشوائية"""
        # جدران الحدود
        for x in range(self.grid_width):
            self.obstacles.append({'type': 'wall', 'x': x, 'y': 0})
            self.obstacles.append({'type': 'wall', 'x': x, 'y': self.grid_height-1})
        
        for y in range(self.grid_height):
            self.obstacles.append({'type': 'wall', 'x': 0, 'y': y})
            self.obstacles.append({'type': 'wall', 'x': self.grid_width-1, 'y': y})
        
        # عوائق داخلية
        num_obstacles = random.randint(5, 10)
        for _ in range(num_obstacles):
            obs_type = random.choice(['wall', 'spike'])
            x = random.randint(2, self.grid_width - 3)
            y = random.randint(2, self.grid_height - 3)
            self.obstacles.append({'type': obs_type, 'x': x, 'y': y})
    
    def check_collision(self, x, y, radius, check_ghost=False):
        """التحقق من الاصطدام بالعوائق"""
        if check_ghost:
            return False
            
        grid_x = int(x // GRID_SIZE)
        grid_y = int(y // GRID_SIZE)
        
        for obstacle in self.obstacles:
            if obstacle['x'] == grid_x and obstacle['y'] == grid_y:
                return obstacle['type']
        
        return None
    
    def get_obstacle_positions(self):
        """الحصول على مواقع العوائق"""
        positions = []
        for obstacle in self.obstacles:
            positions.append((
                obstacle['x'] * GRID_SIZE + GRID_SIZE // 2,
                obstacle['y'] * GRID_SIZE + GRID_SIZE // 2
            ))
        return positions
    
    def is_position_valid(self, x, y, snake_positions=None, padding=1):
        """التحقق إذا الموقع صالح"""
        grid_x = int(x // GRID_SIZE)
        grid_y = int(y // GRID_SIZE)
        
        # التحقق من العوائق
        for obstacle in self.obstacles:
            if obstacle['x'] == grid_x and obstacle['y'] == grid_y:
                return False
        
        # التحقق من الثعبان
        if snake_positions:
            for pos in snake_positions:
                distance = math.sqrt((x - pos[0])**2 + (y - pos[1])**2)
                if distance < GRID_SIZE * padding:
                    return False
        
        return True

class Camera:
    """فئة الكاميرا للمتابعة والتقريب"""
    def __init__(self, width, height):
        self.x = width // 2
        self.y = height // 2
        self.target_x = self.x
        self.target_y = self.y
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.width = width
        self.height = height
        
    def follow(self, target_x, target_y):
        """متابعة هدف"""
        self.target_x = target_x
        self.target_y = target_y
    
    def update(self, dt):
        """تحديث الكاميرا"""
        # سلاسة الحركة
        self.x += (self.target_x - self.x) * CAMERA_SMOOTHNESS
        self.y += (self.target_y - self.y) * CAMERA_SMOOTHNESS
        
        # سلاسة التقريب
        self.zoom += (self.target_zoom - self.zoom) * ZOOM_SPEED
    
    def set_zoom(self, zoom):
        """ضبط مستوى التقريب"""
        self.target_zoom = max(0.5, min(2.0, zoom))
    
    def world_to_screen(self, world_x, world_y):
        """تحويل من إحداثيات العالم إلى الشاشة"""
        screen_x = (world_x - self.x) * self.zoom + self.width // 2
        screen_y = (world_y - self.y) * self.zoom + self.height // 2
        return screen_x, screen_y
    
    def screen_to_world(self, screen_x, screen_y):
        """تحويل من إحداثيات الشاشة إلى العالم"""
        world_x = (screen_x - self.width // 2) / self.zoom + self.x
        world_y = (screen_y - self.height // 2) / self.zoom + self.y
        return world_x, world_y