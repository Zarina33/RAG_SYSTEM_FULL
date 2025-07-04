#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py
Главный файл запуска голосового помощника банка Бакай
Версия: 2.0
Автор: AI Assistant for Bakai Bank

Использование:
    python main.py                  - основной режим
    python main.py --test          - тестирование
    python main.py --voice-demo    - демо голосов
    python main.py --info          - информация о системе
    python main.py --validate      - проверка системы
"""

import sys
import os
import argparse
import traceback
from typing import Optional

# Добавляем текущую директорию в путь для импортов
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Проверка наличия всех необходимых зависимостей"""
    required_modules = [
        ('torch', 'PyTorch'),
        ('torchaudio', 'TorchAudio'), 
        ('langchain_community', 'LangChain Community'),
        ('chromadb', 'ChromaDB')
    ]
    
    missing = []
    installed = []
    
    for module, name in required_modules:
        try:
            imported_module = __import__(module)
            version = getattr(imported_module, '__version__', 'неизвестна')
            installed.append(f"{name} (v{version})")
            print(f"✅ {name}: {version}")
        except ImportError as e:
            missing.append(name)
            print(f"❌ {name}: {e}")
    
    if installed:
        print(f"\n📦 УСТАНОВЛЕНО: {len(installed)} пакетов")
        for pkg in installed:
            print(f"   • {pkg}")
    
    if missing:
        print(f"\n❌ ОТСУТСТВУЮТ: {len(missing)} пакетов")
        for name in missing:
            print(f"   • {name}")
        
        print("\n💡 РЕШЕНИЯ:")
        print("1. Убедитесь, что используете правильный Python:")
        print("   which python3")
        print("   python3 --version")
        
        print("\n2. Проверьте виртуальное окружение:")
        print("   source new_rag/bin/activate  # или ваше окружение")
        
        print("\n3. Переустановите пакеты:")
        print("   pip3 install torch torchaudio langchain-community chromadb")
        
        return False
    
    return True

