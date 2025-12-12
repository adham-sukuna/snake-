"""
🎛️ واجهة المستخدم - الأزرار، القوائم، النوافذ
"""

import pygame
import math
from config import *

class Button:
    """زر قابل للنقر"""
    def __init__(self, x, y, width, height, text, callback=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.state = 'normal'  # normal, hover, clicked
        self.color = BUTTON_NORMAL
        self.hover_color = BUTTON_HOVER
        self.click_color = BUTTON_CLICK
        self.text_color = BUTTON_TEXT
        self.border_radius = 10
        
        # تحميل الخطوط داخل الفئة
        try:
            self.font = pygame.font.Font(None, MENU_FONT_SIZE)
            self.small_font = pygame.font.Font(None, SMALL_FONT_SIZE)
        except:
            self.font = pygame.font.SysFont('arial', MENU_FONT_SIZE, bold=True)
            self.small_font = pygame.font.SysFont('arial', SMALL_FONT_SIZE)
        
        self.pulse_phase = 0
        self.enabled = True
        self.was_clicked = False
        
    def update(self, mouse_pos, mouse_clicked):
        """تحديث حالة الزر"""
        if not self.enabled:
            self.state = 'normal'
            return None
            
        if self.rect.collidepoint(mouse_pos):
            if mouse_clicked and not self.was_clicked:
                self.state = 'clicked'
                self.was_clicked = True
                if self.callback:
                    return self.callback()
            elif not mouse_clicked:
                self.state = 'hover'
                self.was_clicked = False
            else:
                self.state = 'clicked'
        else:
            self.state = 'normal'
            self.was_clicked = False
        
        self.pulse_phase += 0.05
        return None
    
    def draw(self, screen):
        """رسم الزر"""
        if self.state == 'normal':
            color = self.color
            glow = 0
        elif self.state == 'hover':
            color = self.hover_color
            glow = 20
        else:
            color = self.click_color
            glow = 10
        
        if glow > 0:
            glow_rect = pygame.Rect(
                self.rect.x - 5,
                self.rect.y - 5,
                self.rect.width + 10,
                self.rect.height + 10
            )
            glow_surface = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*color[:3], 30), 
                           glow_surface.get_rect(), 
                           border_radius=self.border_radius + 5)
            screen.blit(glow_surface, glow_rect)
        
        pygame.draw.rect(screen, color, self.rect, border_radius=self.border_radius)
        
        border_color = tuple(min(c + 40, 255) for c in color)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=self.border_radius)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
        if self.state == 'hover':
            pulse = (math.sin(self.pulse_phase) + 1) * 0.5
            pulse_size = int(2 * pulse)
            pygame.draw.rect(screen, UI_ACCENT_COLOR, text_rect.inflate(pulse_size, pulse_size), 
                           1, border_radius=5)

