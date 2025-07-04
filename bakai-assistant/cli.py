#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интерфейс командной строки для голосового помощника банка Бакай
"""

import time
from typing import Dict, Any
from assistant import BakaiAssistant
from config import BANK_CONFIG

class BakaiCLI:
    """Интерфейс командной строки для помощника"""
    
    def __init__(self):
        self.assistant = BakaiAssistant()
        self.running = True
        self.show_sources = False
    
    def show_welcome(self) -> None:
        """Показ приветственного сообщения"""
        print("\n" + "=" * 80)
        print("🏦 ГОЛОСОВОЙ ПОМОЩНИК БАНКА БАКАЙ")
        print("Система поддержки клиентов с искусственным интеллектом")
        print("=" * 80)
        
        # Проверяем статус системы
        status = self.assistant.get_system_status()
        
        print("📊 СТАТУС СИСТЕМЫ:")
        print(f"   🔊 TTS: {'✅ готов' if status['tts_available'] else '❌ недоступен'}")
        print(f"   🧠 LLM: {'✅ готов' if status['llm_ready'] else '❌ недоступен'}")
        print(f"   📚 База знаний: {'✅ готова' if status['database_ready'] else '❌ недоступна'}")
        
        if status['database_stats']['total_documents'] > 0:
            print(f"   📄 Документов: {status['database_stats']['total_documents']}")
        
        if status['tts_available']:
            voices = status['available_voices']
            print(f"   🗣️ Голоса: {', '.join(voices)}")
            
            # Приветственное сообщение
            welcome_text = "Добро пожаловать! Я голосовой помощник банка Бакай. Чем могу помочь?"
            print(f"\n🔊 {welcome_text}")
            if status['tts_enabled']:
                self.assistant.tts.speak(welcome_text, voice="baya")
        
        self.show_commands()
    
    def show_commands(self) -> None:
        """Показ доступных команд"""
        print("\n📋 ДОСТУПНЫЕ КОМАНДЫ:")
        print("   💬 Просто задайте вопрос о банковских услугах")
        print("   🧪 'тест' - запуск системных тестов")
        print("   🗣️ 'голоса' - демонстрация голосов")
        print("   🔇 'тихо' - отключить озвучивание")
        print("   🔊 'громко' - включить озвучивание")
        print("   📊 'статус' - подробный статус системы")
        print("   🔧 'настройки' - настройки системы")
        print("   📈 'анализ <запрос>' - анализ запроса")
        print("   📋 'услуги' - список банковских услуг")
        print("   📄 'источники вкл/выкл' - показ источников")
        print("   ❓ 'помощь' - показать команды")
        print("   🚪 'выход' - завершить работу")
        print("=" * 80)
    
    def process_command(self, command: str) -> bool:
        """Обработка специальных команд"""
        cmd = command.lower().strip()
        
        if cmd in ('выход', 'exit', 'quit', 'q'):
            self.shutdown()
            return False
        
        elif cmd in ('тест', 'test'):
            self.run_system_tests()
        
        elif cmd in ('голоса', 'voices'):
            self.demo_voices()
        
        elif cmd in ('тихо', 'mute', 'silence'):
            self.assistant.set_tts_enabled(False)
        
        elif cmd in ('громко', 'unmute', 'sound'):
            self.assistant.set_tts_enabled(True)
        
        elif cmd in ('статус', 'status'):
            self.show_detailed_status()
        
        elif cmd in ('настройки', 'settings'):
            self.show_settings()
        
        elif cmd.startswith('анализ '):
            query = cmd[7:].strip()
            if query:
                self.analyze_query(query)
            else:
                print("❌ Укажите запрос для анализа: анализ <ваш запрос>")
        
        elif cmd in ('услуги', 'services'):
            self.show_services()
        
        elif cmd in ('источники вкл', 'sources on'):
            self.show_sources = True
            print("📄 Показ источников включен")
        
        elif cmd in ('источники выкл', 'sources off'):
            self.show_sources = False
            print("📄 Показ источников отключен")
        
        elif cmd in ('помощь', 'help', '?'):
            self.show_commands()
        
        elif cmd in ('сброс', 'reset'):
            self.assistant.reset_session_stats()
        
        else:
            return False  # Не команда, обработать как запрос
        
        return True
    
    def run_system_tests(self) -> None:
        """Запуск системных тестов"""
        print("\n🧪 ЗАПУСК СИСТЕМНЫХ ТЕСТОВ")
        print("=" * 50)
        
        # Валидация системы
        validation = self.assistant.validate_system()
        
        print("📊 РЕЗУЛЬТАТЫ ВАЛИДАЦИИ:")
        
        # TTS тест
        tts_status = "✅" if validation["tts_system"]["test_passed"] else "❌"
        print(f"   {tts_status} TTS система: {validation['tts_system']['voices_available']} голосов")
        
        # RAG тест
        rag_status = "✅" if validation["rag_system"]["database_ready"] else "❌"
        print(f"   {rag_status} RAG система: {validation['rag_system']['documents_count']} документов")
        
        # Контент тест
        content_ready = validation["content_system"]["service_types_count"] > 0
        content_status = "✅" if content_ready else "❌"
        print(f"   {content_status} Контент система: {validation['content_system']['service_types_count']} типов услуг")
        
        # Ссылки тест
        links_valid = all(validation["link_system"]["links_valid"].values())
        links_status = "✅" if links_valid else "❌"
        print(f"   {links_status} Система ссылок: {validation['link_system']['categories_count']} категорий")
        
        # Общая оценка
        overall_status = "✅" if validation["overall_ready"] else "❌"
        print(f"\n{overall_status} ОБЩАЯ ГОТОВНОСТЬ: {'Система готова' if validation['overall_ready'] else 'Требуется настройка'}")
        
        if validation["critical_issues"] > 0:
            print(f"⚠️ Критических проблем: {validation['critical_issues']}")
        
        # Тест обработки запроса
        print(f"\n🔄 ТЕСТ ОБРАБОТКИ ЗАПРОСА...")
        test_query = "Как открыть карту?"
        
        try:
            result = self.assistant.process_query(test_query)
            if result["processing_success"]:
                print("✅ Тест обработки запроса пройден")
                print(f"   📄 Найдено документов: {result['documents_found']}")
                print(f"   🎯 Определена услуга: {result['service_type'] or 'не определена'}")
            else:
                print("❌ Тест обработки запроса не пройден")
        except Exception as e:
            print(f"❌ Ошибка при тесте: {e}")
    
    def demo_voices(self) -> None:
        """Демонстрация голосов"""
        if not self.assistant.tts.is_initialized:
            print("❌ Система озвучивания недоступна")
            return
        
        voice_info = self.assistant.tts.get_voice_info()
        
        print("🗣️ ДЕМОНСТРАЦИЯ ГОЛОСОВ")
        print("=" * 30)
        
        for voice, info in voice_info.items():
            print(f"\n🔊 Голос: {voice} ({info.get('gender', 'неизвестно')})")
            print(f"   Описание: {info.get('description', 'Описание недоступно')}")
            
            demo_text = f"Привет! Меня зовут {voice}. Добро пожаловать в банк Бакай!"
            self.assistant.tts.speak(demo_text, voice=voice)
            time.sleep(2)
    
    def show_detailed_status(self) -> None:
        """Показ подробного статуса системы"""
        status = self.assistant.get_system_status()
        
        print("\n📊 ПОДРОБНЫЙ СТАТУС СИСТЕМЫ")
        print("=" * 50)
        
        # Основная информация
        print(f"🏦 Банк: {status['bank_info']['name']}")
        print(f"🌐 Сайт: {status['bank_info']['website']}")
        print(f"📞 Поддержка: {status['bank_info']['support_phone']}")
        
        # Компоненты системы
        print(f"\n🔧 КОМПОНЕНТЫ:")
        print(f"   🔊 TTS: {'включен' if status['tts_enabled'] else 'отключен'} ({'доступен' if status['tts_available'] else 'недоступен'})")
        print(f"   🧠 LLM: {'готов' if status['llm_ready'] else 'не готов'}")
        print(f"   📚 База данных: {'готова' if status['database_ready'] else 'не готова'}")
        
        # Статистика базы данных
        db_stats = status['database_stats']
        if 'total_documents' in db_stats:
            print(f"\n📄 БАЗА ЗНАНИЙ:")
            print(f"   Документов: {db_stats['total_documents']}")
            if 'document_types' in db_stats:
                for doc_type, count in db_stats['document_types'].items():
                    print(f"   - {doc_type}: {count}")
        
        # Статистика сессии
        session = status['session_stats']
        print(f"\n📈 СТАТИСТИКА СЕССИИ:")
        print(f"   Запросов обработано: {session['queries_processed']}")
        print(f"   Ошибок: {session['errors_count']}")
        
        if session['services_detected']:
            print("   Определенные услуги:")
            for service, count in session['services_detected'].items():
                print(f"   - {service}: {count}")
    
    def show_settings(self) -> None:
        """Показ настроек системы"""
        status = self.assistant.get_system_status()
        
        print("\n🔧 НАСТРОЙКИ СИСТЕМЫ")
        print("=" * 30)
        
        # TTS настройки
        if status['tts_available']:
            print("🔊 ОЗВУЧИВАНИЕ:")
            print(f"   Статус: {'включено' if status['tts_enabled'] else 'отключено'}")
            print(f"   Доступные голоса: {', '.join(status['available_voices'])}")
            print("   Автовыбор голоса: включен")
        
        # Контент настройки
        print(f"\n📝 КОНТЕНТ:")
        print(f"   Фильтрация: {'включена' if status['content_filters_enabled'] else 'отключена'}")
        print(f"   Вежливость: {'включена' if status['politeness_enabled'] else 'отключена'}")
        print(f"   Предложения услуг: {'включены' if status['service_offers_enabled'] else 'отключены'}")
        print(f"   Показ источников: {'включен' if self.show_sources else 'отключен'}")
        
        # Системные настройки
        print(f"\n⚙️ СИСТЕМА:")
        print(f"   Режим отладки: {'включен' if status['debug_mode'] else 'отключен'}")
        print(f"   Автосохранение аудио: включено")
    
    def show_services(self) -> None:
        """Показ доступных банковских услуг"""
        services = self.assistant.get_service_categories()
        
        print("\n🏦 БАНКОВСКИЕ УСЛУГИ")
        print("=" * 40)
        
        for category, info in services.items():
            service_info = info['info']
            print(f"\n📋 {service_info['name'].upper()}")
            print(f"   Описание: {service_info['description']}")
            print(f"   Ссылка: {info['link']}")
            print(f"   Ключевых слов: {service_info['keywords_count']}")
            print(f"   Вариантов предложений: {info['offers_available']}")
    
    def analyze_query(self, query: str) -> None:
        """Анализ запроса"""
        print(f"\n🔍 АНАЛИЗ ЗАПРОСА: '{query}'")
        print("=" * 50)
        
        analysis = self.assistant.analyze_query(query)
        
        print(f"📏 Длина запроса: {analysis['query_length']} символов")
        print(f"🎯 Определенная услуга: {analysis['detected_service'] or 'не определена'}")
        print(f"🗣️ Рекомендуемый голос: {analysis['suggested_voice'] or 'недоступен'}")
        
        # Анализ категорий ссылок
        link_categories = analysis['link_categories']
        if link_categories:
            print(f"\n🔗 АНАЛИЗ КАТЕГОРИЙ ССЫЛОК:")
            for category, data in sorted(link_categories.items(), 
                                       key=lambda x: x[1]['score'], reverse=True):
                print(f"   {category}: {data['score']:.1f} баллов")
                print(f"      Совпадения: {', '.join(data['matched_patterns'][:3])}")
        
        # Превью документов
        if analysis['documents_preview']:
            print(f"\n📄 НАЙДЕННЫЕ ДОКУМЕНТЫ:")
            for i, doc in enumerate(analysis['documents_preview'], 1):
                print(f"   {i}. {doc['content_preview']}")
                if doc['metadata']:
                    print(f"      Метаданные: {doc['metadata']}")
    
    def shutdown(self) -> None:
        """Завершение работы"""
        # Показываем статистику сессии
        stats = self.assistant.session_stats
        if stats['queries_processed'] > 0:
            print(f"\n📊 СТАТИСТИКА СЕССИИ:")
            print(f"   Обработано запросов: {stats['queries_processed']}")
            print(f"   Ошибок: {stats['errors_count']}")
            if stats['services_detected']:
                print("   Популярные услуги:")
                for service, count in sorted(stats['services_detected'].items(), 
                                          key=lambda x: x[1], reverse=True):
                    print(f"   - {service}: {count}")
        
        goodbye_msg = "До свидания! Спасибо за использование голосового помощника банка Бакай!"
        print(f"\n👋 {goodbye_msg}")
        
        if self.assistant.tts_enabled and self.assistant.tts.is_initialized:
            self.assistant.tts.speak(goodbye_msg, voice="baya")
            time.sleep(2)  # Даем время для воспроизведения
        
        self.running = False
    
    def run(self) -> None:
        """Основной цикл работы"""
        self.show_welcome()
        
        while self.running:
            try:
                user_input = input("\n💬 Ваш вопрос: ").strip()
                
                if not user_input:
                    continue
                
                # Проверяем, является ли ввод командой
                if self.process_command(user_input):
                    continue
                
                # Обрабатываем как обычный запрос
                print("🔄 Обработка запроса...")
                result = self.assistant.process_query(user_input)
                
                print(f"\n✅ ОТВЕТ:")
                print(result['answer'])
                
                # Показываем дополнительную информацию если запрос был успешным
                if result['processing_success']:
                    if result['service_type']:
                        print(f"\n🎯 Определенная услуга: {result['service_type']}")
                    
                    if result['voice_used']:
                        print(f"🗣️ Использован голос: {result['voice_used']}")
                    
                    # Предлагаем показать источники
                    if result['documents'] and (self.show_sources or len(result['documents']) <= 3):
                        show_docs = input("\n❓ Показать источники? (y/n): ").lower()
                        if show_docs in ('y', 'yes', 'да', 'д'):
                            self.show_document_sources(result['documents'])
                
            except KeyboardInterrupt:
                print("\n\n⏸️ Прерывание работы...")
                self.shutdown()
                break
            except Exception as e:
                print(f"\n❌ Неожиданная ошибка: {e}")
                print("Продолжаем работу...")
    
    def show_document_sources(self, documents) -> None:
        """Показ источников документов"""
        print("\n📄 ИСТОЧНИКИ:")
        print("-" * 50)
        
        for i, doc in enumerate(documents, 1):
            print(f"\n{i}. ДОКУМЕНТ:")
            print(f"   Содержание: {doc.page_content[:200]}...")
            
            if hasattr(doc, 'metadata') and doc.metadata:
                print(f"   Метаданные:")
                for key, value in doc.metadata.items():
                    print(f"   - {key}: {value}")
            
            if i < len(documents):
                print("-" * 30)

# =============================================================================
# ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ТЕСТИРОВАНИЯ
# =============================================================================

def run_quick_test():
    """Быстрый тест основных функций"""
    print("🧪 БЫСТРЫЙ ТЕСТ СИСТЕМЫ")
    print("=" * 30)
    
    try:
        assistant = BakaiAssistant()
        
        # Тест определения услуг
        test_queries = [
            "Как открыть карту?",
            "Нужен кредит на машину",
            "Где ваш офис?"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Тест: '{query}'")
            analysis = assistant.analyze_query(query)
            print(f"   Услуга: {analysis['detected_service'] or 'не определена'}")
            print(f"   Голос: {analysis['suggested_voice'] or 'не выбран'}")
        
        print("\n✅ Быстрый тест завершен")
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")

def show_system_info():
    """Показ информации о системе"""
    print("📋 ИНФОРМАЦИЯ О СИСТЕМЕ")
    print("=" * 40)
    
    try:
        assistant = BakaiAssistant()
        help_info = assistant.get_help_info()
        
        print(f"🏦 Банк: {help_info['bank_info']['name']}")
        print(f"📞 Поддержка: {help_info['contact_info']['phone']}")
        print(f"🌐 Сайт: {help_info['contact_info']['website']}")
        
        print(f"\n🔧 Поддерживаемые услуги:")
        for service in help_info['available_services']:
            print(f"   • {service}")
        
        print(f"\n💻 Голосовые команды:")
        for command in help_info['voice_commands']:
            print(f"   • {command}")
        
    except Exception as e:
        print(f"❌ Ошибка получения информации: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "test":
            run_quick_test()
        elif mode == "info":
            show_system_info()
        elif mode == "help":
            print("📖 РЕЖИМЫ ЗАПУСКА:")
            print("python cli.py       - основной режим")
            print("python cli.py test  - быстрый тест")
            print("python cli.py info  - информация о системе")
            print("python cli.py help  - эта справка")
        else:
            print(f"❌ Неизвестный режим: {mode}")
            print("Используйте 'help' для справки")
    else:
        # Основной режим
        try:
            cli = BakaiCLI()
            cli.run()
        except KeyboardInterrupt:
            print("\n👋 Программа завершена")
        except Exception as e:
            print(f"\n❌ Критическая ошибка: {e}")
            print("Проверьте конфигурацию и зависимости")