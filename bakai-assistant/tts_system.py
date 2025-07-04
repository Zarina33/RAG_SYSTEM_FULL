#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Система озвучивания для банка Бакай на основе Silero TTS
"""

import os
import re
import ssl
import time
import subprocess
from typing import Optional, List
import torch
import torchaudio
from config import TTS_CONFIG, CONTENT_CONFIG

class BakaiTTS:
    """Система озвучивания для банка Бакай на основе Silero TTS"""
    
    def __init__(self, cache_dir: str = None):
        self.cache_dir = cache_dir or TTS_CONFIG["cache_dir"]
        self.model = None
        self.sample_rate = TTS_CONFIG["sample_rate"]
        self.language = TTS_CONFIG["language"]
        self.model_name = TTS_CONFIG["model_name"]
        self.is_initialized = False
        self._init_model()
    
    def _init_model(self) -> None:
        """Инициализация модели TTS"""
        try:
            print("🔊 Инициализация системы озвучивания Silero TTS...")
            
            # Настройка SSL для загрузки модели
            ssl._create_default_https_context = ssl._create_unverified_context
            
            # Создаем директорию кэша
            os.makedirs(self.cache_dir, exist_ok=True)
            torch.hub.set_dir(self.cache_dir)
            
            # Загружаем русскую модель Silero
            self.model, _ = torch.hub.load(
                repo_or_dir='snakers4/silero-models',
                model='silero_tts',
                language=self.language,
                speaker=self.model_name,
                force_reload=False,
                trust_repo=True
            )
            
            self.is_initialized = True
            print("✅ Система озвучивания готова!")
            
        except Exception as e:
            print(f"❌ Ошибка инициализации TTS: {e}")
            print("⚠️ Продолжаем работу без озвучивания")
            self.model = None
            self.is_initialized = False
    
    def speak(self, text: str, voice: str = None, save_file: bool = True, play_audio: bool = True) -> Optional[str]:
        """
        Озвучивание текста
        
        Args:
            text: Текст для озвучивания
            voice: Голос (по умолчанию из конфига)
            save_file: Сохранять ли аудиофайл
            play_audio: Воспроизводить ли аудио
        
        Returns:
            Путь к аудиофайлу или None
        """
        if not self.is_initialized or not self.model:
            print("⚠️ TTS недоступен")
            return None
        
        try:
            # Очищаем и подготавливаем текст
            clean_text = self._prepare_text_for_speech(text)
            if not clean_text.strip():
                return None
            
            # Выбираем голос
            if not voice:
                voice = TTS_CONFIG["default_voice"]
            
            print(f"🔊 Озвучивание голосом '{voice}': {clean_text[:50]}...")
            
            # Генерируем аудио
            audio_tensor = self.model.apply_tts(
                text=clean_text,
                speaker=voice,
                sample_rate=self.sample_rate
            )
            
            # Сохраняем файл
            filename = None
            if save_file:
                timestamp = int(time.time())
                filename = f"/Users/zarinamacbook/rag_system/bakai-assistant/voices/bakai_speech_{timestamp}_{voice}.wav"
                torchaudio.save(filename, audio_tensor.unsqueeze(0), self.sample_rate)
            
            # Воспроизводим
            if play_audio and filename:
                self._play_audio_file(filename)
            
            return filename
            
        except Exception as e:
            print(f"❌ Ошибка озвучивания: {e}")
            return None
    
    def _prepare_text_for_speech(self, text: str) -> str:
        """Подготовка текста для качественного озвучивания"""
        # Убираем URL и технические метки
        text = re.sub(r'https?://[^\s]+', '', text)
        text = re.sub(r'Подробности:\s*', '', text)
        text = re.sub(r'💡\s*', '', text)  # Убираем эмодзи
        
        # Замены для лучшего произношения
        replacements = {
            'руб.': 'рублей', 'сом.': 'сом', 'тыс.': 'тысяч', 'млн.': 'миллионов',
            'г.': 'года', 'ул.': 'улица', 'пр.': 'проспект', 'д.': 'дом',
            'тел.': 'телефон', 'email': 'электронная почта', 'SMS': 'СМС',
            'ATM': 'банкомат', 'NFC': 'НФС', 'PIN': 'пин-код', 'CVV': 'код CVV',
            'р/с': 'расчетный счет', 'ИП': 'индивидуальный предприниматель',
            'кв.': 'квартира', 'факс.': 'факс'
        }
        
        for abbr, full in replacements.items():
            text = text.replace(abbr, full)
        
        # Очистка от лишних символов
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Ограничиваем длину
        max_length = CONTENT_CONFIG["max_text_length"]
        if len(text) > max_length:
            sentences = text.split('.')
            result = ""
            for sentence in sentences:
                if len(result + sentence) < max_length - 50:
                    result += sentence + ". "
                else:
                    break
            text = result.strip()
        
        return text
    
    def _play_audio_file(self, filename: str) -> None:
        """Воспроизведение аудиофайла на разных платформах"""
        try:
            # macOS
            if os.system("which afplay > /dev/null 2>&1") == 0:
                subprocess.Popen(['afplay', filename], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Linux
            elif os.system("which aplay > /dev/null 2>&1") == 0:
                subprocess.Popen(['aplay', filename], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Windows
            elif os.name == 'nt':
                os.system(f'start /min "" "{filename}"')
            else:
                print(f"🔊 Аудио сохранено: {filename}")
                
        except Exception as e:
            print(f"⚠️ Ошибка воспроизведения: {e}")
            print(f"🔊 Аудио сохранено: {filename}")
    
    def get_available_voices(self) -> List[str]:
        """Получение списка доступных голосов"""
        if self.is_initialized and self.model:
            return list(self.model.speakers)
        return ['aidar', 'baya', 'kseniya', 'xenia']  # Резервный список
    
    def test_voice(self, voice: str, test_text: str = None) -> bool:
        """Тестирование конкретного голоса"""
        if not test_text:
            test_text = f"Привет! Меня зовут {voice}. Добро пожаловать в банк Бакай!"
        
        result = self.speak(test_text, voice=voice)
        return result is not None
    
    def get_voice_info(self) -> dict:
        """Получение информации о голосах"""
        voice_descriptions = {
            'aidar': {
                'gender': 'мужской',
                'description': 'Официальные объявления, адреса',
                'use_case': 'location_queries'
            },
            'baya': {
                'gender': 'женский',
                'description': 'Универсальный, приятный тембр',
                'use_case': 'general_queries'
            },
            'kseniya': {
                'gender': 'женский', 
                'description': 'Мягкий, подходит для инструкций',
                'use_case': 'instructions'
            },
            'xenia': {
                'gender': 'женский',
                'description': 'Четкий, важная информация',
                'use_case': 'important_info'
            }
        }
        
        available_voices = self.get_available_voices()
        return {voice: voice_descriptions.get(voice, {'description': 'Описание недоступно'}) 
                for voice in available_voices}
    
    def select_voice_for_query(self, query: str) -> str:
        """Автоматический выбор голоса в зависимости от типа запроса"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['где', 'адрес', 'находится', 'расположен']):
            return 'aidar'  # Мужской голос для адресов
        elif any(word in query_lower for word in ['как', 'способ', 'инструкция', 'оформить']):
            return 'baya'   # Женский голос для инструкций
        elif any(word in query_lower for word in ['важно', 'внимание', 'срочно']):
            return 'xenia'  # Четкий голос для важной информации
        else:
            return 'kseniya'  # Мягкий женский голос по умолчанию