"""
⚡ المكافآت والقدرات الخاصة
"""

import pygame
import random
import math
from config import *

class PowerUp:
    """مكافأة/قدرة خاصة"""
    def __init__(self, x, y, powerup_type='double_points'):
        self.x = x
        self.y = y
        self.powerup_type = powerup_type
        self.color = POWERUP_COLORS.get(powerup_type, (255, 255, 255))
        self.size = GRID_SIZE * 0.6
        self.rotation = 0
        self.float_height = 0
        self.float_speed = random.uniform(2, 4)
        self.float_phase = random.uniform(0, 2 * math.pi)
        self.lifetime = 15.0  # ثواني
        self.time_alive = 0.0
        self.active = True
        self.glow_intensity = 0
        self.pulse_speed = 4
        
    def update(self, dt):
        """تحديث المكافأة"""
        if not self.active:
            return
            
        self.time_alive += dt
        self.rotation += dt * 100  # دوران
        
        # حركة الطفو
        self.float_phase += dt * self.float_speed
        self.float_height = math.sin(self.float_phase) * 5
        
        # وميض
        self.glow_intensity = (math.sin(pygame.time.get_ticks() * 0.001 * self.pulse_speed) + 1) * 0.5
        
        # وميض سريع قبل الاختفاء
        if self.lifetime - self.time_alive < 3.0:
            blink_speed = 15 - ((self.lifetime - self.time_alive) * 5)
            self.glow_intensity = (math.sin(pygame.time.get_ticks() * 0.001 * blink_speed) + 1) * 0.5
    
    def is_expired(self):
        """التحقق إذا انتهت المدة"""
        return self.time_alive >= self.lifetime
    
    def check_collision(self, snake_head_pos):
        """التحقق من اصطدام الثعبان بالمكافأة"""
        if not self.active:
            return False
            
        distance = math.sqrt(
            (self.x - snake_head_pos[0])**2 +
            (self.y - snake_head_pos[1])**2
        )
        return distance < GRID_SIZE * 0.8
    
    def get_effect(self):
        """الحصول على تأثير المكافأة"""
        effects = {
            'double_points': {
                'duration': 10.0,
                'description': 'Double points for 10 seconds',
                'multiplier': 2.0
            },
            'invincible': {
                'duration': 8.0,
                'description': 'Invincible for 8 seconds',
                'shield': True
            },
            'teleport': {
                'duration': 0.0,  # فوري
                'description': 'Teleport to random location',
                'instant': True
            },
            'ghost': {
                'duration': 12.0,
                'description': 'Can pass through walls for 12 seconds',
                'ghost': True
            },
            'bomb': {
                'duration': 0.0,  # فوري
                'description': 'Destroy nearby obstacles',
                'instant': True,
                'radius': GRID_SIZE * 3
            }
        }
        return effects.get(self.powerup_type, {})
    
    def draw(self, screen, camera):
        """رسم المكافأة"""
        if not self.active:
            return
            
        screen_x, screen_y = camera.world_to_screen(self.x, self.y + self.float_height)
        powerup_size = self.size * camera.zoom
        
        # توهج
        glow_size = powerup_size * (1 + self.glow_intensity * 0.4)
        for i in range(3):
            glow_radius = glow_size * (1 + i * 0.15)
            glow_alpha = int(70 * self.glow_intensity * (1 - i * 0.2))
            glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*self.color, glow_alpha),
                             (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surface, (screen_x - glow_radius, screen_y - glow_radius))
        
        # المكافأة الرئيسية
        rotated_surface = pygame.transform.rotate(
            pygame.Surface((powerup_size, powerup_size), pygame.SRCALPHA),
            self.rotation
        )
        
        # إنشاء الشكل حسب نوع المكافأة
        shape_surface = pygame.Surface((powerup_size, powerup_size), pygame.SRCALPHA)
        
        if self.powerup_type == 'double_points':
            # نجمة مزدوجة
            self.draw_star(shape_surface, powerup_size//2, powerup_size//2, powerup_size*0.4)
            self.draw_star(shape_surface, powerup_size//2, powerup_size//2, powerup_size*0.2)
            
        elif self.powerup_type == 'invincible':
            # درع
            pygame.draw.circle(shape_surface, self.color,
                             (powerup_size//2, powerup_size//2), powerup_size//2)
            pygame.draw.circle(shape_surface, (255, 255, 255),
                             (powerup_size//2, powerup_size//2), powerup_size//3)
            
        elif self.powerup_type == 'teleport':
            # دوامة
            for i in range(8):
                angle = math.radians(i * 45 + self.rotation)
                radius = powerup_size * 0.3 * (i / 8)
                x = powerup_size//2 + math.cos(angle) * radius
                y = powerup_size//2 + math.sin(angle) * radius
                pygame.draw.circle(shape_surface, self.color,
                                 (int(x), int(y)), int(powerup_size * 0.1))
            
        elif self.powerup_type == 'ghost':
            # شبح
            pygame.draw.circle(shape_surface, self.color,
                             (powerup_size//2, powerup_size//4), powerup_size//4)
            pygame.draw.polygon(shape_surface, self.color, [
                (powerup_size//4, powerup_size//4),
                (3*powerup_size//4, powerup_size//4),
                (3*powerup_size//4, 3*powerup_size//4),
                (powerup_size//4, 3*powerup_size//4)
            ])
            
        elif self.powerup_type == 'bomb':
            # قنبلة
            pygame.draw.circle(shape_surface, self.color,
                             (powerup_size//2, powerup_size//2), powerup_size//2)
            pygame.draw.rect(shape_surface, (255, 0, 0),
                           (powerup_size//2 - 2, powerup_size//4, 4, powerup_size//4))
            
        else:
            # دائرة افتراضية
            pygame.draw.circle(shape_surface, self.color,
                             (powerup_size//2, powerup_size//2), powerup_size//2)
        
        # تدوير ووضع الشكل
        rotated_shape = pygame.transform.rotate(shape_surface, self.rotation)
        shape_rect = rotated_shape.get_rect(center=(int(screen_x), int(screen_y)))
        screen.blit(rotated_shape, shape_rect)
    
    def draw_star(self, surface, x, y, size):
        """رسم نجمة على سطح"""
        points = []
        for i in range(10):
            angle = math.radians(i * 36)
            radius = size if i % 2 == 0 else size * 0.4
            points.append((
                x + math.cos(angle) * radius,
                y + math.sin(angle) * radius
            ))
        pygame.draw.polygon(surface, self.color, points)

class PowerUpManager:
    """مدير المكافآت"""
    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.powerups = []
        self.spawn_timer = 0
        self.spawn_interval = 20.0  # ثواني بين ظهور المكافآت
        self.active_effects = {}
        
    def update(self, dt, snake_positions):
        """تحديث المكافآت"""
        # تحديث المكافآت الحالية
        for powerup in self.powerups[:]:
            powerup.update(dt)
            if powerup.is_expired():
                self.powerups.remove(powerup)
        
        # توليد مكافآت جديدة
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval and len(self.powerups) < 2:
            self.spawn_powerup(snake_positions)
            self.spawn_timer = 0
        
        # تحديث المؤقتات النشطة
        for effect in list(self.active_effects.keys()):
            self.active_effects[effect]['timer'] -= dt
            if self.active_effects[effect]['timer'] <= 0:
                del self.active_effects[effect]
    
    def spawn_powerup(self, snake_positions):
        """توليد مكافأة جديدة"""
        powerup_types = ['double_points', 'invincible', 'teleport', 'ghost', 'bomb']
        weights = [0.3, 0.25, 0.15, 0.2, 0.1]  # أوزان الظهور
        
        powerup_type = random.choices(powerup_types, weights=weights, k=1)[0]
        
        # محاولة إيجاد مكان مناسب
        attempts = 0
        while attempts < 50:
            x = random.randint(1, self.grid_width - 2) * GRID_SIZE + GRID_SIZE // 2
            y = random.randint(1, self.grid_height - 2) * GRID_SIZE + GRID_SIZE // 2
            
            # التأكد من أن الموقع ليس على الثعبان أو قريب منه
            valid_position = True
            for pos in snake_positions:
                distance = math.sqrt((x - pos[0])**2 + (y - pos[1])**2)
                if distance < GRID_SIZE * 3:
                    valid_position = False
                    break
            
            if valid_position:
                powerup = PowerUp(x, y, powerup_type)
                self.powerups.append(powerup)
                return
            
            attempts += 1
    
    def check_collisions(self, snake_head_pos):
        """التحقق من اصطدام الثعبان بالمكافآت"""
        collected = []
        
        for powerup in self.powerups[:]:
            if powerup.check_collision(snake_head_pos):
                collected.append(powerup)
                self.powerups.remove(powerup)
                
                # تسجيل التأثير النشط
                effect = powerup.get_effect()
                if effect:
                    self.active_effects[powerup.powerup_type] = {
                        'timer': effect.get('duration', 0),
                        'effect': effect
                    }
        
        return collected
    
    def get_active_effect(self, effect_type):
        """الحصول على تأثير نشط"""
        return self.active_effects.get(effect_type)
    
    def has_active_effect(self, effect_type):
        """التحقق إذا هناك تأثير نشط"""
        return effect_type in self.active_effects
    
    def get_powerup_positions(self):
        """الحصول على مواقع المكافآت"""
        return [(p.x, p.y) for p in self.powerups]
    
    def draw(self, screen, camera):
        """رسم المكافآت"""
        for powerup in self.powerups:
            powerup.draw(screen, camera)
    
    def clear(self):
        """مسح المكافآت"""
        self.powerups.clear()
        self.active_effects.clear()