"""
💾 نظام الحفظ والتحميل
"""

import json
import os
import pickle
from datetime import datetime
from config import *

class SaveManager:
    """مدير الحفظ والتحميل"""
    def __init__(self):
        self.save_dir = SAVE_DIR
        self.high_scores_file = os.path.join(self.save_dir, "high_scores.json")
        self.settings_file = os.path.join(self.save_dir, "settings.json")
        self.game_saves_dir = os.path.join(self.save_dir, "game_saves")
        
        # إنشاء المجلدات إذا لم تكن موجودة
        self.create_directories()
    
    def create_directories(self):
        """إنشاء مجلدات الحفظ"""
        os.makedirs(self.save_dir, exist_ok=True)
        os.makedirs(self.game_saves_dir, exist_ok=True)
    
    # === إدارة أعلى النقاط ===
    
    def save_high_score(self, player_name, score, level, foods_eaten, play_time):
        """حفظ أعلى نقاط"""
        try:
            # تحميل النقاط الحالية
            scores = self.load_high_scores()
            
            # إضافة النتيجة الجديدة
            new_score = {
                'player': player_name,
                'score': score,
                'level': level,
                'foods_eaten': foods_eaten,
                'play_time': play_time,
                'date': datetime.now().isoformat()
            }
            
            scores.append(new_score)
            
            # ترتيب تنازلي حسب النقاط
            scores.sort(key=lambda x: x['score'], reverse=True)
            
            # حفظ أول 10 نتائج فقط
            scores = scores[:10]
            
            # الحفظ في الملف
            with open(self.high_scores_file, 'w') as f:
                json.dump(scores, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving high score: {e}")
            return False
    
    def load_high_scores(self):
        """تحميل أعلى النقاط"""
        try:
            if os.path.exists(self.high_scores_file):
                with open(self.high_scores_file, 'r') as f:
                    return json.load(f)
            return []
        except:
            return []
    
    def get_high_score(self):
        """الحصول على أعلى نقاط"""
        scores = self.load_high_scores()
        if scores:
            return scores[0]['score']
        return 0
    
    def get_high_scores_table(self, limit=10):
        """الحصول على جدول أعلى النقاط"""
        scores = self.load_high_scores()
        return scores[:limit]
    
    # === إدارة الإعدادات ===
    
    def save_settings(self, settings):
        """حفظ الإعدادات"""
        try:
            default_settings = {
                'music_volume': 0.7,
                'sfx_volume': 0.8,
                'game_speed': 10,
                'player_name': 'Player',
                'controls': {
                    'up': ['up', 'w'],
                    'down': ['down', 's'],
                    'left': ['left', 'a'],
                    'right': ['right', 'd'],
                    'pause': 'escape'
                }
            }
            
            # دمج مع الإعدادات الافتراضية
            merged_settings = {**default_settings, **settings}
            
            with open(self.settings_file, 'w') as f:
                json.dump(merged_settings, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def load_settings(self):
        """تحميل الإعدادات"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            
            # إرجاع الإعدادات الافتراضية
            return {
                'music_volume': 0.7,
                'sfx_volume': 0.8,
                'game_speed': 10,
                'player_name': 'Player',
                'controls': {
                    'up': ['up', 'w'],
                    'down': ['down', 's'],
                    'left': ['left', 'a'],
                    'right': ['right', 'd'],
                    'pause': 'escape'
                }
            }
        except:
            return {
                'music_volume': 0.7,
                'sfx_volume': 0.8,
                'game_speed': 10,
                'player_name': 'Player',
                'controls': {
                    'up': ['up', 'w'],
                    'down': ['down', 's'],
                    'left': ['left', 'a'],
                    'right': ['right', 'd'],
                    'pause': 'escape'
                }
            }
    
    # === حفظ/تحميل اللعبة ===
    
    def save_game(self, game_data, slot=0):
        """حفظ حالة اللعبة"""
        try:
            save_file = os.path.join(self.game_saves_dir, f"save_{slot}.pkl")
            
            # إضافة معلومات الحفظ
            game_data['save_info'] = {
                'save_date': datetime.now().isoformat(),
                'save_slot': slot,
                'version': '1.0'
            }
            
            with open(save_file, 'wb') as f:
                pickle.dump(game_data, f)
            
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self, slot=0):
        """تحميل حالة اللعبة"""
        try:
            save_file = os.path.join(self.game_saves_dir, f"save_{slot}.pkl")
            
            if os.path.exists(save_file):
                with open(save_file, 'rb') as f:
                    return pickle.load(f)
            return None
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
    
    def get_save_slots(self):
        """الحصول على معلومات فتحات الحفظ"""
        slots = []
        for i in range(5):  # 5 فتحات حفظ
            save_file = os.path.join(self.game_saves_dir, f"save_{i}.pkl")
            if os.path.exists(save_file):
                try:
                    with open(save_file, 'rb') as f:
                        game_data = pickle.load(f)
                    
                    slots.append({
                        'slot': i,
                        'exists': True,
                        'score': game_data.get('score', 0),
                        'level': game_data.get('level', 1),
                        'save_date': game_data.get('save_info', {}).get('save_date', '')
                    })
                except:
                    slots.append({
                        'slot': i,
                        'exists': False
                    })
            else:
                slots.append({
                    'slot': i,
                    'exists': False
                })
        
        return slots
    
    def delete_save(self, slot=0):
        """حذف حفظ"""
        try:
            save_file = os.path.join(self.game_saves_dir, f"save_{slot}.pkl")
            if os.path.exists(save_file):
                os.remove(save_file)
                return True
            return False
        except:
            return False
    
    # === إحصائيات اللعبة ===
    
    def save_game_stats(self, stats):
        """حفظ إحصائيات اللعبة"""
        try:
            stats_file = os.path.join(self.save_dir, "game_stats.json")
            
            # تحميل الإحصائيات الحالية
            all_stats = self.load_game_stats()
            
            # إضافة الإحصائيات الجديدة
            stats['date'] = datetime.now().isoformat()
            all_stats.append(stats)
            
            # حفظ أول 100 إحصائية فقط
            all_stats = all_stats[-100:]
            
            with open(stats_file, 'w') as f:
                json.dump(all_stats, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving game stats: {e}")
            return False
    
    def load_game_stats(self):
        """تحميل إحصائيات اللعبة"""
        try:
            stats_file = os.path.join(self.save_dir, "game_stats.json")
            if os.path.exists(stats_file):
                with open(stats_file, 'r') as f:
                    return json.load(f)
            return []
        except:
            return []
    
    def get_player_stats(self, player_name):
        """الحصول على إحصائيات لاعب معين"""
        all_stats = self.load_game_stats()
        player_stats = [s for s in all_stats if s.get('player_name') == player_name]
        return player_stats
    
    # === وظائف مساعدة ===
    
    def export_high_scores(self, filename="high_scores_export.json"):
        """تصدير أعلى النقاط"""
        try:
            scores = self.load_high_scores()
            export_file = os.path.join(self.save_dir, filename)
            
            with open(export_file, 'w') as f:
                json.dump(scores, f, indent=2)
            
            return export_file
        except:
            return None
    
    def import_high_scores(self, filename):
        """استيراد أعلى النقاط"""
        try:
            import_file = os.path.join(self.save_dir, filename)
            if os.path.exists(import_file):
                with open(import_file, 'r') as f:
                    imported_scores = json.load(f)
                
                # دمج مع النقاط الحالية
                current_scores = self.load_high_scores()
                all_scores = current_scores + imported_scores
                
                # ترتيب وتحديد الأعلى
                all_scores.sort(key=lambda x: x['score'], reverse=True)
                all_scores = all_scores[:10]
                
                # الحفظ
                with open(self.high_scores_file, 'w') as f:
                    json.dump(all_scores, f, indent=2)
                
                return True
            return False
        except:
            return False
    
    def clear_all_data(self):
        """مسح كل البيانات"""
        try:
            # مسح النقاط
            if os.path.exists(self.high_scores_file):
                os.remove(self.high_scores_file)
            
            # مسح الإعدادات
            if os.path.exists(self.settings_file):
                os.remove(self.settings_file)
            
            # مسح الحفظات
            for file in os.listdir(self.game_saves_dir):
                os.remove(os.path.join(self.game_saves_dir, file))
            
            # مسح الإحصائيات
            stats_file = os.path.join(self.save_dir, "game_stats.json")
            if os.path.exists(stats_file):
                os.remove(stats_file)
            
            return True
        except:
            return False
    
    def backup_save_data(self, backup_name):
        """نسخ احتياطي للبيانات"""
        try:
            import shutil
            import zipfile
            
            backup_dir = os.path.join(self.save_dir, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            backup_file = os.path.join(backup_dir, f"{backup_name}.zip")
            
            # إنشاء ملف ZIP
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # إضافة الملفات
                files_to_backup = [
                    self.high_scores_file,
                    self.settings_file,
                    os.path.join(self.save_dir, "game_stats.json")
                ]
                
                for file in files_to_backup:
                    if os.path.exists(file):
                        zipf.write(file, os.path.basename(file))
                
                # إضافة مجلد الحفظات
                for root, dirs, files in os.walk(self.game_saves_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.save_dir)
                        zipf.write(file_path, arcname)
            
            return backup_file
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None