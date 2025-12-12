"""
🏆 نظام النقاط، المستويات، والتقدم
"""

import json
import os
from datetime import datetime
from config import *

class ScoreManager:
    """مدير النقاط والمستويات"""
    def __init__(self):
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.combo = 0
        self.max_combo = 0
        self.foods_eaten = 0
        self.special_foods_eaten = 0
        self.start_time = None
        self.play_time = 0
        self.multiplier = 1.0
        self.load_high_score()
    
    def start_game(self):
        """بدء لعبة جديدة"""
        self.score = 0
        self.level = 1
        self.combo = 0
        self.foods_eaten = 0
        self.special_foods_eaten = 0
        self.start_time = datetime.now()
        self.play_time = 0
        self.multiplier = 1.0
    
    def update(self, dt):
        """تحديث الوقت"""
        self.play_time += dt
    
    def add_food_score(self, food_type='normal'):
        """إضافة نقاط للطعام المأكول"""
        base_score = SCORE_PER_FOOD
        
        if food_type == 'golden':
            base_score = 50
        elif food_type in ['speed', 'shield', 'magnet']:
            base_score = 30
        elif food_type in ['slow', 'reverse']:
            base_score = 20
        
        # مضاعف النقاط
        actual_score = int(base_score * self.multiplier)
        
        # إضافة النقاط
        self.score += actual_score
        
        # تحديث الإحصائيات
        if food_type == 'normal':
            self.foods_eaten += 1
        else:
            self.special_foods_eaten += 1
        
        # زيادة الكومبو
        self.combo += 1
        if self.combo > self.max_combo:
            self.max_combo = self.combo
        
        # مكافأة الكومبو
        if self.combo >= 5:
            combo_bonus = (self.combo // 5) * 10
            self.score += combo_bonus
        
        # تحديث المستوى
        self.update_level()
        
        # تحديث أعلى نقاط
        if self.score > self.high_score:
            self.high_score = self.score
        
        return actual_score
    
    def update_level(self):
        """تحديث المستوى"""
        old_level = self.level
        
        # كل 10 أطعمة تزيد مستوى
        total_foods = self.foods_eaten + self.special_foods_eaten
        self.level = 1 + (total_foods // 10)
        
        # مكافأة مستوى جديد
        if self.level > old_level:
            level_bonus = (self.level - 1) * SCORE_LEVEL_BONUS
            self.score += level_bonus
    
    def break_combo(self):
        """كسر سلسلة الكومبو"""
        self.combo = 0
    
    def set_multiplier(self, multiplier, duration=None):
        """ضبط مضاعف النقاط"""
        self.multiplier = multiplier
    
    def get_game_stats(self):
        """الحصول على إحصائيات اللعبة"""
        stats = {
            'score': self.score,
            'high_score': self.high_score,
            'level': self.level,
            'combo': self.combo,
            'max_combo': self.max_combo,
            'foods_eaten': self.foods_eaten,
            'special_foods_eaten': self.special_foods_eaten,
            'play_time': int(self.play_time),
            'multiplier': self.multiplier,
        }
        return stats
    
    def save_high_score(self, player_name="Player"):
        """حفظ أعلى نقاط"""
        if self.score > 0:
            scores = self.load_all_scores()
            
            new_score = {
                'player': player_name,
                'score': self.score,
                'level': self.level,
                'foods_eaten': self.foods_eaten,
                'play_time': int(self.play_time),
                'date': datetime.now().isoformat()
            }
            
            scores.append(new_score)
            
            # ترتيب النقاط تنازلياً
            scores.sort(key=lambda x: x['score'], reverse=True)
            
            # حفظ أول 10 نتائج فقط
            scores = scores[:10]
            
            # حفظ في الملف
            os.makedirs(SAVE_DIR, exist_ok=True)
            with open(os.path.join(SAVE_DIR, "high_scores.json"), 'w') as f:
                json.dump(scores, f, indent=2)
    
    def load_high_score(self):
        """تحميل أعلى نقاط"""
        scores = self.load_all_scores()
        if scores:
            self.high_score = scores[0]['score']
        else:
            self.high_score = 0
    
    def load_all_scores(self):
        """تحميل كل النقاط"""
        try:
            with open(os.path.join(SAVE_DIR, "high_scores.json"), 'r') as f:
                return json.load(f)
        except:
            return []
    
    def get_high_scores_table(self, limit=10):
        """الحصول على جدول أعلى النقاط"""
        scores = self.load_all_scores()
        return scores[:limit]
    
    def calculate_rank(self):
        """حساب الرتبة بناءً على النقاط"""
        if self.score >= 10000:
            return "🐍 Snake Master"
        elif self.score >= 5000:
            return "👑 King Cobra"
        elif self.score >= 2000:
            return "⚔️ Viper Warrior"
        elif self.score >= 1000:
            return "🏹 Python Hunter"
        elif self.score >= 500:
            return "🛡️ Anaconda Defender"
        elif self.score >= 200:
            return "🌿 Grass Snake"
        else:
            return "🥚 Egg Eater"