def run_main_mode():
    """Запуск основного режима работы"""
    print("🚀 Запуск основного режима голосового помощника...")
    
    try:
        from cli import BakaiCLI
        cli = BakaiCLI()
        cli.run()
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("💡 Запустим упрощенную версию...")
        run_minimal_mode()
    except KeyboardInterrupt:
        print("\n👋 Работа завершена пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        if "--debug" in sys.argv:
            traceback.print_exc()
        print("💡 Попробуйте упрощенную версию: python main.py --minimal")

def run_minimal_mode():
    """Запуск упрощенного режима без внешних зависимостей"""
    print("🎯 УПРОЩЕННЫЙ РЕЖИМ")
    print("Базовый помощник без TTS и RAG")
    print("=" * 40)
    
    # Базовые ответы
    responses = {
        "карт": "Банк Бакай предлагает карты Visa, MasterCard и ЭлКарт. Для оформления нужен паспорт и справка о доходах.",
        "офис": "Головной офис: г. Бишкек, ул. Тыныстанова 101. Работаем пн-пт 9:00-18:00.",
        "кредит": "Предлагаем потребительские кредиты, ипотеку, автокредиты. Нужны: паспорт, справки о доходах и работе.",
        "депозит": "Депозиты в сомах и долларах от 8% до 12% годовых. Минимум 1000 сом.",
        "счет": "Для расчетного счета ИП нужны: свидетельство регистрации, паспорт, справка из налоговой."
    }
    
    print("Задайте вопрос или 'выход' для завершения:")
    
    while True:
        try:
            query = input("\n💬 Ваш вопрос: ").strip()
            
            if query.lower() in ['выход', 'exit', 'quit']:
                print("👋 До свидания!")
                break
            
            if not query:
                continue
            
            # Поиск ответа
            query_lower = query.lower()
            answer = None
            
            for key, response in responses.items():
                if key in query_lower:
                    answer = f"Спасибо за обращение! {response}\n\nПодробности: https://bakai.kg"
                    break
            
            if not answer:
                answer = "Спасибо за вопрос! Обратитесь в офис по адресу ул. Тыныстанова 101 или на сайт bakai.kg"
            
            print(f"\n✅ ОТВЕТ:\n{answer}")
            
        except KeyboardInterrupt:
            print("\n👋 До свидания!")
            break

def run_test_mode():
    """Запуск режима тестирования"""
    print("🧪 РЕЖИМ ТЕСТИРОВАНИЯ")
    print("=" * 40)
    
    try:
        print("1. Проверка импортов...")
        success = check_dependencies()
        
        if not success:
            print("\n⚠️ Некоторые зависимости отсутствуют")
            print("Запуск базовых тестов...")
            
            # Базовые тесты Python
            print("\n🐍 ТЕСТ PYTHON:")
            print(f"   Версия: {sys.version}")
            print(f"   Путь: {sys.executable}")
            
            # Тест файловой системы
            print("\n📁 ТЕСТ ФАЙЛОВОЙ СИСТЕМЫ:")
            test_files = ['config.py', 'tts_system.py', 'content_manager.py']
            for file in test_files:
                if os.path.exists(file):
                    print(f"   ✅ {file}")
                else:
                    print(f"   ❌ {file}")
            
            return
        
        print("\n2. Тест инициализации компонентов...")
        
        try:
            from assistant import BakaiAssistant
            assistant = BakaiAssistant()
            print("✅ Основной помощник инициализирован")
            
            # Проверка статуса
            status = assistant.get_system_status()
            print(f"✅ TTS: {'готов' if status['tts_available'] else 'недоступен'}")
            print(f"✅ RAG: {'готов' if status['database_ready'] else 'недоступен'}")
            
            # Тест простого запроса
            print("\n3. Тест обработки запроса...")
            result = assistant.process_query("Привет")
            print(f"✅ Запрос обработан: {result['processing_success']}")
            
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
        
        print("\n✅ Тестирование завершено")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        if "--debug" in sys.argv:
            traceback.print_exc()

def run_voice_demo():
    """Демонстрация голосов"""
    print("🗣️ ДЕМОНСТРАЦИЯ ГОЛОСОВ")
    print("=" * 30)
    
    try:
        from tts_system import BakaiTTS
        
        tts = BakaiTTS()
        
        if not tts.is_initialized:
            print("❌ TTS система недоступна")
            print("\nВозможные причины:")
            print("• Отсутствие интернет-соединения")
            print("• Проблемы с PyTorch")
            print("• Недостаточно места на диске")
            return
        
        voices = tts.get_available_voices()
        print(f"🎭 Доступно голосов: {len(voices)}")
        
        demo_text = "Добро пожаловать в банк Бакай!"
        
        for voice in voices:
            print(f"\n🔊 Тест голоса: {voice}")
            result = tts.speak(demo_text, voice=voice)
            
            if result:
                print(f"✅ Создан файл: {result}")
            else:
                print("❌ Ошибка генерации")
            
            input("Нажмите Enter для следующего...")
        
        print("\n✅ Демонстрация завершена")
        
    except ImportError:
        print("❌ Модуль TTS недоступен")
        print("Установите: pip install torch torchaudio")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def show_system_info():
    """Показ информации о системе"""
    print("📋 ИНФОРМАЦИЯ О СИСТЕМЕ")
    print("=" * 40)
    
    # Информация о Python
    print(f"🐍 PYTHON:")
    print(f"   Версия: {sys.version}")
    print(f"   Исполняемый файл: {sys.executable}")
    print(f"   Платформа: {sys.platform}")
    
    # Информация о виртуальном окружении
    print(f"\n🔧 ОКРУЖЕНИЕ:")
    venv = os.environ.get('VIRTUAL_ENV')
    if venv:
        print(f"   Виртуальное окружение: {venv}")
    else:
        print("   Виртуальное окружение: не активировано")
    
    # Проверка файлов проекта
    print(f"\n📁 ФАЙЛЫ ПРОЕКТА:")
    project_files = [
        'config.py', 'tts_system.py', 'content_manager.py', 
        'rag_system.py', 'link_manager.py', 'assistant.py', 'cli.py'
    ]
    
    for file in project_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"   ✅ {file} ({size} байт)")
        else:
            print(f"   ❌ {file}")
    
    # Проверка зависимостей
    print(f"\n📦 ЗАВИСИМОСТИ:")
    check_dependencies()

