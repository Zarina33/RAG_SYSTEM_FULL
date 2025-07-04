#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конфигурация голосового помощника банка Бакай
"""

# =============================================================================
# ОСНОВНЫЕ НАСТРОЙКИ БАНКА
# =============================================================================

BANK_CONFIG = {
    "name": "Бакай Банк",
    "website": "https://bakai.kg",
    "support_phone": "+996 (312) 666-000",
    "main_office": "г. Бишкек, ул. Тыныстанова 101"
}

# =============================================================================
# ССЫЛКИ НА СТРАНИЦЫ БАНКА
# =============================================================================

BANK_LINKS = {
    "general": "https://bakai.kg/ru/individual/",
    "branches": "https://bakai.kg/ru/office/",
    "cards": "https://bakai.kg/ru/individual/cards/",
    "atm": "https://bakai.kg/ru/office/",
    "services": "https://bakai.kg/ru/individual/",
    "support": "https://bakai.kg/ru/individual/",
    "deposits": "https://bakai.kg/ru/individual/deposits/",
    "credits": "https://bakai.kg/ru/individual/credits/",
    "business": "https://bakai.kg/ru/business/",
    "insurance": "https://bakai.kg/ru/individual/insurance/",
    "transfers": "https://bakai.kg/ru/individual/transfers/",
    "exchange": "https://bakai.kg/ru/individual/exchange/"
}

# =============================================================================
# НАСТРОЙКИ RAG СИСТЕМЫ
# =============================================================================

RAG_CONFIG = {
    "chroma_db_path": "/Users/zarinamacbook/rag_system/chroma_db",
    "embedding_model": "llama3",
    "llm_model": "llama3",
    "search_k": 5,
    "temperature": 0.1,
    "max_tokens": 600,
    "top_p": 0.9,
    "repeat_penalty": 1.1
}

# =============================================================================
# НАСТРОЙКИ TTS (ОЗВУЧИВАНИЕ)
# =============================================================================

TTS_CONFIG = {
    "cache_dir": "./torch_hub_cache",
    "sample_rate": 48000,
    "default_voice": "baya",
    "language": "ru",
    "model_name": "v3_1_ru"
}

# =============================================================================
# НАСТРОЙКИ КОНТЕНТ-МЕНЕДЖЕРА
# =============================================================================

CONTENT_CONFIG = {
    "max_text_length": 500,  # Максимальная длина текста для TTS
    "min_answer_length": 10,  # Минимальная длина ответа
    "enable_politeness": True,  # Включить систему вежливости
    "enable_filtering": True,   # Включить фильтрацию
    "enable_offers": True       # Включить предложения услуг
}

# =============================================================================
# НАСТРОЙКИ СИСТЕМЫ
# =============================================================================

SYSTEM_CONFIG = {
    "debug_mode": False,
    "log_file": "./bakai_assistant.log",
    "auto_save_audio": True,
    "audio_format": "wav",
    "max_search_results": 10
}