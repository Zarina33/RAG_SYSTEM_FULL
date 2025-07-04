#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rag_system.py
Система RAG с точным совпадением для банка Бакай
"""

import re
from typing import List, Dict, Optional, Tuple
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain.docstore.document import Document
from config import RAG_CONFIG
from difflib import SequenceMatcher

class BakaiRAG:
    """Система поиска и генерации ответов для банка Бакай с точным совпадением"""
    
    def __init__(self):
        self.vectorstore = None
        self.llm = None
        self.embeddings = None
        self.document_count = 0
        self.faq_database = {}  # Кэш для точных FAQ
        self._last_search_type = 'no_exact_match'
        self._init_components()
    
    def _init_components(self) -> None:
        """Инициализация компонентов RAG системы"""
        try:
            print("🔍 Инициализация RAG системы...")
            
            # Инициализация эмбеддингов
            self.embeddings = OllamaEmbeddings(model=RAG_CONFIG["embedding_model"])
            
            # Инициализация векторного хранилища
            self.vectorstore = Chroma(
                persist_directory=RAG_CONFIG["chroma_db_path"],
                embedding_function=self.embeddings
            )
            
            # Инициализация LLM
            self.llm = ChatOllama(
                model=RAG_CONFIG["llm_model"],
                temperature=RAG_CONFIG["temperature"],
                num_predict=RAG_CONFIG["max_tokens"],
                top_p=RAG_CONFIG["top_p"],
                repeat_penalty=RAG_CONFIG["repeat_penalty"]
            )
            
            print("✅ RAG система инициализирована")
            self._validate_database()
            self._build_faq_index()
            
        except Exception as e:
            print(f"❌ Ошибка инициализации RAG: {e}")
            raise
    
    def _validate_database(self) -> None:
        """Проверка состояния базы данных"""
        try:
            collection = self.vectorstore._collection.get()
            self.document_count = len(collection.get('documents', []))
            print(f"📊 База знаний содержит {self.document_count} документов")
            
            if self.document_count == 0:
                print("⚠️ База знаний пуста. Необходимо загрузить документы.")
            elif self.document_count < 10:
                print("⚠️ Мало документов в базе. Рекомендуется добавить больше контента.")
            
        except Exception as e:
            print(f"⚠️ Не удалось проверить базу данных: {e}")
    
    def _build_faq_index(self) -> None:
        """Построение индекса FAQ для точного совпадения"""
        try:
            collection = self.vectorstore._collection.get()
            documents = collection.get('documents', [])
            metadatas = collection.get('metadatas', [])
            
            for doc, metadata in zip(documents, metadatas):
                # Ищем FAQ структуру
                if 'FAQ:' in doc:
                    # Извлекаем вопрос и ответ
                    faq_match = re.search(r'FAQ:\s*(.+?)\?\s*\n?Ответ:\s*(.+)', doc, re.DOTALL)
                    if faq_match:
                        question = faq_match.group(1).strip()
                        answer = faq_match.group(2).strip()
                        
                        # Нормализуем вопрос для поиска
                        normalized_question = self._normalize_question(question)
                        
                        self.faq_database[normalized_question] = {
                            'original_question': question,
                            'answer': answer,
                            'full_content': doc,
                            'metadata': metadata
                        }
                        
                        print(f"📝 Индексирован FAQ: {question[:50]}...")
            
            print(f"✅ Проиндексировано {len(self.faq_database)} FAQ записей")
            
        except Exception as e:
            print(f"⚠️ Не удалось построить индекс FAQ: {e}")
    
    def _normalize_question(self, question: str) -> str:
        """Нормализация вопроса для точного поиска"""
        # Убираем лишние пробелы, знаки препинания
        normalized = re.sub(r'\s+', ' ', question.strip())
        normalized = re.sub(r'[^\w\s]', '', normalized)
        
        # Приводим к нижнему регистру
        normalized = normalized.lower()
        
        return normalized
    
    def search_documents(self, query: str, k: int = None) -> List[Document]:
        """Поиск документов (совместимость с существующим кодом)"""
        documents, search_type = self.search_documents_with_type(query, k)
        
        # Сохраняем тип поиска для использования в generate_answer
        self._last_search_type = search_type
        
        return documents
    
    def search_documents_with_type(self, query: str, k: int = None) -> Tuple[List[Document], str]:
        """Поиск: сначала точное совпадение, иначе - обычный поиск"""
        if k is None:
            k = RAG_CONFIG["search_k"]
        
        try:
            print(f"🔍 Поиск для запроса: '{query}'")
            
            # Шаг 1: Проверяем точное совпадение в FAQ
            exact_match = self._find_exact_faq_match(query)
            if exact_match:
                print("✅ Найдено ТОЧНОЕ совпадение в FAQ")
                doc = Document(
                    page_content=exact_match['full_content'],
                    metadata=exact_match['metadata'] or {}
                )
                return [doc], 'exact_match'
            
            # Шаг 2: Нет точного совпадения - обычный поиск
            print("🔍 Точного совпадения нет - выполняем обычный поиск...")
            
            # Комбинируем: сначала похожие FAQ, потом векторный поиск
            all_docs = []
            
            # Ищем похожие вопросы с низким порогом
            similar_matches = self._find_similar_faq_matches(query, threshold=0.6)
            if similar_matches:
                print(f"📋 Найдено {len(similar_matches)} похожих FAQ")
                for match in similar_matches:
                    doc = Document(
                        page_content=match['full_content'],
                        metadata=match['metadata'] or {}
                    )
                    all_docs.append(doc)
            
            # Добавляем результаты векторного поиска
            vector_results = self._enhanced_vector_search(query, k)
            all_docs.extend(vector_results)
            
            # Убираем дубликаты
            unique_docs = []
            seen_content = set()
            for doc in all_docs:
                if doc.page_content not in seen_content:
                    unique_docs.append(doc)
                    seen_content.add(doc.page_content)
            
            return unique_docs[:k], 'no_exact_match'
            
        except Exception as e:
            print(f"❌ Ошибка поиска документов: {e}")
            return [], 'error'
    
    def _find_exact_faq_match(self, query: str) -> Optional[Dict]:
        """Поиск ТОЧНОГО совпадения в FAQ"""
        
        # Очищаем запрос от номеров и лишних символов
        clean_query = re.sub(r'^\d+\.\s*', '', query.strip())
        clean_query = re.sub(r'\s+', ' ', clean_query)
        
        print(f"🔍 Ищем точное совпадение для: '{clean_query}'")
        
        # Проверяем каждый FAQ на точное совпадение
        for normalized_faq, faq_data in self.faq_database.items():
            original_question = faq_data['original_question']
            
            # Убираем лишние символы из оригинального вопроса
            clean_original = re.sub(r'\s+', ' ', original_question.strip())
            
            # Проверяем точное совпадение (игнорируя регистр)
            if clean_query.lower() == clean_original.lower():
                print(f"✅ ТОЧНОЕ СОВПАДЕНИЕ найдено!")
                print(f"   Вопрос: {original_question}")
                print(f"   Ответ: {faq_data['answer'][:100]}...")
                return faq_data
            
            # Дополнительная проверка: очень высокое сходство (>95%)
            similarity = SequenceMatcher(None, clean_query.lower(), clean_original.lower()).ratio()
            if similarity > 0.95:
                print(f"✅ ПРАКТИЧЕСКИ ТОЧНОЕ СОВПАДЕНИЕ найдено (сходство: {similarity:.2f})!")
                print(f"   Вопрос: {original_question}")
                print(f"   Ответ: {faq_data['answer'][:100]}...")
                return faq_data
        
        print("❌ Точное совпадение не найдено")
        return None
    
    def _find_similar_faq_matches(self, query: str, threshold: float = 0.7) -> List[Dict]:
        """Поиск похожих FAQ с оценкой сходства"""
        normalized_query = self._normalize_question(query)
        
        similar_matches = []
        
        for faq_question, faq_data in self.faq_database.items():
            # Вычисляем сходство
            similarity = SequenceMatcher(None, normalized_query, faq_question).ratio()
            
            if similarity >= threshold:
                similar_matches.append({
                    'similarity': similarity,
                    'original_question': faq_data['original_question'],
                    'answer': faq_data['answer'],
                    'full_content': faq_data['full_content'],
                    'metadata': faq_data['metadata']
                })
                print(f"   📋 Похожий вопрос (сходство: {similarity:.2f}): {faq_data['original_question']}")
        
        # Сортируем по сходству
        similar_matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similar_matches
    
    def _enhanced_vector_search(self, query: str, k: int) -> List[Document]:
        """Улучшенный векторный поиск с проверкой ключевых слов"""
        try:
            # Сначала пробуем прямой поиск по ключевым словам в документах
            keyword_results = self._keyword_search_in_documents(query)
            if keyword_results:
                print(f"🎯 Найдено {len(keyword_results)} документов по ключевым словам")
                return keyword_results[:k]
            
            # Если не нашли по ключевым словам, используем векторный поиск
            query_variants = self._generate_query_variants(query)
            
            all_results = []
            
            for variant in query_variants:
                try:
                    results = self.vectorstore.similarity_search_with_score(variant, k=k*2)
                    all_results.extend(results)
                    print(f"   🔍 '{variant[:40]}...' → {len(results)} результатов")
                except Exception as e:
                    print(f"⚠️ Ошибка векторного поиска для '{variant}': {e}")
            
            # Убираем дубликаты и сортируем
            unique_docs = {}
            for doc, score in all_results:
                doc_text = doc.page_content
                if doc_text not in unique_docs or unique_docs[doc_text][1] > score:
                    unique_docs[doc_text] = (doc, score)
            
            sorted_results = sorted(unique_docs.values(), key=lambda x: x[1])
            final_docs = [doc for doc, _ in sorted_results[:k]]
            
            return final_docs
            
        except Exception as e:
            print(f"⚠️ Ошибка расширенного векторного поиска: {e}")
            return []
    
    def _keyword_search_in_documents(self, query: str) -> List[Document]:
        """Поиск по ключевым словам в содержимом документов"""
        try:
            collection = self.vectorstore._collection.get()
            documents = collection.get('documents', [])
            metadatas = collection.get('metadatas', [])
            
            query_lower = query.lower()
            
            # Извлекаем ключевые слова из запроса
            keywords = self._extract_keywords(query_lower)
            
            if not keywords:
                return []
            
            matches = []
            
            for doc, metadata in zip(documents, metadatas):
                doc_lower = doc.lower()
                
                # Подсчитываем совпадения ключевых слов
                match_score = 0
                matched_keywords = []
                
                for keyword in keywords:
                    if keyword in doc_lower:
                        match_score += 1
                        matched_keywords.append(keyword)
                
                # Если есть совпадения, добавляем документ
                if match_score > 0:
                    matches.append({
                        'document': Document(page_content=doc, metadata=metadata or {}),
                        'score': match_score,
                        'keywords': matched_keywords,
                        'content_preview': doc[:100] + '...'
                    })
            
            # Сортируем по количеству совпадений
            matches.sort(key=lambda x: x['score'], reverse=True)
            
            # Показываем найденные документы
            for match in matches[:3]:  # Показываем топ-3
                print(f"   📄 Найден документ (совпадений: {match['score']}):")
                print(f"      Ключевые слова: {match['keywords']}")
                print(f"      Превью: {match['content_preview']}")
            
            return [match['document'] for match in matches]
            
        except Exception as e:
            print(f"⚠️ Ошибка поиска по ключевым словам: {e}")
            return []
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Извлечение ключевых слов из запроса"""
        # Удаляем стоп-слова и извлекаем значимые слова
        stop_words = {
            'ли', 'предоставляет', 'банк', 'бакай', 'услуги', 'ваш', 'наш', 'это', 'что', 'как',
            'где', 'когда', 'почему', 'какой', 'какая', 'какие', 'или', 'и', 'в', 'на', 'с', 'для'
        }
        
        # Разбиваем на слова и убираем знаки препинания
        words = re.findall(r'\b\w+\b', query.lower())
        
        # Фильтруем стоп-слова
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Добавляем специальные комбинации
        special_combinations = {
            'сейфовых ячеек': ['сейфов', 'ячеек', 'сейфовых', 'депозитных'],
            'депозитных ячеек': ['депозитных', 'ячеек', 'сейфовых'],
            'банковских ячеек': ['банковских', 'ячеек', 'сейфовых']
        }
        
        query_text = query.lower()
        for phrase, related_words in special_combinations.items():
            if any(word in query_text for word in phrase.split()):
                keywords.extend(related_words)
        
        return list(set(keywords))  # Убираем дубликаты
    
    def _generate_query_variants(self, query: str) -> List[str]:
        """Генерация вариантов запроса с улучшенными синонимами"""
        variants = [query, query.lower()]
        
        # Убираем номера вопросов
        clean_query = re.sub(r'^\d+\.\s*', '', query.strip())
        variants.append(clean_query)
        variants.append(clean_query.lower())
        
        # Расширенные синонимы
        replacements = {
            'сейфовых ячеек': ['депозитных ячеек', 'банковских ячеек', 'сейфов', 'ячеек для хранения'],
            'аренды': ['аренда', 'прокат', 'предоставление', 'услуг'],
            'предоставляет': ['предлагает', 'есть', 'имеет', 'оказывает'],
            'услуги': ['сервис', 'предложения', 'возможности'],
            'перевести': ['отправить', 'переслать', 'сделать перевод'],
            'карту': ['карточку', 'пластик'],
            'SWIFT': ['свифт', 'swift перевод', 'международный перевод'],
            'как': ['способ', 'каким образом'],
            'где': ['адрес', 'местоположение'],
            'документы': ['справки', 'бумаги', 'требования'],
            'лимиты': ['ограничения', 'пределы', 'максимум'],
            'валютные': ['валютных', 'обменных', 'currency']
        }
        
        query_lower = query.lower()
        for original, alternatives in replacements.items():
            if original in query_lower:
                for alt in alternatives:
                    new_variant = query_lower.replace(original, alt)
                    variants.append(new_variant)
        
        # Добавляем простые ключевые слова
        if 'сейф' in query_lower:
            variants.extend([
                'сейфовые ячейки',
                'банковские ячейки',
                'индивидуальные сейфовые ячейки',
                'хранение ценностей'
            ])
        
        return list(dict.fromkeys(variants))[:8]  # Уникальные варианты
    
    def generate_answer(self, query: str, documents: List[Document], search_type: str = None) -> str:
        """Генерация ответа: прямой ответ при точном совпадении, генерация - при отсутствии"""
        
        # Если search_type не передан, используем сохраненный тип
        if search_type is None:
            search_type = getattr(self, '_last_search_type', 'no_exact_match')
        
        try:
            if not documents:
                return "К сожалению, не найдено информации по вашему запросу. Обратитесь в офис банка для получения точной информации."
            
            # Если найдено точное совпадение - возвращаем прямой ответ БЕЗ генерации
            if search_type == 'exact_match':
                print("✅ Точное совпадение - возвращаем прямой ответ БЕЗ генерации")
                return self._extract_direct_answer(documents[0])
            
            # Во всех остальных случаях - генерируем ответ на основе найденных данных
            else:
                print("🤖 Нет точного совпадения - генерируем ответ на основе найденных данных")
                return self._generate_contextual_answer(query, documents)
            
        except Exception as e:
            print(f"❌ Ошибка генерации ответа: {e}")
            return "Произошла техническая ошибка при формировании ответа. Обратитесь к консультанту."
    
    def _extract_direct_answer(self, document: Document) -> str:
        """Извлечение прямого ответа из FAQ БЕЗ генерации"""
        content = document.page_content
        
        # Извлекаем ответ из FAQ структуры
        faq_match = re.search(r'FAQ:\s*(.+?)\?\s*\n?Ответ:\s*(.+)', content, re.DOTALL)
        if faq_match:
            answer = faq_match.group(2).strip()
            print(f"📋 Прямой ответ извлечен: {answer[:50]}...")
            return answer
        
        # Если нет FAQ структуры, возвращаем весь контент
        return content.strip()
    
    def _generate_contextual_answer(self, query: str, documents: List[Document]) -> str:
        """Генерация контекстуального ответа для векторного поиска"""
        
        # Определяем тип запроса
        query_type = self._analyze_query_type(query)
        
        # Создаем контекст
        context = self._build_context(documents)
        
        # Создаем промпт
        prompt = self._create_contextual_prompt(context, query, query_type)
        
        print(f"🤖 Генерация контекстуального ответа для типа: {query_type}")
        
        try:
            response = self.llm.invoke(prompt)
            answer = response.content.strip()
            
            # Минимальная очистка
            return self._clean_answer(answer)
            
        except Exception as e:
            print(f"❌ Ошибка генерации: {e}")
            return "Не удалось сформировать ответ. Обратитесь к консультанту."
    
    def _analyze_query_type(self, query: str) -> str:
        """Анализ типа запроса"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['как', 'каким образом', 'способ', 'процедура']):
            return 'инструкция'
        elif any(word in query_lower for word in ['где', 'адрес', 'находится']):
            return 'адрес'
        elif any(word in query_lower for word in ['документы', 'требуются', 'нужны']):
            return 'документы'
        elif any(word in query_lower for word in ['лимит', 'ограничение', 'максимум']):
            return 'лимиты'
        elif any(word in query_lower for word in ['что такое', 'расскажи']):
            return 'объяснение'
        else:
            return 'общий'
    
    def _build_context(self, documents: List[Document]) -> str:
        """Построение контекста из документов"""
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            content = doc.page_content.strip()
            
            metadata_info = ""
            if hasattr(doc, 'metadata') and doc.metadata:
                metadata = doc.metadata
                if 'type' in metadata:
                    metadata_info = f"[{metadata['type']}] "
            
            context_parts.append(f"Документ {i}: {metadata_info}{content}")
        
        return "\n\n".join(context_parts)
    
    def _create_contextual_prompt(self, context: str, query: str, query_type: str) -> str:
        """Создание контекстуального промпта"""
        return f"""Ты - консультант банка Бакай. Отвечай точно на основе предоставленной информации.

ПРАВИЛА:
- Используй только информацию из контекста
- Будь конкретным и точным
- Отвечай на русском языке
- Если нет информации, честно скажи об этом

КОНТЕКСТ:
{context}

ВОПРОС: {query}

ОТВЕТ:"""
    
    def _clean_answer(self, answer: str) -> str:
        """Очистка ответа"""
        # Убираем лишние фразы
        unwanted_phrases = [
            "Рад помочь вам!",
            "Помощник банка Бакай:",
            "Здравствуйте!"
        ]
        
        cleaned = answer
        for phrase in unwanted_phrases:
            cleaned = cleaned.replace(phrase, "")
        
        # Убираем лишние пробелы
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def get_database_stats(self) -> Dict[str, any]:
        """Получение статистики базы данных"""
        try:
            collection = self.vectorstore._collection.get()
            documents = collection.get('documents', [])
            
            return {
                'total_documents': len(documents),
                'faq_count': len(self.faq_database),
                'database_ready': len(documents) > 0
            }
        except Exception as e:
            return {
                'error': str(e),
                'total_documents': 0,
                'database_ready': False
            }