"""
🔊 نظام الصوت والموسيقى
"""

import pygame
import math
import numpy as np
from config import *

class SoundEffect:
    """تأثير صوتي واحد"""
    def __init__(self, frequency, duration, wave_type='sine', envelope=None):
        self.frequency = frequency
        self.duration = duration
        self.wave_type = wave_type
        self.envelope = envelope or {'attack': 0.1, 'decay': 0.2, 'sustain': 0.7, 'release': 0.3}
        self.sound = self.generate_sound()
    
    def generate_sound(self):
        """توليد الصوت باستخدام numpy"""
        sample_rate = 22050
        n_samples = int(self.duration * sample_rate)
        
        # إنشاء مصفوفة numpy للعينات
        t = np.linspace(0, self.duration, n_samples, False)
        
        # توليد الموجة الأساسية
        if self.wave_type == 'sine':
            wave = np.sin(2 * np.pi * self.frequency * t)
        elif self.wave_type == 'square':
            wave = np.sign(np.sin(2 * np.pi * self.frequency * t))
        elif self.wave_type == 'sawtooth':
            wave = 2 * (t * self.frequency - np.floor(0.5 + t * self.frequency))
        else:  # triangle
            wave = 2 * np.abs(2 * (t * self.frequency - np.floor(t * self.frequency + 0.5))) - 1
        
        # تطبيق الغلاف
        envelope_array = self.get_envelope_array(n_samples, sample_rate)
        wave = wave * envelope_array
        
        # تحويل إلى 16-bit
        wave_normalized = np.int16(wave * 32767)
        
        # إنشاء الصوت
        sound = pygame.sndarray.make_sound(np.array([wave_normalized, wave_normalized]).T)
        return sound
    
    def get_envelope_array(self, n_samples, sample_rate):
        """الحصول على مصفوفة الغلاف"""
        t = np.linspace(0, self.duration, n_samples)
        envelope = np.zeros(n_samples)
        
        attack = self.envelope['attack']
        decay = self.envelope['decay']
        sustain = self.envelope['sustain']
        release = self.envelope['release']
        
        # حساب الغلاف
        for i in range(n_samples):
            time_ratio = t[i] / self.duration
            
            if time_ratio < attack:
                envelope[i] = time_ratio / attack
            elif time_ratio < attack + decay:
                envelope[i] = 1.0 - (1.0 - sustain) * ((time_ratio - attack) / decay)
            elif time_ratio < 1.0 - release:
                envelope[i] = sustain
            else:
                envelope[i] = sustain * (1.0 - (time_ratio - (1.0 - release)) / release)
        
        return envelope
    
    def play(self):
        """تشغيل الصوت"""
        self.sound.play()

class AudioManager:
    """مدير الصوتيات"""
    def __init__(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.sounds = {}
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.music_playing = None
        
        # إنشاء الأصوات
        self.create_sounds()
    
    def create_sounds(self):
        """إنشاء جميع الأصوات"""
        # أصوات الأكل
        self.sounds['eat'] = SoundEffect(523.25, 0.1, 'square',  # C5
                                         {'attack': 0.05, 'decay': 0.1, 'sustain': 0.5, 'release': 0.05})
        self.sounds['special_eat'] = SoundEffect(1046.50, 0.2, 'sine',  # C6
                                                {'attack': 0.1, 'decay': 0.2, 'sustain': 0.7, 'release': 0.2})
        
        # أصوات المكافآت
        self.sounds['powerup'] = SoundEffect(659.25, 0.3, 'sine',  # E5
                                            {'attack': 0.1, 'decay': 0.3, 'sustain': 0.6, 'release': 0.3})
        
        # أصوات الحركة
        self.sounds['move'] = SoundEffect(261.63, 0.05, 'square',  # C4
                                         {'attack': 0.01, 'decay': 0.04, 'sustain': 0.3, 'release': 0.01})
        
        # أصوات الاصطدام
        self.sounds['collision'] = SoundEffect(220.00, 0.4, 'sawtooth',  # A3
                                              {'attack': 0.05, 'decay': 0.35, 'sustain': 0.2, 'release': 0.1})
        
        # أصوات التقدم
        self.sounds['level_up'] = SoundEffect(523.25, 0.5, 'sine',  # C5
                                             {'attack': 0.1, 'decay': 0.4, 'sustain': 0.8, 'release': 0.2})
        self.sounds['game_over'] = SoundEffect(174.61, 1.0, 'sawtooth',  # F3
                                              {'attack': 0.1, 'decay': 0.9, 'sustain': 0.1, 'release': 0.3})
        
        # أصوات الأزرار
        self.sounds['button_hover'] = SoundEffect(392.00, 0.1, 'sine',  # G4
                                                 {'attack': 0.05, 'decay': 0.05, 'sustain': 0.3, 'release': 0.05})
        self.sounds['button_click'] = SoundEffect(493.88, 0.15, 'square',  # B4
                                                 {'attack': 0.05, 'decay': 0.1, 'sustain': 0.4, 'release': 0.05})
    
    def play_eat(self):
        """تشغيل صوت الأكل"""
        self.sounds['eat'].sound.set_volume(self.sfx_volume * 0.8)
        self.sounds['eat'].play()
    
    def play_special_eat(self, food_type):
        """تشغيل صوت أكل الطعام الخاص"""
        self.sounds['special_eat'].sound.set_volume(self.sfx_volume * 1.0)
        self.sounds['special_eat'].play()
    
    def play_powerup(self, powerup_type):
        """تشغيل صوت المكافأة"""
        self.sounds['powerup'].sound.set_volume(self.sfx_volume * 0.9)
        self.sounds['powerup'].play()
    
    def play_move(self):
        """تشغيل صوت الحركة"""
        self.sounds['move'].sound.set_volume(self.sfx_volume * 0.3)
        self.sounds['move'].play()
    
    def play_collision(self):
        """تشغيل صوت الاصطدام"""
        self.sounds['collision'].sound.set_volume(self.sfx_volume * 1.0)
        self.sounds['collision'].play()
    
    def play_level_up(self):
        """تشغيل صوت التقدم للمستوى"""
        self.sounds['level_up'].sound.set_volume(self.sfx_volume * 0.9)
        self.sounds['level_up'].play()
    
    def play_game_over(self):
        """تشغيل صوت انتهاء اللعبة"""
        self.sounds['game_over'].sound.set_volume(self.sfx_volume * 1.0)
        self.sounds['game_over'].play()
    
    def play_button_hover(self):
        """تشغيل صوت تمرير الزر"""
        self.sounds['button_hover'].sound.set_volume(self.sfx_volume * 0.5)
        self.sounds['button_hover'].play()
    
    def play_button_click(self):
        """تشغيل صوت نقر الزر"""
        self.sounds['button_click'].sound.set_volume(self.sfx_volume * 0.7)
        self.sounds['button_click'].play()
    
    def play_music(self, track_name):
        """تشغيل الموسيقى"""
        # يمكن إضافة ملفات MP3 هنا
        pass
    
    def stop_music(self):
        """إيقاف الموسيقى"""
        pygame.mixer.music.stop()
        self.music_playing = None
    
    def set_music_volume(self, volume):
        """ضبط مستوى الموسيقى"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume):
        """ضبط مستوى المؤثرات الصوتية"""
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def pause_all(self):
        """إيقاف كل الصوتيات مؤقتاً"""
        pygame.mixer.pause()
    
    def resume_all(self):
        """استئناف كل الصوتيات"""
        pygame.mixer.unpause()