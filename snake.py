"""
🐍 منطق الثعبان الأساسي
"""

import pygame
import math
from config import *

class SnakeSegment:
    """جزء من جسم الثعبان"""
    def __init__(self, x, y, is_head=False):
        self.x = x
        self.y = y
        self.is_head = is_head
        self.direction = (1, 0)  # الاتجاه الافتراضي
        self.next_direction = (1, 0)
        self.color = SNAKE_HEAD_COLOR if is_head else SNAKE_BODY_COLOR
        self.size = GRID_SIZE
        self.glow_intensity = 0
        
    def update(self, direction=None):
        """تحديث موقع القطعة"""
        if direction and self.is_head:
            self.next_direction = direction
        
        # تحديث الاتجاه
        self.direction = (
            self.direction[0] + (self.next_direction[0] - self.direction[0]) * SNAKE_TURN_SPEED,
            self.direction[1] + (self.next_direction[1] - self.direction[1]) * SNAKE_TURN_SPEED
        )
        
        # تطبيع الاتجاه
        length = math.sqrt(self.direction[0]**2 + self.direction[1]**2)
        if length > 0:
            self.direction = (self.direction[0]/length, self.direction[1]/length)
    
    def get_next_position(self):
        """الحصول على الموقع التالي"""
        return (
            self.x + self.direction[0] * GRID_SIZE,
            self.y + self.direction[1] * GRID_SIZE
        )