def run_validation():
    """Комплексная проверка системы"""
    print("🔍 КОМПЛЕКСНАЯ ПРОВЕРКА СИСТЕМЫ")
    print("=" * 50)
    
    try:
        # 1. Системная информация
        print("1. Системная информация...")
        show_system_info()
        
        # 2. Проверка зависимостей
        print(f"\n2. Проверка зависимостей...")
        deps_ok = check_dependencies()
        
        if not deps_ok:
            print("\n❌ ПРОБЛЕМЫ С ЗАВИСИМОСТЯМИ")
            print("Исправьте их перед продолжением")
            return
        
        # 3. Инициализация компонентов
        print(f"\n3. Инициализация компонентов...")
        from assistant import BakaiAssistant
        
        assistant = BakaiAssistant()
        validation = assistant.validate_system()
        
        # 4. Отчет о валидации
        print(f"\n4. Результаты валидации...")
        
        components = [
            ("TTS", validation["tts_system"]["test_passed"]),
            ("RAG", validation["rag_system"]["database_ready"]),
            ("База данных", validation["rag_system"]["documents_count"] > 0),
            ("LLM", validation["rag_system"]["llm_ready"])
        ]
        
        for name, status in components:
            icon = "✅" if status else "❌"
            print(f"   {icon} {name}")
        
        overall = "✅ ГОТОВ" if validation["overall_ready"] else "⚠️ ТРЕБУЕТ НАСТРОЙКИ"
        print(f"\n🎯 ОБЩЕЕ СОСТОЯНИЕ: {overall}")
        
        if not validation["overall_ready"]:
            print(f"\n💡 РЕКОМЕНДАЦИИ:")
            if not validation["tts_system"]["test_passed"]:
                print("   • Проверьте интернет для загрузки TTS")
            if validation["rag_system"]["documents_count"] == 0:
                print("   • Добавьте документы в базу знаний")
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Запустите: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Ошибка валидации: {e}")
        if "--debug" in sys.argv:
            traceback.print_exc()

