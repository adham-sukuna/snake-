"""
✨ نظام تأثيرات الجسيمات
"""

import pygame
import random
import math
from config import *

class Particle:
    """جسيم واحد"""
    def __init__(self, x, y, particle_type='spark', color=None, size=5, lifetime=1.0):
        self.x = x
        self.y = y
        self.particle_type = particle_type
        self.color = color or PARTICLE_COLORS.get(particle_type, (255, 255, 255))
        self.size = random.uniform(size * 0.5, size * 1.5)
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.velocity = self.get_initial_velocity()
        self.gravity = 0.1 if particle_type != 'spark' else 0.0
        self.drag = 0.98
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-5, 5)
        self.glow_intensity = 1.0
        
    def get_initial_velocity(self):
        """الحصول على السرعة الابتدائية"""
        if self.particle_type == 'spark':
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            return [
                math.cos(angle) * speed,
                math.sin(angle) * speed
            ]
        elif self.particle_type == 'confetti':
            return [
                random.uniform(-3, 3),
                random.uniform(-5, -2)
            ]
        elif self.particle_type == 'explosion':
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 15)
            return [
                math.cos(angle) * speed,
                math.sin(angle) * speed
            ]
        else:  # default
            return [random.uniform(-1, 1), random.uniform(-1, 1)]
    
    def update(self, dt):
        """تحديث الجسيم"""
        # تحديث الموقع
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        
        # تطبيق الجاذبية
        self.velocity[1] += self.gravity
        
        # تطبيق مقاومة الهواء
        self.velocity[0] *= self.drag
        self.velocity[1] *= self.drag
        
        # تحديث الدوران
        self.rotation += self.rotation_speed
        
        # تحديث العمر
        self.lifetime -= dt
        
        # تحديث شدة التوهج
        life_ratio = self.lifetime / self.max_lifetime
        self.glow_intensity = life_ratio * 0.5 + 0.5  # من 0.5 إلى 1.0
    
    def is_alive(self):
        """التحقق إذا الجسيم لا يزال حياً"""
        return self.lifetime > 0
    
    def draw(self, screen):
        """رسم الجسيم"""
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        
        if self.particle_type == 'spark':
            # شرارة متوهجة
            glow_size = self.size * 3 * self.glow_intensity
            glow_surface = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
            glow_color = (*self.color, int(150 * self.glow_intensity))
            pygame.draw.circle(glow_surface, glow_color, 
                             (int(glow_size), int(glow_size)), int(glow_size))
            screen.blit(glow_surface, (self.x - glow_size, self.y - glow_size))
            
            # مركز الشرارة
            pygame.draw.circle(screen, self.color, 
                             (int(self.x), int(self.y)), int(self.size))
            
        elif self.particle_type == 'confetti':
            # قطع كونفيتي
            points = []
            for i in range(4):
                angle = self.rotation + i * 90
                radius = self.size
                points.append((
                    self.x + math.cos(math.radians(angle)) * radius,
                    self.y + math.sin(math.radians(angle)) * radius
                ))
            pygame.draw.polygon(screen, self.color, points)
            
        elif self.particle_type == 'explosion':
            # دائرة متوسعة
            radius = self.size * (1 - self.lifetime/self.max_lifetime) * 3
            pygame.draw.circle(screen, (*self.color, alpha), 
                             (int(self.x), int(self.y)), int(radius), 2)
            
            # مركز الانفجار
            center_radius = self.size * 0.5
            pygame.draw.circle(screen, self.color, 
                             (int(self.x), int(self.y)), int(center_radius))

class ParticleSystem:
    """نظام إدارة الجسيمات"""
    def __init__(self):
        self.particles = []
        self.emitters = []
    
    def update(self, dt):
        """تحديث كل الجسيمات"""
        # تحديث الجسيمات
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.is_alive():
                self.particles.remove(particle)
        
        # تحديث الباعثات
        for emitter in self.emitters[:]:
            emitter['timer'] -= dt
            if emitter['timer'] <= 0:
                self.emit_from_emitter(emitter)
                emitter['timer'] = emitter['interval']
                
                # إزالة الباعثات المنتهية
                emitter['duration'] -= dt
                if emitter['duration'] <= 0:
                    self.emitters.remove(emitter)
    
    def add_particle(self, particle):
        """إضافة جسيم جديد"""
        self.particles.append(particle)
    
    def create_emitter(self, x, y, particle_type, color=None, count=10, 
                      interval=0.1, duration=1.0):
        """إنشاء باعث جسيمات"""
        emitter = {
            'x': x,
            'y': y,
            'particle_type': particle_type,
            'color': color,
            'count': count,
            'interval': interval,
            'timer': interval,
            'duration': duration
        }
        self.emitters.append(emitter)
    
    def emit_from_emitter(self, emitter):
        """إصدار جسيمات من باعث"""
        for _ in range(emitter['count']):
            particle = Particle(
                emitter['x'],
                emitter['y'],
                emitter['particle_type'],
                emitter['color']
            )
            self.add_particle(particle)
    
    def create_food_particles(self, x, y, food_type='normal'):
        """إنشاء جسيمات للطعام"""
        color = FOOD_COLOR if food_type == 'normal' else SPECIAL_FOOD_COLORS.get(food_type, (255, 215, 0))
        
        for _ in range(15):
            particle = Particle(x, y, 'spark', color, size=3, lifetime=0.5)
            self.add_particle(particle)
    
    def create_snake_particles(self, x, y, count=5):
        """إنشاء جسيمات للثعبان"""
        for _ in range(count):
            particle = Particle(x, y, 'spark', SNAKE_HEAD_COLOR, size=2, lifetime=0.3)
            self.add_particle(particle)
    
    def create_explosion(self, x, y, color=(255, 100, 100)):
        """إنشاء انفجار"""
        # انفجار مركزي
        for _ in range(20):
            particle = Particle(x, y, 'explosion', color, size=5, lifetime=1.0)
            self.add_particle(particle)
        
        # شرارات
        for _ in range(30):
            particle = Particle(x, y, 'spark', color, size=3, lifetime=0.8)
            self.add_particle(particle)
    
    def create_level_up_effect(self, x, y):
        """إنشاء تأثير التقدم للمستوى"""
        # كونفيتي
        for _ in range(50):
            color = random.choice(list(PARTICLE_COLORS.values()))
            particle = Particle(x, y, 'confetti', color, size=4, lifetime=2.0)
            self.add_particle(particle)
        
        # دائرة متوسعة
        emitter = {
            'x': x,
            'y': y,
            'particle_type': 'spark',
            'color': (255, 215, 0),
            'count': 5,
            'interval': 0.05,
            'timer': 0,
            'duration': 0.5
        }
        self.emitters.append(emitter)
    
    def draw(self, screen):
        """رسم كل الجسيمات"""
        for particle in self.particles:
            particle.draw(screen)
    
    def clear(self):
        """مسح كل الجسيمات"""
        self.particles.clear()
        self.emitters.clear()