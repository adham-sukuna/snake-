"""
🍎 الطعام والطعام الخاص
"""

import pygame
import random
import math
from config import *

class Food:
    """فئة الطعام الأساسي"""
    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.position = self.generate_position()
        self.color = FOOD_COLOR
        self.size = GRID_SIZE * 0.7
        self.glow_intensity = 0
        self.rotation = 0
        self.pulse_speed = 3
        
    def generate_position(self):
        """توليد موقع عشوائي للطعام"""
        x = random.randint(0, self.grid_width - 1) * GRID_SIZE + GRID_SIZE // 2
        y = random.randint(0, self.grid_height - 1) * GRID_SIZE + GRID_SIZE // 2
        return [x, y]
    
    def update(self, dt):
        """تحديث حالة الطعام"""
        self.rotation += dt * 50
        self.glow_intensity = (math.sin(pygame.time.get_ticks() * 0.001 * self.pulse_speed) + 1) * 0.5
    
    def check_collision(self, snake_head_pos):
        """التحقق من اصطدام الثعبان بالطعام"""
        distance = math.sqrt(
            (self.position[0] - snake_head_pos[0])**2 +
            (self.position[1] - snake_head_pos[1])**2
        )
        return distance < GRID_SIZE * 0.8
    
    def respawn(self, snake_positions):
        """إعادة ظهور الطعام في موقع جديد"""
        attempts = 0
        while attempts < 100:  # منع التكرار اللانهائي
            self.position = self.generate_position()
            
            # التأكد من أن الطعام ليس على الثعبان
            valid_position = True
            for pos in snake_positions:
                distance = math.sqrt(
                    (self.position[0] - pos[0])**2 +
                    (self.position[1] - pos[1])**2
                )
                if distance < GRID_SIZE * 1.5:
                    valid_position = False
                    break
            
            if valid_position:
                return
            
            attempts += 1

class SpecialFood(Food):
    """طعام خاص بقدرات مختلفة"""
    def __init__(self, grid_width, grid_height, food_type='golden'):
        super().__init__(grid_width, grid_height)
        self.food_type = food_type
        self.color = SPECIAL_FOOD_COLORS.get(food_type, (255, 215, 0))
        self.size = GRID_SIZE * 0.8
        self.lifetime = 15.0  # ثواني قبل الاختفاء
        self.time_alive = 0.0
        self.pulse_speed = 5
        
        # خصائص حسب النوع
        self.properties = self.get_properties()
    
    def get_properties(self):
        """الحصول على خصائص الطعام الخاص"""
        properties = {
            'golden': {'points': 50, 'effect': 'extra_points'},
            'speed': {'points': 30, 'effect': 'speed_boost'},
            'slow': {'points': 20, 'effect': 'slow_down'},
            'reverse': {'points': 25, 'effect': 'reverse_controls'},
            'shield': {'points': 40, 'effect': 'shield'},
            'magnet': {'points': 35, 'effect': 'magnet'},
        }
        return properties.get(self.food_type, {'points': 30, 'effect': 'extra_points'})
    
    def update(self, dt):
        """تحديث حالة الطعام الخاص"""
        super().update(dt)
        self.time_alive += dt
        
        # وميض قبل الاختفاء
        if self.lifetime - self.time_alive < 3.0:
            blink_speed = 10 - ((self.lifetime - self.time_alive) * 3)
            self.glow_intensity = (math.sin(pygame.time.get_ticks() * 0.001 * blink_speed) + 1) * 0.5
    
    def is_expired(self):
        """التحقق إذا انتهت مدة الطعام"""
        return self.time_alive >= self.lifetime

class FoodManager:
    """مدير الطعام"""
    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.foods = []
        self.special_foods = []
        self.spawn_timer = 0
        self.spawn_interval = 5.0  # ثواني بين ظهور الطعام الخاص
        
    def update(self, dt, snake_positions):
        """تحديث كل الطعام"""
        # تحديث الطعام العادي
        for food in self.foods:
            food.update(dt)
        
        # تحديث الطعام الخاص
        for food in self.special_foods[:]:
            food.update(dt)
            if food.is_expired():
                self.special_foods.remove(food)
        
        # توليد طعام خاص جديد
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval and len(self.special_foods) < 3:
            self.spawn_special_food(snake_positions)
            self.spawn_timer = 0
    
    def spawn_food(self, snake_positions):
        """توليد طعام عادي"""
        food = Food(self.grid_width, self.grid_height)
        food.respawn(snake_positions)
        self.foods.append(food)
    
    def spawn_special_food(self, snake_positions):
        """توليد طعام خاص"""
        # أنواع الطعام الخاص
        food_types = ['golden', 'speed', 'slow', 'reverse', 'shield', 'magnet']
        weights = [0.3, 0.15, 0.15, 0.1, 0.2, 0.1]  # أوزان الظهور
        
        food_type = random.choices(food_types, weights=weights, k=1)[0]
        food = SpecialFood(self.grid_width, self.grid_height, food_type)
        
        # محاولة إيجاد مكان مناسب
        attempts = 0
        while attempts < 50:
            food.position = food.generate_position()
            
            # التأكد من أنه ليس على الثعبان أو طعام آخر
            valid_position = True
            
            # التحقق من الثعبان
            for pos in snake_positions:
                distance = math.sqrt(
                    (food.position[0] - pos[0])**2 +
                    (food.position[1] - pos[1])**2
                )
                if distance < GRID_SIZE * 2:
                    valid_position = False
                    break
            
            # التحقق من الطعام الآخر
            if valid_position:
                for other_food in self.foods + self.special_foods:
                    distance = math.sqrt(
                        (food.position[0] - other_food.position[0])**2 +
                        (food.position[1] - other_food.position[1])**2
                    )
                    if distance < GRID_SIZE * 2:
                        valid_position = False
                        break
            
            if valid_position:
                self.special_foods.append(food)
                return
            
            attempts += 1
    
    def check_collisions(self, snake_head_pos):
        """التحقق من اصطدام الثعبان بالطعام"""
        eaten_foods = []
        eaten_specials = []
        
        # الطعام العادي
        for food in self.foods[:]:
            if food.check_collision(snake_head_pos):
                eaten_foods.append(food)
                self.foods.remove(food)
        
        # الطعام الخاص
        for food in self.special_foods[:]:
            if food.check_collision(snake_head_pos):
                eaten_specials.append(food)
                self.special_foods.remove(food)
        
        return eaten_foods, eaten_specials
    
    def get_all_food_positions(self):
        """الحصول على مواقع كل الطعام"""
        positions = []
        for food in self.foods:
            positions.append(food.position)
        for food in self.special_foods:
            positions.append(food.position)
        return positions
    
    def clear(self):
        """مسح كل الطعام"""
        self.foods.clear()
        self.special_foods.clear()