class Menu:
    """القائمة الرئيسية"""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.buttons = []
        self.title = "Snake Game Pro"
        self.subtitle = "Eat, Grow, Survive!"
        self.background_phase = 0
        self.selected_button = 0
        self.key_delay = 0  # تأخير المفاتيح
        self.enter_pressed = False
        
        try:
            self.title_font = pygame.font.Font(None, TITLE_FONT_SIZE)
            self.menu_font = pygame.font.Font(None, MENU_FONT_SIZE)
            self.score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
            self.small_font = pygame.font.Font(None, SMALL_FONT_SIZE)
        except:
            self.title_font = pygame.font.SysFont('arial', TITLE_FONT_SIZE, bold=True)
            self.menu_font = pygame.font.SysFont('arial', MENU_FONT_SIZE, bold=True)
            self.score_font = pygame.font.SysFont('arial', SCORE_FONT_SIZE)
            self.small_font = pygame.font.SysFont('arial', SMALL_FONT_SIZE)
        
        self.create_buttons()
    
    def create_buttons(self):
        """إنشاء أزرار القائمة"""
        button_width = 300
        button_height = 60
        start_y = 250
        spacing = 80
        
        buttons_data = [
            ("🎮 Start Game", self.start_game),
            ("⚙️ Settings", self.open_settings),
            ("🏆 High Scores", self.show_high_scores),
            ("❓ How to Play", self.show_instructions),
            ("❌ Exit", self.exit_game),
        ]
        
        for i, (text, callback) in enumerate(buttons_data):
            x = self.screen_width // 2 - button_width // 2
            y = start_y + i * spacing
            button = Button(x, y, button_width, button_height, text, callback)
            self.buttons.append(button)
    
    def update(self, mouse_pos, mouse_clicked, keys, dt):
        """تحديث القائمة"""
        # تقليل تأخير المفاتيح
        if self.key_delay > 0:
            self.key_delay -= dt * 1000
        
        # التنقل بالمفاتيح
        if self.key_delay <= 0:
            if keys[pygame.K_UP]:
                self.selected_button = (self.selected_button - 1) % len(self.buttons)
                self.key_delay = 200  # 200ms تأخير
            elif keys[pygame.K_DOWN]:
                self.selected_button = (self.selected_button + 1) % len(self.buttons)
                self.key_delay = 200
        
        # معالجة Enter
        if keys[pygame.K_RETURN] and not self.enter_pressed:
            self.enter_pressed = True
            result = self.buttons[self.selected_button].callback()
            if result:
                return result
        elif not keys[pygame.K_RETURN]:
            self.enter_pressed = False
        
        # تحديث الأزرار
        for i, button in enumerate(self.buttons):
            if i == self.selected_button:
                fake_mouse_pos = button.rect.center
                result = button.update(fake_mouse_pos, False)
                if result:
                    return result
            else:
                button.update(mouse_pos, mouse_clicked)
        
        self.background_phase += dt
        
        return None
    
    def draw(self, screen):
        """رسم القائمة"""
        self.draw_animated_background(screen)
        
        title_text = self.title_font.render(self.title, True, UI_ACCENT_COLOR)
        subtitle_text = self.score_font.render(self.subtitle, True, UI_TEXT_COLOR)
        
        glow = abs(math.sin(self.background_phase * 2)) * 20 + 5
        glow_surface = pygame.Surface((title_text.get_width() + 20, title_text.get_height() + 20), 
                                     pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*UI_ACCENT_COLOR, 30), 
                        glow_surface.get_rect(), border_radius=15)
        screen.blit(glow_surface, 
                   (self.screen_width//2 - title_text.get_width()//2 - 10, 
                    80))
        
        screen.blit(title_text, 
                   (self.screen_width//2 - title_text.get_width()//2, 
                    90))
        screen.blit(subtitle_text, 
                   (self.screen_width//2 - subtitle_text.get_width()//2, 
                    170))
        
        for button in self.buttons:
            button.draw(screen)
        
        # رسم مؤشر السهم
        selected_button = self.buttons[self.selected_button]
        arrow_size = 15
        arrow_x = selected_button.rect.left - arrow_size - 10
        arrow_y = selected_button.rect.centery
        
        pygame.draw.polygon(screen, UI_ACCENT_COLOR, [
            (arrow_x, arrow_y - arrow_size),
            (arrow_x + arrow_size, arrow_y),
            (arrow_x, arrow_y + arrow_size)
        ])
        
        controls_text = self.small_font.render(
            "Use ARROW KEYS to navigate, ENTER to select", 
            True, (150, 150, 150)
        )
        screen.blit(controls_text, 
                   (self.screen_width//2 - controls_text.get_width()//2, 
                    self.screen_height - 50))
    
    def draw_animated_background(self, screen):
        """رسم خلفية متحركة"""
        for i in range(0, self.screen_width, 50):
            for j in range(0, self.screen_height, 50):
                x = i + math.sin(self.background_phase + i * 0.01 + j * 0.005) * 10
                y = j + math.cos(self.background_phase + i * 0.005 + j * 0.01) * 10
                
                color_value = 30 + abs(math.sin(self.background_phase + i * 0.02)) * 20
                color = (color_value, color_value + 10, color_value + 20)
                
                pygame.draw.rect(screen, color, (x, y, 48, 48), border_radius=5)
    
    def start_game(self):
        return "playing"
    
    def open_settings(self):
        return "settings"
    
    def show_high_scores(self):
        print("Showing high scores...")
        return "high_scores"
    
    def show_instructions(self):
        print("Showing instructions...")
        return "instructions"
    
    def exit_game(self):
        return "exit"