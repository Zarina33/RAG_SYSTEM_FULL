#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Главный класс голосового помощника банка Бакай
"""

from typing import Dict, List, Optional, Any
from config import BANK_CONFIG, BANK_LINKS
from tts_system import BakaiTTS
from content_manager import BakaiContentManager
from rag_system import BakaiRAG
from link_manager import BakaiLinkManager

class BakaiAssistant:
    """Главный класс голосового помощника банка Бакай"""
    
    def __init__(self):
        print("🏦 Инициализация голосового помощника банка Бакай...")
        
        # Инициализация компонентов
        self.tts = BakaiTTS()
        self.content_manager = BakaiContentManager()
        self.rag = BakaiRAG()
        self.link_manager = BakaiLinkManager()
        
        # Настройки
        self.tts_enabled = True
        self.debug_mode = False
        self.session_stats = {
            'queries_processed': 0,
            'services_detected': {},
            'errors_count': 0
        }
        
        print("✅ Помощник готов к работе!")
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Обработка пользовательского запроса"""
        try:
            print(f"\n🤖 Обработка запроса: '{query}'")
            self.session_stats['queries_processed'] += 1
            
            # 1. Озвучиваем вопрос
            if self.tts_enabled and self.tts.is_initialized:
                voice = self.tts.select_voice_for_query(query)
                self.tts.speak(f"Ваш вопрос: {query}", voice="kseniya")
            
            # 2. Поиск документов
            print("🔍 Поиск релевантных документов...")
            documents = self.rag.search_documents(query)
            
            # 3. Генерация или создание ответа
            if not documents:
                answer = "К сожалению, не найдено информации по вашему запросу."
                link = BANK_LINKS["support"]
                service_type = None
            else:
                # Генерация ответа
                print("📝 Генерация ответа...")
                raw_answer = self.rag.generate_answer(query, documents)
                
                # Улучшение ответа (фильтрация, вежливость, предложения)
                print("✨ Улучшение ответа...")
                enhanced_answer = self.content_manager.enhance_response(raw_answer, query)
                
                # Определение типа услуги
                service_type = self.content_manager.detect_service_type(query)
                if service_type:
                    self.session_stats['services_detected'][service_type] = \
                        self.session_stats['services_detected'].get(service_type, 0) + 1
                
                # Получение релевантной ссылки
                link = self.link_manager.get_relevant_link(query, documents)
                
                answer = enhanced_answer
            
            # 4. Финальный ответ с ссылкой
            full_answer = f"{answer}\n\nПодробности: {link}"
            
            # 5. Озвучиваем ответ
            if self.tts_enabled and self.tts.is_initialized:
                voice = self.tts.select_voice_for_query(query)
                print(f"🔊 Озвучивание ответа голосом {voice}...")
                self.tts.speak(answer, voice=voice)
            
            # 6. Формируем результат
            result = {
                "answer": full_answer,
                "raw_answer": answer,
                "documents": documents,
                "link": link,
                "service_type": service_type,
                "voice_used": voice if self.tts_enabled else None,
                "documents_found": len(documents),
                "processing_success": True
            }
            
            print(f"✅ Запрос обработан успешно")
            return result
            
        except Exception as e:
            self.session_stats['errors_count'] += 1
            error_msg = f"Произошла ошибка при обработке запроса: {str(e)}"
            print(f"❌ {error_msg}")
            
            # Озвучиваем ошибку
            if self.tts_enabled and self.tts.is_initialized:
                self.tts.speak("Извините, произошла техническая ошибка.")
            
            return {
                "answer": f"{error_msg}\n\nПодробности: {BANK_LINKS['support']}",
                "raw_answer": error_msg,
                "documents": [],
                "link": BANK_LINKS["support"],
                "service_type": None,
                "voice_used": None,
                "documents_found": 0,
                "processing_success": False,
                "error": str(e)
            }
    
    def set_tts_enabled(self, enabled: bool) -> None:
        """Включение/выключение озвучивания"""
        self.tts_enabled = enabled
        status = "включено" if enabled else "отключено"
        print(f"🔊 Озвучивание {status}")
        
        if enabled and self.tts.is_initialized:
            self.tts.speak(f"Озвучивание {status}")
    
    def set_debug_mode(self, enabled: bool) -> None:
        """Включение/выключение режима отладки"""
        self.debug_mode = enabled
        status = "включен" if enabled else "выключен"
        print(f"🐛 Режим отладки {status}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Получение статуса всех компонентов системы"""
        return {
            # Основные компоненты
            "tts_available": self.tts.is_initialized,
            "tts_enabled": self.tts_enabled,
            "database_ready": self.rag.vectorstore is not None,
            "llm_ready": self.rag.llm is not None,
            
            # TTS информация
            "available_voices": self.tts.get_available_voices(),
            "voice_info": self.tts.get_voice_info(),
            
            # Статистика базы данных
            "database_stats": self.rag.get_database_stats(),
            
            # Конфигурация контента
            "content_filters_enabled": True,
            "politeness_enabled": True,
            "service_offers_enabled": True,
            
            # Статистика сессии
            "session_stats": self.session_stats.copy(),
            
            # Информация о банке
            "bank_info": BANK_CONFIG,
            
            # Системные настройки
            "debug_mode": self.debug_mode
        }
    
    def get_service_categories(self) -> Dict[str, Dict[str, Any]]:
        """Получение информации о категориях услуг"""
        categories = self.link_manager.get_all_categories()
        result = {}
        
        for category in categories:
            result[category] = {
                "info": self.link_manager.get_category_info(category),
                "link": BANK_LINKS.get(category, BANK_LINKS["general"]),
                "service_patterns_count": len(self.content_manager.service_patterns.get(category, [])),
                "offers_available": len(self.content_manager.service_offers.get(category, []))
            }
        
        return result
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Подробный анализ запроса без генерации ответа"""
        analysis = {
            "query": query,
            "query_length": len(query),
            "detected_service": self.content_manager.detect_service_type(query),
            "link_categories": self.link_manager.analyze_query_categories(query),
            "suggested_voice": self.tts.select_voice_for_query(query) if self.tts.is_initialized else None
        }
        
        # Поиск документов для анализа
        documents = self.rag.search_documents(query, k=3)
        analysis["documents_preview"] = [
            {
                "content_preview": doc.page_content[:100] + "...",
                "metadata": doc.metadata if hasattr(doc, 'metadata') else {}
            }
            for doc in documents[:3]
        ]
        
        return analysis
    
    def reset_session_stats(self) -> None:
        """Сброс статистики сессии"""
        self.session_stats = {
            'queries_processed': 0,
            'services_detected': {},
            'errors_count': 0
        }
        print("📊 Статистика сессии сброшена")
    
    def validate_system(self) -> Dict[str, Any]:
        """Комплексная проверка системы"""
        validation = {
            "tts_system": {
                "initialized": self.tts.is_initialized,
                "voices_available": len(self.tts.get_available_voices()),
                "test_passed": False
            },
            "rag_system": {
                "database_ready": self.rag.vectorstore is not None,
                "llm_ready": self.rag.llm is not None,
                "documents_count": self.rag.document_count
            },
            "content_system": {
                "forbidden_words_count": len(self.content_manager.forbidden_words),
                "service_types_count": len(self.content_manager.service_patterns),
                "polite_phrases_count": sum(len(phrases) for phrases in self.content_manager.polite_phrases.values())
            },
            "link_system": {
                "categories_count": len(self.link_manager.get_all_categories()),
                "links_valid": self.link_manager.validate_links()
            }
        }
        
        # Тест TTS
        if self.tts.is_initialized:
            try:
                test_result = self.tts.test_voice("baya", "Тест системы")
                validation["tts_system"]["test_passed"] = test_result is not None
            except:
                validation["tts_system"]["test_passed"] = False
        
        # Общая оценка
        critical_components = [
            validation["rag_system"]["database_ready"],
            validation["rag_system"]["llm_ready"],
            validation["rag_system"]["documents_count"] > 0
        ]
        
        validation["overall_ready"] = all(critical_components)
        validation["critical_issues"] = len([c for c in critical_components if not c])
        
        return validation
    
    def get_help_info(self) -> Dict[str, Any]:
        """Получение справочной информации"""
        return {
            "bank_info": BANK_CONFIG,
            "available_services": list(self.content_manager.service_patterns.keys()),
            "voice_commands": [
                "тихо / громко - управление озвучиванием",
                "статус - состояние системы",
                "помощь - эта справка",
                "выход - завершение работы"
            ],
            "supported_queries": [
                "Вопросы о банковских услугах",
                "Адреса офисов и филиалов",
                "Информация о картах и кредитах",
                "Условия депозитов и вкладов",
                "Бизнес-услуги и расчетные счета"
            ],
            "contact_info": {
                "phone": BANK_CONFIG["support_phone"],
                "website": BANK_CONFIG["website"],
                "main_office": BANK_CONFIG["main_office"]
            }
        }