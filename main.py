#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🐍 لعبة الثعبان المتطورة
🎮 Snake Game Pro - Advanced Version
"""

import pygame
import sys
import os
import random
from config import *
from ui import Menu

class SnakeGame:
    """اللعبة الرئيسية"""
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game Pro 🐍")
        
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.fps = FPS
        
        self.game_state = "menu"
        self.running = True
        
        self.menu = Menu(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # إعدادات لعبة الثعبان
        self.grid_size = 20
        self.grid_width = WINDOW_WIDTH // self.grid_size
        self.grid_height = WINDOW_HEIGHT // self.grid_size
        
        self.reset_game()
        
        print("=" * 50)
        print("🎮 Snake Game Pro - Started Successfully!")
        print("=" * 50)
    
    def reset_game(self):
        """إعادة تعيين لعبة الثعبان"""
        # الثعبان
        self.snake = [(self.grid_width // 2, self.grid_height // 2)]
        self.snake_direction = (1, 0)  # يمين
        self.next_direction = (1, 0)
        
        # الطعام
        self.food = self.generate_food()
        
        # النقاط
        self.score = 0
        self.high_score = 0
        
        # السرعة
        self.snake_speed = 10  # إطار في الثانية
        self.speed_timer = 0
        
        # حالة اللعبة
        self.game_over = False
        
        # الألوان
        self.snake_color = SNAKE_HEAD_COLOR
        self.food_color = FOOD_COLOR
    
    def generate_food(self):
        """توليد طعام في مكان عشوائي"""
        while True:
            food = (random.randint(0, self.grid_width - 1), 
                   random.randint(0, self.grid_height - 1))
            if food not in self.snake:
                return food
    
    def handle_events(self):
        """معالجة الأحداث"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == "playing":
                        self.game_state = "menu"
                    elif self.game_state == "menu" and self.game_over:
                        self.reset_game()
                        self.game_state = "menu"
                elif event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_F1:
                    self.take_screenshot()
                
                # تحكم في الثعبان
                if self.game_state == "playing" and not self.game_over:
                    if event.key == pygame.K_UP and self.snake_direction != (0, 1):
                        self.next_direction = (0, -1)
                    elif event.key == pygame.K_DOWN and self.snake_direction != (0, -1):
                        self.next_direction = (0, 1)
                    elif event.key == pygame.K_LEFT and self.snake_direction != (1, 0):
                        self.next_direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and self.snake_direction != (-1, 0):
                        self.next_direction = (1, 0)
                    elif event.key == pygame.K_SPACE:
                        self.reset_game()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True
        
        return mouse_pos, mouse_clicked
    
    def update_snake(self):
        """تحديث حالة الثعبان"""
        if self.game_over:
            return
        
        # تحديث السرعة
        self.speed_timer += self.dt
        
        if self.speed_timer >= 1.0 / self.snake_speed:
            self.speed_timer = 0
            
            # تحديث الاتجاه
            self.snake_direction = self.next_direction
            
            # حساب الموقع الجديد للرأس
            head_x, head_y = self.snake[0]
            new_x = head_x + self.snake_direction[0]
            new_y = head_y + self.snake_direction[1]
            
            # التحقق من الاصطدام بالجدران
            if (new_x < 0 or new_x >= self.grid_width or 
                new_y < 0 or new_y >= self.grid_height):
                self.game_over = True
                return
            
            # التحقق من الاصطدام بالنفس
            new_head = (new_x, new_y)
            if new_head in self.snake:
                self.game_over = True
                return
            
            # إضافة الرأس الجديد
            self.snake.insert(0, new_head)
            
            # التحقق من أكل الطعام
            if new_head == self.food:
                self.score += 10
                if self.score > self.high_score:
                    self.high_score = self.score
                self.food = self.generate_food()
                
                # زيادة السرعة كل 50 نقطة
                if self.score % 50 == 0 and self.snake_speed < 20:
                    self.snake_speed += 1
            else:
                # إزالة الذيل إذا لم يؤكل طعام
                self.snake.pop()
    
    def update(self):
        """تحديث اللعبة"""
        if self.game_state == "playing":
            self.update_snake()
    
    def draw_snake(self):
        """رسم الثعبان والطعام"""
        # رسم الطعام
        food_x, food_y = self.food
        pygame.draw.rect(self.screen, self.food_color,
                        (food_x * self.grid_size, food_y * self.grid_size,
                         self.grid_size - 2, self.grid_size - 2),
                        border_radius=5)
        
        # رسم الثعبان
        for i, (x, y) in enumerate(self.snake):
            color = self.snake_color if i == 0 else SNAKE_BODY_COLOR
            
            # الرأس
            if i == 0:
                pygame.draw.rect(self.screen, color,
                                (x * self.grid_size, y * self.grid_size,
                                 self.grid_size - 2, self.grid_size - 2),
                                border_radius=7)
                
                # العيون
                eye_size = 3
                if self.snake_direction == (1, 0):  # يمين
                    pygame.draw.circle(self.screen, SNAKE_EYE_COLOR,
                                     (x * self.grid_size + self.grid_size - 6,
                                      y * self.grid_size + 6), eye_size)
                    pygame.draw.circle(self.screen, SNAKE_EYE_COLOR,
                                     (x * self.grid_size + self.grid_size - 6,
                                      y * self.grid_size + self.grid_size - 6), eye_size)
                elif self.snake_direction == (-1, 0):  # يسار
                    pygame.draw.circle(self.screen, SNAKE_EYE_COLOR,
                                     (x * self.grid_size + 6,
                                      y * self.grid_size + 6), eye_size)
                    pygame.draw.circle(self.screen, SNAKE_EYE_COLOR,
                                     (x * self.grid_size + 6,
                                      y * self.grid_size + self.grid_size - 6), eye_size)
                elif self.snake_direction == (0, -1):  # أعلى
                    pygame.draw.circle(self.screen, SNAKE_EYE_COLOR,
                                     (x * self.grid_size + 6,
                                      y * self.grid_size + 6), eye_size)
                    pygame.draw.circle(self.screen, SNAKE_EYE_COLOR,
                                     (x * self.grid_size + self.grid_size - 6,
                                      y * self.grid_size + 6), eye_size)
                elif self.snake_direction == (0, 1):  # أسفل
                    pygame.draw.circle(self.screen, SNAKE_EYE_COLOR,
                                     (x * self.grid_size + 6,
                                      y * self.grid_size + self.grid_size - 6), eye_size)
                    pygame.draw.circle(self.screen, SNAKE_EYE_COLOR,
                                     (x * self.grid_size + self.grid_size - 6,
                                      y * self.grid_size + self.grid_size - 6), eye_size)
            else:
                # الجسم
                pygame.draw.rect(self.screen, color,
                                (x * self.grid_size, y * self.grid_size,
                                 self.grid_size - 2, self.grid_size - 2),
                                border_radius=5)
    
    def draw(self):
        """رسم اللعبة"""
        keys = pygame.key.get_pressed()
        
        if self.game_state == "menu":
            self.screen.fill(BACKGROUND_COLOR)
            mouse_pos, mouse_clicked = self.handle_events()
            
            result = self.menu.update(mouse_pos, mouse_clicked, keys, self.dt)
            if result == "playing":
                self.reset_game()
                self.game_state = "playing"
            elif result == "exit":
                self.running = False
            
            self.menu.draw(self.screen)
            
        elif self.game_state == "playing":
            # رسم خلفية الشبكة
            self.screen.fill(BACKGROUND_COLOR)
            
            # رسم الشبكة
            for x in range(0, WINDOW_WIDTH, self.grid_size):
                pygame.draw.line(self.screen, GRID_LINE_COLOR, 
                               (x, 0), (x, WINDOW_HEIGHT), 1)
            for y in range(0, WINDOW_HEIGHT, self.grid_size):
                pygame.draw.line(self.screen, GRID_LINE_COLOR, 
                               (0, y), (WINDOW_WIDTH, y), 1)
            
            # رسم الثعبان والطعام
            self.draw_snake()
            
            # معالجة الأحداث
            self.handle_events()
            
            # عرض النقاط
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Score: {self.score}", True, UI_TEXT_COLOR)
            high_score_text = font.render(f"High Score: {self.high_score}", True, UI_TEXT_COLOR)
            speed_text = font.render(f"Speed: {self.snake_speed}", True, UI_TEXT_COLOR)
            
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(high_score_text, (10, 50))
            self.screen.blit(speed_text, (10, 90))
            
            # تعليمات التحكم
            controls_font = pygame.font.Font(None, 24)
            controls = [
                "Use ARROW KEYS to move",
                "Press SPACE to restart",
                "Press ESC to return to menu"
            ]
            
            for i, text in enumerate(controls):
                control_text = controls_font.render(text, True, (150, 150, 150))
                self.screen.blit(control_text, 
                               (WINDOW_WIDTH - control_text.get_width() - 10, 
                                10 + i * 30))
            
            # عرض حالة game over
            if self.game_over:
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                self.screen.blit(overlay, (0, 0))
                
                game_over_font = pygame.font.Font(None, 72)
                game_over_text = game_over_font.render("GAME OVER", True, (255, 50, 50))
                self.screen.blit(game_over_text, 
                               (WINDOW_WIDTH//2 - game_over_text.get_width()//2,
                                WINDOW_HEIGHT//2 - 100))
                
                final_score_font = pygame.font.Font(None, 48)
                final_score_text = final_score_font.render(f"Final Score: {self.score}", True, UI_TEXT_COLOR)
                self.screen.blit(final_score_text,
                               (WINDOW_WIDTH//2 - final_score_text.get_width()//2,
                                WINDOW_HEIGHT//2))
                
                restart_font = pygame.font.Font(None, 32)
                restart_text = restart_font.render("Press SPACE to restart or ESC for menu", True, (200, 200, 200))
                self.screen.blit(restart_text,
                               (WINDOW_WIDTH//2 - restart_text.get_width()//2,
                                WINDOW_HEIGHT//2 + 80))
        
        # عرض الـ FPS
        fps_text = f"FPS: {int(self.clock.get_fps())}"
        font = pygame.font.Font(None, 24)
        fps_surface = font.render(fps_text, True, (200, 200, 200))
        self.screen.blit(fps_surface, (WINDOW_WIDTH - fps_surface.get_width() - 10, 
                                      WINDOW_HEIGHT - 30))
        
        pygame.display.flip()
    
    def take_screenshot(self):
        """أخذ لقطة شاشة"""
        try:
            screenshots_dir = "screenshots"
            os.makedirs(screenshots_dir, exist_ok=True)
            
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(screenshots_dir, f"screenshot_{timestamp}.png")
            
            pygame.image.save(self.screen, filename)
            print(f"📸 Screenshot saved: {filename}")
        except Exception as e:
            print(f"❌ Failed to save screenshot: {e}")
    
    def run(self):
        """تشغيل اللعبة الرئيسي"""
        while self.running:
            self.dt = self.clock.tick(self.fps) / 1000.0
            self.update()
            self.draw()
        
        pygame.quit()
        sys.exit()

def main():
    """الدالة الرئيسية"""
    try:
        print("🎮 Snake Game Pro - Starting...")
        game = SnakeGame()
        game.run()
    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()