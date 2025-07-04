#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Система управления ссылками на страницы банка
"""

from typing import Dict, List, Optional
from langchain.docstore.document import Document
from config import BANK_LINKS

class BakaiLinkManager:
    """Управление ссылками на страницы банка"""
    
    def __init__(self):
        self.link_patterns = self._init_link_patterns()
        self.category_priorities = self._init_category_priorities()
    
    def _init_link_patterns(self) -> Dict[str, List[str]]:
        """Инициализация паттернов для определения нужных ссылок"""
        return {
            "cards": [
                # Основные термины (высокий приоритет)
                "карта", "карту", "карты", "банковская карта", "платежная карта",
                "дебетовая", "кредитная карта", "visa", "mastercard", "элкарт", "elkart",
                # Действия с картами
                "открыть карту", "оформить карту", "заказать карту", "активировать карту",
                # Специфичные термины (средний приоритет)
                "кешбэк", "cashback", "стикер", "платежный стикер", "nfc", "бесконтактная",
                "тумар", "рассрочка", "пин код", "пин-код", "cvv", "cvc"
            ],
            "credits": [
                "кредит", "кредита", "кредиты", "кредитный", "займ", "заем", "ссуда",
                "ипотека", "ипотечный", "автокредит", "авто кредит", "потребительский кредит",
                "кредитование", "кредитный продукт", "взять кредит", "получить кредит",
                "оформить кредит", "ставка кредит", "условия кредит", "процентная ставка",
                "досрочное погашение", "график платежей", "рефинансирование"
            ],
            "deposits": [
                "депозит", "депозита", "депозиты", "депозитный", "вклад", "вклада", "вклады",
                "накопительный", "сберегательный", "срочный вклад", "бессрочный вклад",
                "открыть депозит", "оформить вклад", "процент депозит", "процентная ставка",
                "капитализация", "пополнить депозит", "снять с депозита", "проценты",
                "сберегательный счет", "накопительный счет"
            ],
            "business": [
                "расчетный счет", "расчётный счёт", "р/с", "рс", "расчетка",
                "корпоративный", "бизнес", "юридическое лицо", "юрлицо", "юр лицо",
                "ип", "индивидуальный предприниматель", "предприниматель",
                "счет для бизнеса", "бизнес счет", "корпоративная карта", "корпоративный счет",
                "эквайринг", "pos терминал", "терминал", "инкассация", "инкассо",
                "банк-клиент", "зарплатный проект", "документооборот"
            ],
            "branches": [
                "филиал", "филиала", "филиале", "филиалы", "сберкасса", "сберкассы", "сберкассе",
                "офис", "офиса", "офисе", "офисы", "головной офис", "главный офис", "центральный офис",
                "адрес", "адреса", "адресе", "где находится", "где расположен", "расположение",
                "график работы", "режим работы", "часы работы", "время работы",
                "тыныстанова", "абдрахманова", "бишкек", "местоположение"
            ],
            "atm": [
                "банкомат", "банкомата", "банкоматы", "atm", "атм", "банкомате",
                "снять деньги", "снять наличные", "снятие наличных", "выдача наличных",
                "где банкомат", "ближайший банкомат", "комиссия банкомат", "лимит банкомат",
                "работа банкомата", "банкомат не работает"
            ],
            "insurance": [
                "страхование", "страховка", "страховой", "полис", "страховой продукт",
                "застраховать", "страховая защита", "страховое покрытие",
                "осаго", "каско", "страхование жизни", "медицинская страховка",
                "страховой случай", "страховая выплата"
            ],
            "transfers": [
                "перевод", "переводы", "денежный перевод", "отправить деньги",
                "перечисление", "платеж", "оплата", "перевести деньги", "платежи",
                "быстрый перевод", "международный перевод", "валютный перевод",
                "комиссия перевод", "лимит перевода", "срок перевода"
            ],
            "exchange": [
                "обмен валют", "валюта", "курс", "доллар", "евро", "конвертация",
                "валютный", "обменка", "курс валют", "обменять валюту",
                "покупка валюты", "продажа валюты", "валютные операции",
                "курс доллара", "курс евро", "актуальный курс"
            ],
            "services": [
                "услуга", "услуги", "сервис", "сервисы", "банковские услуги",
                "дополнительные услуги", "тарифы", "тарифный план",
                "комиссия", "комиссии", "условия обслуживания"
            ]
        }
    
    def _init_category_priorities(self) -> Dict[str, int]:
        """Инициализация приоритетов категорий"""
        return {
            "cards": 100,
            "credits": 95,
            "deposits": 90,
            "business": 85,
            "insurance": 80,
            "transfers": 75,
            "exchange": 70,
            "branches": 65,
            "atm": 60,
            "services": 50
        }
    
    def _get_pattern_weight(self, pattern: str, category: str) -> float:
        """Определение веса паттерна в зависимости от его важности"""
        # Основные термины для каждой категории (получают максимальный вес)
        primary_terms = {
            "cards": ["карта", "карту", "карты", "банковская карта", "платежная карта", 
                     "дебетовая", "кредитная карта", "visa", "mastercard", "элкарт"],
            "credits": ["кредит", "кредита", "кредиты", "кредитный", "займ", "ипотека"],
            "deposits": ["депозит", "депозита", "депозиты", "вклад", "вклада", "вклады"],
            "business": ["расчетный счет", "бизнес", "корпоративный", "юридическое лицо", "ип"],
            "branches": ["филиал", "офис", "адрес", "график работы"],
            "atm": ["банкомат", "банкомата", "банкоматы", "atm", "атм"],
            "insurance": ["страхование", "страховка", "полис"],
            "transfers": ["перевод", "переводы", "платеж", "оплата"],
            "exchange": ["обмен валют", "валюта", "курс"],
            "services": ["услуга", "услуги", "сервис"]
        }
        
        # Если это основной термин - высокий вес
        if pattern in primary_terms.get(category, []):
            return 10.0
        
        # Если это составная фраза - средний вес
        if len(pattern.split()) > 1:
            return 3.0
        
        # Остальные термины - базовый вес
        return 1.0
    
    def get_relevant_link(self, query: str, documents: List[Document] = None) -> str:
        """Получение наиболее подходящей ссылки"""
        query_lower = query.lower()
        
        # 1. Проверяем документы на наличие специфичных ссылок
        if documents:
            specific_link = self._extract_link_from_documents(documents, query_lower)
            if specific_link:
                return specific_link
        
        # 2. Определяем категорию по ключевым словам
        category = self._determine_category(query_lower)
        
        # 3. Возвращаем соответствующую ссылку
        link = BANK_LINKS.get(category, BANK_LINKS["general"])
        
        print(f"🔗 Выбрана ссылка для категории '{category}': {link}")
        return link
    
    def _extract_link_from_documents(self, documents: List[Document], query_lower: str) -> Optional[str]:
        """Извлечение специфичной ссылки из документов"""
        for doc in documents:
            if hasattr(doc, 'metadata') and doc.metadata:
                doc_url = doc.metadata.get('url', '')
                
                if doc_url and doc_url.startswith('http'):
                    # Проверяем релевантность URL к запросу
                    if self._is_url_relevant(doc_url, query_lower):
                        print(f"🎯 Найдена специфичная ссылка в документах: {doc_url}")
                        return doc_url
        
        return None
    
    def _is_url_relevant(self, url: str, query_lower: str) -> bool:
        """Проверка релевантности URL к запросу"""
        url_lower = url.lower()
        
        # Словарь соответствий URL и ключевых слов
        url_keywords = {
            'card': ['карт', 'visa', 'mastercard', 'элкарт'],
            'credit': ['кредит', 'займ', 'ипотек'],
            'deposit': ['депозит', 'вклад', 'накопитель'],
            'business': ['бизнес', 'корпоратив', 'предпринимател'],
            'office': ['офис', 'филиал', 'адрес'],
            'insurance': ['страхов', 'полис'],
            'transfer': ['перевод', 'платеж'],
            'exchange': ['валют', 'курс', 'обмен']
        }
        
        for url_pattern, keywords in url_keywords.items():
            if url_pattern in url_lower:
                if any(keyword in query_lower for keyword in keywords):
                    return True
        
        return False
    
    def _determine_category(self, query_lower: str) -> str:
        """Определение категории по ключевым словам запроса"""
        category_scores = {}
        
        # Подсчитываем совпадения для каждой категории
        for category, patterns in self.link_patterns.items():
            score = 0
            matched_patterns = []
            
            for pattern in patterns:
                if pattern in query_lower:
                    # Используем вес паттерна вместо длины фразы
                    pattern_weight = self._get_pattern_weight(pattern, category)
                    
                    # Точное совпадение получает дополнительные баллы
                    exact_bonus = 5 if pattern == query_lower.strip() else 0
                    
                    pattern_score = pattern_weight + exact_bonus
                    score += pattern_score
                    matched_patterns.append((pattern, pattern_score))
            
            if score > 0:
                # Применяем приоритет категории
                priority = self.category_priorities.get(category, 50)
                category_scores[category] = {
                    'score': score * (priority / 100),
                    'raw_score': score,
                    'priority': priority,
                    'patterns': matched_patterns
                }
        
        # Возвращаем категорию с максимальным баллом
        if category_scores:
            best_category = max(category_scores, key=lambda x: category_scores[x]['score'])
            best_score = category_scores[best_category]['score']
            
            print(f"🎯 Определена категория '{best_category}' с баллом {best_score:.1f}")
            print(f"📊 Совпавшие паттерны: {category_scores[best_category]['patterns']}")
            
            return best_category
        
        # По умолчанию - общая страница
        print("🔗 Категория не определена, используем общую ссылку")
        return "general"
    
    def get_category_info(self, category: str) -> Dict[str, any]:
        """Получение информации о категории"""
        category_info = {
            "cards": {
                "name": "Банковские карты",
                "description": "Дебетовые и кредитные карты, стикеры, рассрочка",
                "keywords_count": len(self.link_patterns.get("cards", []))
            },
            "credits": {
                "name": "Кредитование",
                "description": "Потребительские кредиты, ипотека, автокредиты",
                "keywords_count": len(self.link_patterns.get("credits", []))
            },
            "deposits": {
                "name": "Депозиты и вклады",
                "description": "Срочные и накопительные вклады",
                "keywords_count": len(self.link_patterns.get("deposits", []))
            },
            "business": {
                "name": "Бизнес-услуги",
                "description": "Расчетные счета, корпоративные карты, эквайринг",
                "keywords_count": len(self.link_patterns.get("business", []))
            },
            "branches": {
                "name": "Офисы и филиалы",
                "description": "Адреса, график работы, местоположение",
                "keywords_count": len(self.link_patterns.get("branches", []))
            },
            "atm": {
                "name": "Банкоматы",
                "description": "Расположение банкоматов, снятие наличных",
                "keywords_count": len(self.link_patterns.get("atm", []))
            },
            "insurance": {
                "name": "Страхование",
                "description": "Страховые продукты и полисы",
                "keywords_count": len(self.link_patterns.get("insurance", []))
            },
            "transfers": {
                "name": "Переводы и платежи",
                "description": "Денежные переводы, платежные услуги",
                "keywords_count": len(self.link_patterns.get("transfers", []))
            },
            "exchange": {
                "name": "Валютные операции",
                "description": "Обмен валют, актуальные курсы",
                "keywords_count": len(self.link_patterns.get("exchange", []))
            }
        }
        
        return category_info.get(category, {
            "name": "Неизвестная категория",
            "description": "Описание недоступно",
            "keywords_count": 0
        })
    
    def analyze_query_categories(self, query: str) -> Dict[str, float]:
        """Анализ запроса по всем категориям с баллами"""
        query_lower = query.lower()
        analysis = {}
        
        for category, patterns in self.link_patterns.items():
            score = 0
            matched_patterns = []
            
            for pattern in patterns:
                if pattern in query_lower:
                    pattern_weight = self._get_pattern_weight(pattern, category)
                    exact_bonus = 5 if pattern == query_lower.strip() else 0
                    pattern_score = pattern_weight + exact_bonus
                    score += pattern_score
                    matched_patterns.append(pattern)
            
            if score > 0:
                priority = self.category_priorities.get(category, 50)
                final_score = score * (priority / 100)
                
                analysis[category] = {
                    "score": final_score,
                    "raw_score": score,
                    "priority": priority,
                    "matched_patterns": matched_patterns,
                    "link": BANK_LINKS.get(category, BANK_LINKS["general"])
                }
        
        return analysis
    
    def get_all_categories(self) -> List[str]:
        """Получение списка всех доступных категорий"""
        return list(self.link_patterns.keys())
    
    def validate_links(self) -> Dict[str, bool]:
        """Проверка доступности всех ссылок (базовая проверка)"""
        validation_results = {}
        
        for category, url in BANK_LINKS.items():
            # Базовая проверка формата URL
            is_valid = (
                isinstance(url, str) and
                len(url) > 0 and
                (url.startswith('http://') or url.startswith('https://'))
            )
            validation_results[category] = is_valid
        
        return validation_results