class Snake:
    """الفئة الرئيسية للثعبان"""
    def __init__(self, start_x, start_y):
        # إنشاء الرأس والجسم
        self.head = SnakeSegment(start_x, start_y, is_head=True)
        self.body = []
        self.growth_pending = 3  # طول ابتدائي
        self.direction = (1, 0)  # يمين
        self.next_direction = (1, 0)
        
        # الحالة
        self.alive = True
        self.score = 0
        self.length = 1
        self.speed = INITIAL_SPEED
        self.move_timer = 0
        
        # القدرات الخاصة
        self.powerups = {
            'shield': False,
            'magnet': False,
            'invincible': False,
            'ghost': False,
            'double_points': False,
            'speed_boost': False,
        }
        self.powerup_timers = {}
        
        # الرسوم المتحركة
        self.wobble_phase = 0
        self.glow_phase = 0
        
    def update(self, dt, food_positions=None):
        """تحديث حالة الثعبان"""
        if not self.alive:
            return
        
        # تحديث مؤقتات القدرات
        self.update_powerups(dt)
        
        # تحديث الرأس
        self.head.update(self.next_direction)
        self.direction = self.head.direction
        
        # تحديث مؤتمر الحركة
        self.move_timer += dt * self.speed
        if self.move_timer >= 1.0:
            self.move_timer = 0
            self.move()
        
        # تحديث الجسم
        self.update_body()
        
        # تحديث الرسوم المتحركة
        self.wobble_phase += dt * 5
        self.glow_phase += dt * 3
        
        # تأثير المغناطيس
        if self.powerups['magnet'] and food_positions:
            self.apply_magnet(food_positions)
    
    def move(self):
        """تحريك الثعبان خطوة واحدة"""
        # حفظ الموقع السابق للرأس
        prev_x, prev_y = self.head.x, self.head.y
        
        # تحريك الرأس
        self.head.x += self.direction[0] * GRID_SIZE
        self.head.y += self.direction[1] * GRID_SIZE
        
        # تحريك الجسم
        if self.body:
            # تحريك الجسم كسلسلة
            for i in range(len(self.body)-1, 0, -1):
                self.body[i].x = self.body[i-1].x
                self.body[i].y = self.body[i-1].y
            
            # أول قطعة من الجسم تذهب لموقع الرأس السابق
            self.body[0].x = prev_x
            self.body[0].y = prev_y
        
        # إضافة أجزاء جديدة إذا كان الثعبان ينمو
        if self.growth_pending > 0:
            self.add_segment(prev_x, prev_y)
            self.growth_pending -= 1
    
    def update_body(self):
        """تحديث حركة الجسم"""
        # تحديث اتجاه كل قطعة
        for i, segment in enumerate(self.body):
            if i == 0:
                # أول قطعة تتبع الرأس
                target_dir = (
                    self.head.x - segment.x,
                    self.head.y - segment.y
                )
            else:
                # القطع الأخرى تتبع التي قبلها
                target_dir = (
                    self.body[i-1].x - segment.x,
                    self.body[i-1].y - segment.y
                )
            
            # تطبيع الاتجاه
            length = math.sqrt(target_dir[0]**2 + target_dir[1]**2)
            if length > 0:
                segment.next_direction = (target_dir[0]/length, target_dir[1]/length)
            
            segment.update()
    
    def add_segment(self, x, y):
        """إضافة جزء جديد للجسم"""
        new_segment = SnakeSegment(x, y, is_head=False)
        self.body.append(new_segment)
        self.length += 1
    
    def grow(self, amount=1):
        """جعل الثعبان ينمو"""
        self.growth_pending += amount
    
    def change_direction(self, direction):
        """تغيير اتجاه الثعبان"""
        # منع الدوران المباشر للخلف
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.next_direction = direction
    
    def check_self_collision(self):
        """التحقق من اصطدام الثعبان بنفسه"""
        if not self.powerups['ghost']:
            for segment in self.body:
                if self.distance_to_segment(segment) < GRID_SIZE - COLLISION_MARGIN:
                    return True
        return False
    
    def check_wall_collision(self, grid_width, grid_height):
        """التحقق من اصطدام الثعبان بالجدران"""
        if self.powerups['ghost']:
            return False
            
        head_grid_x = self.head.x // GRID_SIZE
        head_grid_y = self.head.y // GRID_SIZE
        
        return (head_grid_x < 0 or head_grid_x >= grid_width or
                head_grid_y < 0 or head_grid_y >= grid_height)
    
    def distance_to_segment(self, segment):
        """حساب المسافة إلى قطعة"""
        dx = self.head.x - segment.x
        dy = self.head.y - segment.y
        return math.sqrt(dx*dx + dy*dy)
    
    def apply_magnet(self, food_positions):
        """تطبيق تأثير المغناطيس على الطعام القريب"""
        magnet_radius = GRID_SIZE * 5
        
        for food in food_positions:
            dx = self.head.x - food[0]
            dy = self.head.y - food[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < magnet_radius:
                # جذب الطعام نحو الثعبان
                pull_strength = 0.1
                food[0] += (-dx / distance) * pull_strength
                food[1] += (-dy / distance) * pull_strength
    
    def update_powerups(self, dt):
        """تحديث مؤقتات القدرات الخاصة"""
        for powerup in list(self.powerup_timers.keys()):
            self.powerup_timers[powerup] -= dt
            if self.powerup_timers[powerup] <= 0:
                self.remove_powerup(powerup)
    
    def add_powerup(self, powerup_type, duration=10.0):
        """إضافة قدرة خاصة للثعبان"""
        self.powerups[powerup_type] = True
        self.powerup_timers[powerup_type] = duration
        
        # تأثيرات خاصة لكل قدرة
        if powerup_type == 'speed_boost':
            self.speed *= 1.5
        elif powerup_type == 'invincible':
            self.head.color = (255, 255, 255)  # أبيض
    
    def remove_powerup(self, powerup_type):
        """إزالة قدرة خاصة"""
        self.powerups[powerup_type] = False
        
        # إعادة القيم الأصلية
        if powerup_type == 'speed_boost':
            self.speed = INITIAL_SPEED + (self.length // 10) * SPEED_INCREMENT
        elif powerup_type == 'invincible':
            self.head.color = SNAKE_HEAD_COLOR
        
        if powerup_type in self.powerup_timers:
            del self.powerup_timers[powerup_type]
    
    def get_head_position(self):
        """الحصول على موقع الرأس"""
        return (self.head.x, self.head.y)
    
    def get_body_positions(self):
        """الحصول على مواقع الجسم"""
        positions = [(self.head.x, self.head.y)]
        positions.extend([(segment.x, segment.y) for segment in self.body])
        return positions
    
    def die(self):
        """قتل الثعبان"""
        self.alive = False
        # تأثيرات الموت
        self.head.color = (128, 128, 128)  # رمادي
    
    def reset(self, start_x, start_y):
        """إعادة تعيين الثعبان"""
        self.__init__(start_x, start_y)