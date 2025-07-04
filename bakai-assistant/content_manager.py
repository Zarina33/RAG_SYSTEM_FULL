#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Система управления контентом: вежливость, фильтрация, предложения услуг
"""

import re
import random
from typing import Dict, List, Optional, Set
from config import CONTENT_CONFIG

class BakaiContentManager:
    """Система управления контентом: вежливость, фильтрация, предложения услуг"""
    
    def __init__(self):
        self.forbidden_words = self._init_forbidden_words()
        self.polite_phrases = self._init_polite_phrases()
        self.service_patterns = self._init_service_patterns()
        self.service_offers = self._init_service_offers()
        self.replacements = self._init_replacements()
    
    def _init_forbidden_words(self) -> Set[str]:
        """Инициализация списка запрещенных слов"""
        return {
            # Технические термины ИИ
            'llm', 'language model', 'ai', 'artificial intelligence', 'машинное обучение',
            'neural network', 'нейронная сеть', 'алгоритм', 'токен', 'промпт', 'prompt',
            'vectorstore', 'embeddings', 'chroma', 'ollama', 'langchain', 'gpt', 'chatgpt',
            'модель', 'нейронка', 'искусственный интеллект',
            
            # Неподходящие для банка выражения
            'не знаю', 'понятия не имею', 'без понятия', 'хрен знает', 'фиг знает',
            'черт знает', 'не в курсе', 'ни сном ни духом', 'хз', 'пофиг', 'пофигу',
            'не курю', 'без понятий', 'чёрт знает', 'хрен его знает',
            
            # Сленг и жаргон
            'бабки', 'деньжата', 'капуста', 'лавэ', 'зелень', 'бабло', 'башли',
            'тысяча', 'штука', 'лям', 'косарь', 'рубас', 'бакс', 'евр',
            'нал', 'безнал', 'кэш', 'зарплатка', 'пенсионка',
            
            # Слишком неформальные выражения
            'круто', 'клево', 'прикольно', 'офигеть', 'вау', 'супер', 'мега',
            'ультра', 'топ', 'крутяк', 'прикол', 'классно', 'отпад', 'улёт',
            'зачёт', 'огонь', 'бомба', 'жесть', 'шок', 'жесткач',
            
            # Негативные отзывы о банке
            'плохой банк', 'ужасный банк', 'отвратительный', 'кошмар банк',
            'ужас банк', 'беда банк', 'проблемный банк', 'говённый банк',
            'дерьмовый банк', 'паршивый банк'
        }
    
    def _init_polite_phrases(self) -> Dict[str, List[str]]:
        """Инициализация вежливых фраз"""
        return {
            'greetings': [
                "Благодарю за обращение в банк Бакай! ",
                "Спасибо за ваш вопрос! ",
                "Рад помочь вам! ",
                "С удовольствием отвечу на ваш вопрос! ",
                "Благодарю за доверие к банку Бакай! ",
                "Спасибо, что выбрали наш банк! ",
                "Приветствую! Рад быть полезным! ",
                "Добро пожаловать! Готов помочь! "
            ],
            'endings': [
                " Будем рады помочь вам в любое время!",
                " Обращайтесь, всегда готовы помочь!",
                " Спасибо за выбор банка Бакай!",
                " Рады быть полезными!",
                " С уважением, команда банка Бакай!",
                " Удачного дня и финансового благополучия!",
                " Желаем успехов в ваших финансовых делах!",
                " Ваше финансовое благополучие - наша цель!"
            ]
        }
    
    def _init_service_patterns(self) -> Dict[str, List[str]]:
        """Инициализация паттернов для определения типов услуг"""
        return {
            'cards': [
                'карта', 'карту', 'карты', 'картой', 'карте', 'банковская карта',
                'visa', 'mastercard', 'элкарт', 'elkart', 'платежная карта',
                'дебетовая', 'кредитная карта', 'стикер', 'платежный стикер',
                'nfc', 'бесконтактная', 'кешбэк', 'cashback', 'тумар', 'рассрочка',
                'открыть карту', 'оформить карту', 'заказать карту', 'получить карту',
                'активировать карту', 'пин код', 'пин-код', 'cvv', 'cvc'
            ],
            'credits': [
                'кредит', 'кредита', 'кредите', 'кредиты', 'кредитный', 'займ',
                'ипотека', 'автокредит', 'потребительский кредит', 'кредитование',
                'заем', 'ссуда', 'кредитный продукт', 'взять кредит', 'получить кредит',
                'оформить кредит', 'ставка кредит', 'условия кредит', 'кредитная линия',
                'рефинансирование', 'реструктуризация', 'досрочное погашение'
            ],
            'deposits': [
                'депозит', 'депозита', 'депозите', 'депозиты', 'депозитный',
                'вклад', 'вклада', 'вкладе', 'вклады', 'накопительный', 'сберегательный',
                'срочный вклад', 'открыть депозит', 'оформить вклад', 'процент депозит',
                'капитализация', 'пополнить депозит', 'проценты вклад', 'сберегательный счет'
            ],
            'business': [
                'расчетный счет', 'расчётный счёт', 'р/с', 'рс', 'расчетка',
                'корпоративный', 'бизнес', 'юридическое лицо', 'юрлицо', 'ип',
                'индивидуальный предприниматель', 'предприниматель', 'счет для бизнеса',
                'корпоративная карта', 'эквайринг', 'pos терминал', 'инкассация',
                'документооборот', 'банк-клиент', 'зарплатный проект'
            ],
            'insurance': [
                'страхование', 'страховка', 'страховой', 'полис', 'страховой продукт',
                'застраховать', 'страховая защита', 'страховое покрытие', 'осаго',
                'каско', 'страхование жизни', 'медицинская страховка'
            ],
            'transfers': [
                'перевод', 'переводы', 'денежный перевод', 'отправить деньги',
                'перечисление', 'платеж', 'оплата', 'перевести деньги', 'платежи',
                'быстрый перевод', 'международный перевод', 'валютный перевод'
            ],
            'exchange': [
                'обмен валют', 'валюта', 'курс', 'доллар', 'евро', 'конвертация',
                'валютный', 'обменка', 'курс валют', 'обменять валюту', 'покупка валюты',
                'продажа валюты', 'валютные операции'
            ]
        }
    
    def _init_service_offers(self) -> Dict[str, List[str]]:
        """Инициализация предложений услуг"""
        return {
            'cards': [
                "Хотите, помогу оформить банковскую карту? Это займет всего несколько минут!",
                "Могу помочь с заказом карты. Желаете узнать о доступных вариантах?",
                "Предлагаю оформить карту прямо сейчас. Интересно, какая вам подойдет?",
                "Хотите, чтобы я помог выбрать и оформить подходящую карту?",
                "Готов помочь с выбором оптимальной карты для ваших потребностей!"
            ],
            'credits': [
                "Хотите, помогу оформить кредит? Могу рассчитать условия под ваши потребности!",
                "Могу помочь с получением кредита. Желаете узнать о процентных ставках?",
                "Предлагаю рассмотреть наши кредитные программы. Интересно?",
                "Хотите, чтобы я помог подобрать оптимальный кредитный продукт?",
                "Готов рассчитать индивидуальные условия кредитования!"
            ],
            'deposits': [
                "Хотите, помогу открыть депозит? Могу подобрать выгодные условия!",
                "Могу помочь с оформлением вклада. Желаете узнать о процентных ставках?",
                "Предлагаю открыть депозит для накопления средств. Интересно?",
                "Хотите, чтобы я помог выбрать подходящий депозитный продукт?",
                "Готов подобрать депозит с максимальной доходностью!"
            ],
            'business': [
                "Хотите, помогу открыть расчетный счёт? Это займет всего несколько минут!",
                "Могу помочь с оформлением корпоративного счета. Желаете узнать подробности?",
                "Предлагаю оформить расчетный счёт для вашего бизнеса. Интересно?",
                "Хотите, чтобы я помог с открытием счета для предпринимательской деятельности?",
                "Готов помочь с полным банковским обслуживанием вашего бизнеса!"
            ],
            'insurance': [
                "Хотите, помогу оформить страховку? Могу подобрать подходящий полис!",
                "Могу помочь с выбором страхового продукта. Желаете узнать условия?",
                "Предлагаю рассмотреть наши страховые программы. Интересно?",
                "Хотите, чтобы я помог подобрать оптимальную страховую защиту?",
                "Готов подобрать страховку, которая максимально защитит ваши интересы!"
            ],
            'transfers': [
                "Хотите, помогу оформить денежный перевод? Могу подсказать выгодные тарифы!",
                "Могу помочь с переводом средств. Желаете узнать о комиссиях?",
                "Предлагаю воспользоваться нашими услугами денежных переводов. Интересно?",
                "Хотите, чтобы я помог с быстрым и безопасным переводом?",
                "Готов помочь с переводом по самым выгодным тарифам!"
            ],
            'exchange': [
                "Хотите, помогу с обменом валют? Могу подсказать актуальный курс!",
                "Могу помочь с валютными операциями. Желаете узнать сегодняшние курсы?",
                "Предлагаю воспользоваться выгодным обменом валют. Интересно?",
                "Хотите, чтобы я помог с валютными операциями по лучшему курсу?",
                "Готов помочь с обменом валют по самому выгодному курсу!"
            ]
        }
    
    def _init_replacements(self) -> Dict[str, str]:
        """Инициализация замен для запрещенных слов"""
        return {
            'не знаю': 'уточню для вас',
            'понятия не имею': 'требует дополнительного уточнения',
            'хз': 'уточним',
            'пофиг': 'не имеет значения',
            'бабки': 'денежные средства',
            'лавэ': 'денежные средства',
            'деньжата': 'денежные средства',
            'круто': 'отлично',
            'клево': 'хорошо',
            'супер': 'превосходно',
            # Убираем замену AI - пусть остается как есть в названиях приложений
            # 'ai': 'наша система',
            'llm': 'система обработки',
            'алгоритм': 'наша система',
            'модель': 'система',
            'штука': 'единица',
            'тысяча': 'тысяча рублей'
        }
    
    def filter_content(self, text: str) -> str:
        """Фильтрация запрещенного контента"""
        if not CONTENT_CONFIG.get("enable_filtering", True):
            return text
        
        text_lower = text.lower()
        
        for forbidden in self.forbidden_words:
            if forbidden in text_lower:
                replacement = self.replacements.get(forbidden, 'информация')
                # Заменяем с учетом регистра
                text = re.sub(re.escape(forbidden), replacement, text, flags=re.IGNORECASE)
                print(f"🚫 Заменено: '{forbidden}' → '{replacement}'")
        
        return text
    
    def add_politeness(self, text: str) -> str:
        """Добавление вежливых фраз"""
        if not CONTENT_CONFIG.get("enable_politeness", True):
            return text
        
        # Проверяем, есть ли уже вежливые фразы
        text_lower = text.lower()
        
        has_greeting = any(phrase.strip().lower() in text_lower 
                          for phrase in self.polite_phrases['greetings'])
        
        has_ending = any(phrase.strip().lower() in text_lower 
                        for phrase in self.polite_phrases['endings'])
        
        # Добавляем приветствие
        if not has_greeting:
            greeting = random.choice(self.polite_phrases['greetings'])
            text = greeting + text
        
        # Добавляем окончание
        if not has_ending:
            if not text.endswith(('.', '!', '?')):
                text += '.'
            ending = random.choice(self.polite_phrases['endings'])
            text += ending
        
        return text
    
    def detect_service_type(self, query: str) -> Optional[str]:
        """Определение типа банковской услуги по запросу"""
        query_lower = query.lower()
        service_scores = {}
        
        for service_type, patterns in self.service_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in query_lower:
                    # Длинные фразы получают больше баллов
                    score += len(pattern.split()) * 2 + 1
            
            if score > 0:
                service_scores[service_type] = score
        
        if service_scores:
            best_service = max(service_scores, key=service_scores.get)
            print(f"🎯 Определен тип услуги: {best_service} (балл: {service_scores[best_service]})")
            return best_service
        
        return None
    
    def get_service_offer(self, service_type: str) -> Optional[str]:
        """Получение предложения услуги"""
        offers = self.service_offers.get(service_type, [])
        return random.choice(offers) if offers else None
    
    def enhance_response(self, text: str, query: str) -> str:
        """Полное улучшение ответа: фильтрация + вежливость + предложения"""
        # 1. Фильтруем запрещенный контент
        text = self.filter_content(text)
        
        # 2. Добавляем вежливость
        text = self.add_politeness(text)
        
        # 3. Определяем тип услуги и добавляем предложение
        if CONTENT_CONFIG.get("enable_offers", True):
            service_type = self.detect_service_type(query)
            if service_type:
                offer = self.get_service_offer(service_type)
                if offer:
                    if not text.endswith(('.', '!', '?')):
                        text += '.'
                    text += f"\n\n💡 {offer}"
        
        return text
    
    def validate_response_length(self, text: str) -> bool:
        """Проверка длины ответа"""
        min_length = CONTENT_CONFIG.get("min_answer_length", 10)
        return len(text.strip()) >= min_length
    
    def get_service_statistics(self, queries: List[str]) -> Dict[str, int]:
        """Статистика определения услуг для списка запросов"""
        stats = {}
        for query in queries:
            service_type = self.detect_service_type(query)
            if service_type:
                stats[service_type] = stats.get(service_type, 0) + 1
        return stats