def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description="Голосовой помощник банка Бакай",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main.py                  # Основной режим
  python main.py --test          # Тестирование системы  
  python main.py --voice-demo    # Демонстрация голосов
  python main.py --info          # Информация о системе
  python main.py --validate      # Проверка всех компонентов
  python main.py --minimal       # Упрощенный режим
  python main.py --debug --test  # Тест с подробной отладкой
        """
    )
    
    parser.add_argument('--test', action='store_true', 
                       help='Запуск режима тестирования')
    parser.add_argument('--voice-demo', action='store_true',
                       help='Демонстрация голосов TTS')
    parser.add_argument('--info', action='store_true',
                       help='Показать информацию о системе')
    parser.add_argument('--validate', action='store_true',
                       help='Комплексная проверка системы')
    parser.add_argument('--minimal', action='store_true',
                       help='Упрощенный режим без зависимостей')
    parser.add_argument('--debug', action='store_true',
                       help='Включить подробную отладку')
    
    args = parser.parse_args()
    
    try:
        # Выбираем режим работы
        if args.minimal:
            run_minimal_mode()
        elif args.test:
            run_test_mode()
        elif args.voice_demo:
            run_voice_demo()
        elif args.info:
            show_system_info()
        elif args.validate:
            run_validation()
        else:
            # Основной режим
            run_main_mode()
            
    except KeyboardInterrupt:
        print("\n👋 Программа завершена пользователем")
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        if args.debug:
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

def run_main_mode():
    """Запуск основного режима работы"""
    print("🚀 Запуск основного режима голосового помощника...")
    
    try:
        from cli import BakaiCLI
        cli = BakaiCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n👋 Работа завершена пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        if "--debug" in sys.argv:
            traceback.print_exc()
        print("Проверьте конфигурацию и попробуйте снова")

def run_test_mode():
    """Запуск режима тестирования"""
    print("🧪 РЕЖИМ ТЕСТИРОВАНИЯ")
    print("=" * 40)
    
    try:
        from assistant import BakaiAssistant
        
        print("1. Инициализация системы...")
        assistant = BakaiAssistant()
        
        print("2. Проверка компонентов...")
        validation = assistant.validate_system()
        
        # Отчет о валидации
        print("\n📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ:")
        components = [
            ("TTS система", validation["tts_system"]["test_passed"]),
            ("RAG система", validation["rag_system"]["database_ready"]),
            ("База данных", validation["rag_system"]["documents_count"] > 0),
            ("LLM модель", validation["rag_system"]["llm_ready"])
        ]
        
        for name, status in components:
            icon = "✅" if status else "❌"
            print(f"   {icon} {name}")
        
        print(f"\n🎯 Общая готовность: {'✅ Готов' if validation['overall_ready'] else '❌ Требует настройки'}")
        
        # Тест обработки запроса
        if validation['overall_ready']:
            print("\n3. Тест обработки запроса...")
            test_queries = [
                "Как открыть карту?",
                "Где ваш офис?",
                "Условия кредитования"
            ]
            
            for query in test_queries:
                print(f"\n   🔍 Тест: '{query}'")
                try:
                    result = assistant.process_query(query)
                    if result["processing_success"]:
                        print(f"   ✅ Успешно (найдено {result['documents_found']} документов)")
                        if result['service_type']:
                            print(f"   🎯 Услуга: {result['service_type']}")
                    else:
                        print(f"   ❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")
                except Exception as e:
                    print(f"   ❌ Исключение: {e}")
        
        print("\n✅ Тестирование завершено")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        if "--debug" in sys.argv:
            traceback.print_exc()

def run_voice_demo():
    """Демонстрация голосов"""
    print("🗣️ ДЕМОНСТРАЦИЯ ГОЛОСОВ")
    print("=" * 30)
    
    try:
        from tts_system import BakaiTTS
        
        tts = BakaiTTS()
        
        if not tts.is_initialized:
            print("❌ TTS система недоступна")
            print("Возможные причины:")
            print("• Отсутствие интернет-соединения для загрузки модели")
            print("• Недостаточно места на диске")
            print("• Проблемы с PyTorch")
            return
        
        voices = tts.get_available_voices()
        voice_info = tts.get_voice_info()
        
        print(f"Доступно голосов: {len(voices)}")
        
        for voice in voices:
            info = voice_info.get(voice, {})
            print(f"\n🔊 Голос: {voice}")
            print(f"   Тип: {info.get('gender', 'неизвестно')}")
            print(f"   Описание: {info.get('description', 'Описание недоступно')}")
            
            # Демонстрация
            demo_text = f"Привет! Меня зовут {voice}. Добро пожаловать в банк Бакай!"
            print("   🎵 Воспроизведение...")
            
            result = tts.speak(demo_text, voice=voice)
            if result:
                print(f"   ✅ Аудио сохранено: {result}")
            else:
                print("   ❌ Ошибка воспроизведения")
            
            input("   Нажмите Enter для следующего голоса...")
        
        print("\n✅ Демонстрация завершена")
        
    except Exception as e:
        print(f"❌ Ошибка демонстрации: {e}")
        if "--debug" in sys.argv:
            traceback.print_exc()

def show_system_info():
    """Показ информации о системе"""
    print("📋 ИНФОРМАЦИЯ О СИСТЕМЕ")
    print("=" * 40)
    
    try:
        from assistant import BakaiAssistant
        from config import BANK_CONFIG, RAG_CONFIG, TTS_CONFIG
        
        assistant = BakaiAssistant()
        status = assistant.get_system_status()
        help_info = assistant.get_help_info()
        
        # Информация о банке
        print("🏦 БАНК:")
        print(f"   Название: {BANK_CONFIG['name']}")
        print(f"   Сайт: {BANK_CONFIG['website']}")
        print(f"   Поддержка: {BANK_CONFIG['support_phone']}")
        print(f"   Главный офис: {BANK_CONFIG['main_office']}")
        
        # Конфигурация
        print(f"\n⚙️ КОНФИГУРАЦИЯ:")
        print(f"   LLM модель: {RAG_CONFIG['llm_model']}")
        print(f"   Embedding модель: {RAG_CONFIG['embedding_model']}")
        print(f"   TTS голос по умолчанию: {TTS_CONFIG['default_voice']}")
        print(f"   База знаний: {RAG_CONFIG['chroma_db_path']}")
        
        # Статистика
        if status['database_ready']:
            db_stats = status['database_stats']
            print(f"\n📊 БАЗА ЗНАНИЙ:")
            print(f"   Документов: {db_stats.get('total_documents', 0)}")
            print(f"   Средний размер: {db_stats.get('avg_document_length', 0):.0f} символов")
        
        # Возможности
        print(f"\n🔧 ВОЗМОЖНОСТИ:")
        print(f"   Озвучивание: {'✅' if status['tts_available'] else '❌'}")
        print(f"   Голосов доступно: {len(status['available_voices'])}")
        print(f"   Типов услуг: {len(help_info['available_services'])}")
        print(f"   Фильтрация контента: ✅")
        print(f"   Умные предложения: ✅")
        print(f"   Система вежливости: ✅")
        
        # Поддерживаемые услуги
        print(f"\n🏪 ПОДДЕРЖИВАЕМЫЕ УСЛУГИ:")
        for service in help_info['available_services']:
            print(f"   • {service}")
        
    except Exception as e:
        print(f"❌ Ошибка получения информации: {e}")
        if "--debug" in sys.argv:
            traceback.print_exc()

def run_validation():
    """Комплексная проверка системы"""
    print("🔍 КОМПЛЕКСНАЯ ПРОВЕРКА СИСТЕМЫ")
    print("=" * 50)
    
    try:
        from assistant import BakaiAssistant
        
        print("1. Инициализация...")
        assistant = BakaiAssistant()
        
        print("2. Запуск валидации...")
        validation = assistant.validate_system()
        
        print("\n📊 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
        
        # TTS система
        tts = validation["tts_system"]
        print(f"\n🔊 TTS СИСТЕМА:")
        print(f"   Инициализирована: {'✅' if tts['initialized'] else '❌'}")
        print(f"   Голосов доступно: {tts['voices_available']}")
        print(f"   Тест пройден: {'✅' if tts['test_passed'] else '❌'}")
        
        # RAG система
        rag = validation["rag_system"]
        print(f"\n🧠 RAG СИСТЕМА:")
        print(f"   База данных: {'✅' if rag['database_ready'] else '❌'}")
        print(f"   LLM модель: {'✅' if rag['llm_ready'] else '❌'}")
        print(f"   Документов: {rag['documents_count']}")
        
        # Контент система
        content = validation["content_system"]
        print(f"\n📝 КОНТЕНТ СИСТЕМА:")
        print(f"   Запрещенных слов: {content['forbidden_words_count']}")
        print(f"   Типов услуг: {content['service_types_count']}")
        print(f"   Вежливых фраз: {content['polite_phrases_count']}")
        
        # Система ссылок
        links = validation["link_system"]
        print(f"\n🔗 СИСТЕМА ССЫЛОК:")
        print(f"   Категорий: {links['categories_count']}")
        
        valid_links = sum(1 for valid in links['links_valid'].values() if valid)
        total_links = len(links['links_valid'])
        print(f"   Валидных ссылок: {valid_links}/{total_links}")
        
        # Общая оценка
        print(f"\n🎯 ОБЩАЯ ОЦЕНКА:")
        if validation["overall_ready"]:
            print("   ✅ Система полностью готова к работе")
        else:
            print(f"   ⚠️ Критических проблем: {validation['critical_issues']}")
            print("   Система требует дополнительной настройки")
        
        # Рекомендации
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        if not tts['initialized']:
            print("   • Проверьте интернет-соединение для загрузки TTS модели")
        if rag['documents_count'] == 0:
            print("   • Загрузите документы в базу знаний")
        if rag['documents_count'] < 10:
            print("   • Добавьте больше документов для лучшего качества ответов")
        if not validation["overall_ready"]:
            print("   • Исправьте критические проблемы перед использованием")
        
    except Exception as e:
        print(f"❌ Ошибка валидации: {e}")
        if "--debug" in sys.argv:
            traceback.print_exc()

def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description="Голосовой помощник банка Бакай",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main.py                  # Основной режим
  python main.py --test          # Тестирование системы  
  python main.py --voice-demo    # Демонстрация голосов
  python main.py --info          # Информация о системе
  python main.py --validate      # Проверка всех компонентов
  python main.py --debug --test  # Тест с подробной отладкой
        """
    )
    
    parser.add_argument('--test', action='store_true', 
                       help='Запуск режима тестирования')
    parser.add_argument('--voice-demo', action='store_true',
                       help='Демонстрация голосов TTS')
    parser.add_argument('--info', action='store_true',
                       help='Показать информацию о системе')
    parser.add_argument('--validate', action='store_true',
                       help='Комплексная проверка системы')
    parser.add_argument('--debug', action='store_true',
                       help='Включить подробную отладку')
    
    args = parser.parse_args()
    
    # Проверяем зависимости
    if not check_dependencies():
        sys.exit(1)
    
    try:
        # Выбираем режим работы
        if args.test:
            run_test_mode()
        elif args.voice_demo:
            run_voice_demo()
        elif args.info:
            show_system_info()
        elif args.validate:
            run_validation()
        else:
            # Основной режим
            run_main_mode()
            
    except KeyboardInterrupt:
        print("\n👋 Программа завершена пользователем")
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        if args.debug:
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()