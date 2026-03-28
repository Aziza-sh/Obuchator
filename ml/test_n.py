import logging
import re
import sys
import traceback
import warnings
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

warnings.filterwarnings("ignore")

# Настройка логирования
logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RobustThesisExtractor:
    """
    НАДЕЖНЫЙ извлекатель тезисов с улучшенной обработкой и обработкой ошибок
    """

    def __init__(self, model_name: str = "IlyaGusev/rut5_base_sum_gazeta"):
        """
        Инициализация экстрактора с улучшенной обработкой ошибок
        """
        print(f"🤖 Загружаем модель {model_name}...")

        # Инициализируем все атрибуты заранее
        self.model_loaded = False
        self.model_name = model_name
        self.summarizer = None
        self.backup_mode = False  # Режим резервного алгоритма

        # Инициализируем backup_keywords независимо от режима
        self._init_backup_keywords()

        try:
            import torch
            from transformers import pipeline

            print("📦 Проверяем наличие CUDA...")
            has_cuda = torch.cuda.is_available()
            device = 0 if has_cuda else -1
            if has_cuda:
                print("✅ CUDA доступна, используем GPU")
            else:
                print("ℹ️ CUDA не найдена, используем CPU")

            # Загружаем пайплайн с улучшенными параметрами
            self.summarizer = pipeline(
                "summarization",
                model=model_name,
                device=device,
                tokenizer=model_name,
                framework="pt",
                trust_remote_code=True,  # Добавляем для совместимости
            )

            # Сохраняем параметры для генерации
            self.generation_params = {
                "max_length": 200,  # Уменьшаем для большей стабильности
                "min_length": 30,
                "do_sample": False,
                "temperature": 1.0,
                "repetition_penalty": 1.5,
                "length_penalty": 1.0,
                "num_beams": 2,  # Уменьшаем для скорости
                "no_repeat_ngram_size": 2,
                "early_stopping": True,
            }

            self.model_loaded = True
            print(f"✅ Модель {model_name} успешно загружена")

        except ImportError as e:
            print(f"❌ Ошибка импорта: {e}")
            print("🔄 Переходим в резервный режим (без ИИ-модели)...")
            self.backup_mode = True
            self.model_loaded = False

        except Exception as e:
            print(f"⚠️ Ошибка при загрузке модели: {e}")
            print("🔄 Переходим в резервный режим (без ИИ-модели)...")
            self.backup_mode = True
            self.model_loaded = False

    def _init_backup_keywords(self):
        """Инициализация ключевых слов для резервного режима"""
        self.backup_keywords = {
            "искусственный интеллект": 4.0,
            "ии": 3.5,
            "машинное обучение": 4.0,
            "глубокое обучение": 3.5,
            "нейронная сеть": 3.0,
            "алгоритм": 2.5,
            "данные": 2.0,
            "модель": 2.0,
            "обучение": 2.5,
            "прогнозирование": 2.0,
            "анализ": 2.0,
            "обработка": 2.5,
            "nlp": 3.0,
            "компьютерное зрение": 2.5,
            "этика": 2.5,
            "безопасность": 2.0,
            "применение": 2.0,
            "будущее": 1.5,
            "развитие": 1.5,
            "технология": 2.0,
            "система": 2.0,
            "сеть": 2.0,
            "программа": 1.5,
            "код": 1.5,
            "разработка": 2.0,
            "инновация": 2.0,
            "цифровой": 2.0,
            "автоматизация": 2.5,
            "робот": 2.0,
            "бот": 1.5,
            "чат": 1.5,
            "ассистент": 1.5,
            "платформа": 1.5,
            "сервис": 1.5,
            "приложение": 1.5,
        }

    def extract_theses(self, text: str, num_theses: int = 7) -> List[str]:
        """
        Основной метод извлечения тезисов
        """
        print(f"\n🎯 Извлекаем {num_theses} ключевых тезисов...")

        if not text or len(text.strip()) < 100:
            return ["Текст слишком короткий для анализа."]

        # Проверяем режим работы
        if self.backup_mode or not self.model_loaded:
            print("ℹ️ Используем резервный алгоритм...")
            return self._extract_theses_backup(text, num_theses)

        try:
            # 1. Чистка текста
            clean_text = self._clean_text(text)

            # 2. Разделяем на предложения
            sentences = self._split_into_sentences(clean_text)
            print(f"   Найдено предложений: {len(sentences)}")

            if len(sentences) < num_theses:
                print("⚠️ Мало предложений, возвращаем лучшие...")
                return self._get_best_sentences(sentences, num_theses)

            # 3. Отбираем ключевые предложения
            key_sentences = self._select_key_sentences(sentences, num_theses * 2)

            # 4. Объединяем для суммаризации
            text_for_summary = " ".join(key_sentences)

            if len(text_for_summary.split()) < 100:
                # Если текст короткий, используем все предложения
                text_for_summary = clean_text

            # 5. Генерируем суммаризацию
            print("   Генерируем пересказ с помощью ИИ...")
            summary = self._generate_summary(text_for_summary, num_theses)

            # 6. Разбиваем результат на тезисы
            result_sentences = self._split_into_sentences(summary)

            # 7. Если результат короткий, дополняем ключевыми предложениями
            if len(result_sentences) < num_theses:
                additional = self._get_best_sentences(
                    key_sentences, num_theses - len(result_sentences)
                )
                result_sentences.extend(additional)

            # 8. Форматируем и ограничиваем количество
            final_theses = self._format_theses(result_sentences[:num_theses])

            return final_theses

        except Exception as e:
            print(f"⚠️ Ошибка при извлечении тезисов: {e}")
            print("🔄 Используем резервный алгоритм...")
            return self._extract_theses_backup(text, num_theses)

    def _extract_theses_backup(self, text: str, num_theses: int) -> List[str]:
        """Резервный алгоритм извлечения тезисов"""
        print("📝 Используем алгоритм на основе ключевых слов...")

        # Очищаем текст
        clean_text = self._clean_text(text)

        # Разбиваем на предложения
        sentences = self._split_into_sentences(clean_text)

        if not sentences:
            return ["Не удалось разбить текст на предложения."]

        print(f"   Обрабатываем {len(sentences)} предложений...")

        # Оцениваем и ранжируем предложения
        scored_sentences = []

        for i, sentence in enumerate(sentences):
            score = self._score_sentence(sentence, i, len(sentences))
            if score > 0:
                scored_sentences.append((sentence, score))

        # Сортируем по оценке
        scored_sentences.sort(key=lambda x: x[1], reverse=True)

        # Берем лучшие
        best_sentences = [s for s, _ in scored_sentences[:num_theses]]

        # Форматируем
        formatted = []
        for sentence in best_sentences:
            formatted_sentence = self._format_sentence(sentence)
            if formatted_sentence:
                formatted.append(formatted_sentence)

        # Если не хватает тезисов
        if len(formatted) < num_theses:
            for sentence in sentences:
                if sentence not in best_sentences:
                    formatted_sentence = self._format_sentence(sentence)
                    if formatted_sentence and formatted_sentence not in formatted:
                        formatted.append(formatted_sentence)
                        if len(formatted) >= num_theses:
                            break

        return formatted if formatted else ["Не удалось извлечь тезисы."]

    def _clean_text(self, text: str) -> str:
        """Очистка текста"""
        if not text:
            return ""

        # Удаляем лишние пробелы и переносы строк
        text = re.sub(r"\s+", " ", text)

        # Удаляем специальные символы, но сохраняем пунктуацию
        text = re.sub(r'[^\w\s.,!?;:\-—()\[\]"\']', "", text)

        # Исправляем множественные точки
        text = re.sub(r"\.{3,}", "...", text)

        # Убираем пробелы перед пунктуацией
        text = re.sub(r"\s+([.,!?;:])", r"\1", text)

        return text.strip()

    def _split_into_sentences(self, text: str) -> List[str]:
        """Разделение текста на предложения"""
        if not text:
            return []

        # Используем простой алгоритм разделения
        # Сначала делим по основным разделителям
        import nltk

        try:
            nltk.data.find("tokenizers/punkt")
        except:
            nltk.download("punkt", quiet=True)

        try:
            sentences = nltk.sent_tokenize(text, language="russian")
        except:
            # Fallback: простой алгоритм
            sentences = []
            current = []
            words = text.split()

            for i, word in enumerate(words):
                current.append(word)

                # Проверяем, закончилось ли предложение
                if word.endswith((".", "!", "?", "...")):
                    if i + 1 < len(words):
                        next_word = words[i + 1]
                        if next_word and next_word[0].isupper():
                            sentence = " ".join(current)
                            if len(sentence.split()) >= 3:  # Минимум 3 слова
                                sentences.append(sentence)
                            current = []

            # Добавляем последнее предложение
            if current:
                sentence = " ".join(current)
                if len(sentence.split()) >= 3:
                    sentences.append(sentence)

            # Если все еще нет предложений, используем простое разделение по точке
            if not sentences:
                parts = [p.strip() + "." for p in text.split(".") if p.strip()]
                sentences = [p for p in parts if len(p.split()) >= 3]

        # Очищаем предложения
        clean_sentences = []
        for s in sentences:
            s = s.strip()
            if len(s.split()) >= 3:  # Минимум 3 слова
                # Убеждаемся, что есть завершающая пунктуация
                if s and s[-1] not in ".!?":
                    s += "."
                clean_sentences.append(s)

        return clean_sentences

    def _select_key_sentences(self, sentences: List[str], max_count: int) -> List[str]:
        """Выбор ключевых предложений"""
        if not sentences:
            return []

        # Оцениваем предложения
        scored = []
        for i, sentence in enumerate(sentences):
            score = self._score_sentence(sentence, i, len(sentences))
            scored.append((sentence, score))

        # Сортируем по оценке
        scored.sort(key=lambda x: x[1], reverse=True)

        # Возвращаем лучшие
        return [s for s, _ in scored[:max_count]]

    def _score_sentence(self, sentence: str, position: int, total: int) -> float:
        """Оценка важности предложения"""
        score = 0.0
        s_lower = sentence.lower()

        # Ключевые слова
        for keyword, weight in self.backup_keywords.items():
            if keyword in s_lower:
                score += weight

        # Длина предложения (оптимально 10-25 слов)
        word_count = len(sentence.split())
        if 10 <= word_count <= 25:
            score += 3.0
        elif 5 <= word_count <= 40:
            score += 1.0

        # Позиция в тексте (первые и последние предложения важнее)
        if position < 3:
            score += 2.0  # Начало текста
        elif position > total - 3:
            score += 1.5  # Конец текста

        # Наличие определений
        if any(
            word in s_lower for word in ["это", "означает", "определение", "является"]
        ):
            score += 2.0

        # Наличие конкретики
        if any(
            word in s_lower
            for word in ["например", "в частности", "таких как", "следующий"]
        ):
            score += 1.5

        # Наличие цифр и конкретных данных
        if re.search(r"\d+", sentence):
            score += 1.0

        return score

    def _get_best_sentences(self, sentences: List[str], count: int) -> List[str]:
        """Получение лучших предложений"""
        if not sentences:
            return ["Нет данных для анализа."]

        if len(sentences) <= count:
            return [self._format_sentence(s) for s in sentences]

        # Оцениваем и выбираем лучшие
        scored = []
        for i, s in enumerate(sentences):
            score = self._score_sentence(s, i, len(sentences))
            scored.append((s, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        return [self._format_sentence(s) for s, _ in scored[:count]]

    def _generate_summary(self, text: str, num_sentences: int) -> str:
        """Генерация суммаризации с помощью модели"""
        try:
            # Ограничиваем длину текста для модели
            words = text.split()
            if len(words) > 1000:
                text = " ".join(words[:1000])
                print(f"   Ограничили текст до {len(text.split())} слов")

            # Динамически настраиваем параметры
            word_count = len(text.split())

            params = {
                "max_length": 150,
                "min_length": 50,
                "do_sample": False,
                "temperature": 1.0,
                "repetition_penalty": 1.5,
                "length_penalty": 1.0,
                "num_beams": 2,
                "no_repeat_ngram_size": 2,
                "early_stopping": True,
            }

            # Настройка длины в зависимости от количества предложений
            if num_sentences <= 3:
                params["max_length"] = 100
                params["min_length"] = 40
            elif num_sentences <= 5:
                params["max_length"] = 120
                params["min_length"] = 60

            # Если текст короткий, уменьшаем параметры
            if word_count < 200:
                params["max_length"] = min(
                    params["max_length"], max(60, word_count // 2)
                )
                params["min_length"] = min(
                    params["min_length"], max(30, word_count // 4)
                )

            # Генерируем суммаризацию
            result = self.summarizer(text, **params)

            if result and len(result) > 0:
                summary = result[0]["summary_text"]
                # Очищаем результат
                summary = self._clean_summary(summary)
                print(f"   Сгенерирован пересказ: {len(summary.split())} слов")
                return summary
            else:
                raise ValueError("Пустой результат от модели")

        except Exception as e:
            print(f"⚠️ Ошибка генерации ИИ: {e}")
            # Возвращаем первые N предложений как fallback
            sentences = self._split_into_sentences(text)[:num_sentences]
            return " ".join(sentences)

    def _clean_summary(self, text: str) -> str:
        """Очистка результата суммаризации"""
        if not text:
            return ""

        # Убираем лишние пробелы
        text = re.sub(r"\s+", " ", text).strip()

        # Убираем кавычки в начале/конце
        text = text.strip("\"'")

        # Исправляем пунктуацию
        text = re.sub(r"\s([.,!?;:])", r"\1", text)
        text = re.sub(r"\.{2,}", ".", text)

        # Убеждаемся, что первая буква заглавная
        if text and text[0].islower():
            text = text[0].upper() + text[1:]

        # Убеждаемся, что есть точка в конце
        if text and text[-1] not in ".!?":
            text += "."

        return text

    def _format_theses(self, sentences: List[str]) -> List[str]:
        """Форматирование тезисов"""
        formatted = []

        for sentence in sentences:
            if not sentence:
                continue

            formatted_sentence = self._format_sentence(sentence)
            if formatted_sentence:
                # Убираем дубликаты
                if formatted_sentence not in formatted:
                    formatted.append(formatted_sentence)

        return formatted if formatted else ["Не удалось сформулировать тезисы."]

    def _format_sentence(self, sentence: str) -> str:
        """Форматирование одного предложения"""
        if not sentence:
            return ""

        sentence = sentence.strip()

        # Убираем лишние пробелы
        sentence = re.sub(r"\s+", " ", sentence)

        # Убеждаемся, что начинается с заглавной буквы
        if sentence and sentence[0].islower():
            sentence = sentence[0].upper() + sentence[1:]

        # Убеждаемся, что есть точка в конце
        if sentence and sentence[-1] not in ".!?":
            sentence += "."

        # Проверяем минимальную длину
        if len(sentence.split()) < 3:
            return ""

        return sentence


def analyze_theses(theses: List[str], original_text: str = None):
    """Анализ извлеченных тезисов с улучшенным выводом"""
    print("\n" + "=" * 80)
    print("📊 АНАЛИЗ РЕЗУЛЬТАТОВ")
    print("=" * 80)

    if not theses or (len(theses) == 1 and theses[0].startswith("Не удалось")):
        print("❌ Тезисы не извлечены или произошла ошибка")
        return

    print(f"📈 Извлечено тезисов: {len(theses)}")

    # Статистика
    if theses:
        lengths = [len(t.split()) for t in theses]
        print(f"📏 Статистика длины:")
        print(f"   • Средняя: {sum(lengths)/len(lengths):.1f} слов")
        print(f"   • Минимум: {min(lengths)} слов")
        print(f"   • Максимум: {max(lengths)} слов")
        print(f"   • Общий объем: {sum(lengths)} слов")

    # Проверка качества
    print(f"\n✅ КОНТРОЛЬ КАЧЕСТВА:")

    quality_checks = {
        "Заглавные буквы": all(t and t[0].isupper() for t in theses),
        "Завершающая пунктуация": all(t and t[-1] in ".!?" for t in theses),
        "Минимальная длина": all(len(t.split()) >= 3 for t in theses),
        "Нет обрывков": not any(
            t.strip().endswith(("котор", "что", "для", "на", "в", "с", "и", "а", "но"))
            for t in theses
        ),
        "Уникальность": len(set(theses)) == len(theses),
    }

    for check_name, passed in quality_checks.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check_name}")

    # Покрытие тем (если есть исходный текст)
    if original_text:
        coverage = check_themes_coverage(theses, original_text)
        if coverage:
            print(f"\n🎯 ПОКРЫТИЕ ТЕМ:")
            covered_count = sum(1 for v in coverage.values() if v)
            print(f"   Покрыто тем: {covered_count}/{len(coverage)}")
            for theme, covered in coverage.items():
                status = "✅" if covered else "❌"
                print(f"   {status} {theme}")

    # Вывод тезисов
    print(f"\n📝 ИЗВЛЕЧЕННЫЕ ТЕЗИСЫ:")
    print("-" * 80)

    for i, thesis in enumerate(theses, 1):
        words = len(thesis.split())
        print(f"{i:2d}. {thesis}")
        print(f"    [слов: {words}]")
        if i < len(theses):
            print()


def check_themes_coverage(theses: List[str], original_text: str) -> Dict[str, bool]:
    """Проверка покрытия ключевых тем"""
    if not theses or not original_text:
        return {}

    all_theses = " ".join(theses).lower()
    original = original_text.lower()

    # Ключевые темы для анализа текстов об ИИ
    themes = {
        "Определение ИИ": [
            "искусственный интеллект",
            "ии ",
            " ai ",
            "artificial intelligence",
        ],
        "Машинное обучение": ["машинное обучение", "ml ", "machine learning"],
        "Нейронные сети": ["нейронная сеть", "нейронные сети", "neural network"],
        "Глубокое обучение": ["глубокое обучение", "deep learning"],
        "Обработка языка": [
            "естественный язык",
            "nlp",
            "обработка текста",
            "natural language",
        ],
        "Применение ИИ": ["применение", "использование", "application", "используется"],
        "Этика и риски": [
            "этика",
            "риск",
            "безопасность",
            "ответственность",
            "этический",
        ],
    }

    coverage = {}
    for theme, keywords in themes.items():
        # Проверяем, есть ли тема в оригинале
        in_original = any(keyword in original for keyword in keywords)
        # Проверяем, есть ли тема в тезисах
        in_theses = any(keyword in all_theses for keyword in keywords)

        # Тема считается покрытой, если она есть в тексте и отражена в тезисах
        coverage[theme] = in_original and in_theses

    return coverage


def save_results(theses: List[str], filename: str = None):
    """Сохранение результатов в файл"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"theses_{timestamp}.txt"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("ИЗВЛЕЧЕННЫЕ ТЕЗИСЫ\n")
            f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Количество: {len(theses)}\n")
            f.write("=" * 80 + "\n\n")

            for i, thesis in enumerate(theses, 1):
                words = len(thesis.split())
                f.write(f"{i}. {thesis}\n")
                f.write(f"   [слов: {words}]\n\n")

        print(f"✅ Результаты сохранены в файл: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Ошибка при сохранении: {e}")
        return None


def demo_mode():
    """Демонстрационный режим"""
    print("\n" + "=" * 80)
    print("🎯 ДЕМОНСТРАЦИОННЫЙ РЕЖИМ")
    print("=" * 80)

    # Демонстрационный текст
    demo_text = """Искусственный интеллект (ИИ) представляет собой область компьютерных наук, которая занимается созданием интеллектуальных машин, способных выполнять задачи, требующие человеческого интеллекта. Машинное обучение — это подраздел ИИ, который позволяет системам автоматически обучаться и совершенствоваться на основе опыта. Глубокое обучение, в свою очередь, является подразделом машинного обучения, использующим многослойные нейронные сети. Нейронные сети имитируют работу человеческого мозга и состоят из взаимосвязанных узлов (нейронов). Алгоритмы глубокого обучения достигли значительных успехов в таких областях, как компьютерное зрение и обработка естественного языка. Компьютерное зрение позволяет машинам интерпретировать и понимать визуальную информацию из окружающего мира. Обработка естественного языка (NLP) дает компьютерам возможность понимать, интерпретировать и генерировать человеческий язык. Этические вопросы, связанные с ИИ, включают проблему смещения в данных, приватность информации и влияние на занятость. Развитие ИИ обещает революционизировать многие отрасли, включая медицину, финансы, транспорт и образование."""

    print(f"📄 Демонстрационный текст ({len(demo_text.split())} слов):")
    print("-" * 80)
    print(demo_text[:300] + "..." if len(demo_text) > 300 else demo_text)
    print("-" * 80)

    try:
        num_theses = int(
            input("\nСколько тезисов извлечь? (5-10, по умолчанию 7): ") or "7"
        )
        num_theses = max(3, min(15, num_theses))  # Ограничиваем диапазон
    except:
        num_theses = 7

    print("\n🤖 Инициализация модели...")
    extractor = RobustThesisExtractor()

    print("⏳ Обрабатываю текст...")
    theses = extractor.extract_theses(demo_text, num_theses)

    # Анализ результатов
    analyze_theses(theses, demo_text)

    # Предложение сохранить
    save_choice = input("\n💾 Сохранить результаты? (да/нет): ").lower()
    if save_choice in ["да", "д", "y", "yes"]:
        save_results(theses)


def manual_input_mode():
    """Ручной ввод текста"""
    print("\n" + "=" * 80)
    print("📝 РУЧНОЙ ВВОД ТЕКСТА")
    print("=" * 80)

    print("\nВведите текст (две пустые строки для завершения):")
    print("=" * 80)

    lines = []
    empty_lines = 0

    while True:
        try:
            line = input()
            if line.strip() == "":
                empty_lines += 1
                if empty_lines >= 2:
                    break
            else:
                empty_lines = 0
                lines.append(line)
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\n⏹️ Прервано пользователем")
            return

    text = "\n".join(lines).strip()

    if not text or len(text.split()) < 30:
        print("❌ Текст слишком короткий. Минимум 30 слов.")
        return

    print(f"\n✅ Текст получен: {len(text.split())} слов")

    try:
        num_theses = int(
            input("\nСколько тезисов извлечь? (3-15, по умолчанию 7): ") or "7"
        )
        num_theses = max(3, min(20, num_theses))
    except:
        num_theses = 7

    print("\n🤖 Инициализация модели...")
    extractor = RobustThesisExtractor()

    print("⏳ Обрабатываю текст...")
    theses = extractor.extract_theses(text, num_theses)

    analyze_theses(theses, text)

    save_choice = input("\n💾 Сохранить результаты? (да/нет): ").lower()
    if save_choice in ["да", "д", "y", "yes"]:
        filename = input("Имя файла (оставьте пустым для автоимени): ").strip()
        save_results(theses, filename if filename else None)


def file_input_mode():
    """Загрузка текста из файла"""
    print("\n" + "=" * 80)
    print("📁 ЗАГРУЗКА ИЗ ФАЙЛА")
    print("=" * 80)

    filename = input("\nВведите путь к файлу: ").strip()

    if not filename:
        print("❌ Не указан файл")
        return

    try:
        with open(filename, "r", encoding="utf-8") as f:
            text = f.read()

        if not text or len(text.split()) < 30:
            print("❌ Файл пуст или слишком короткий")
            return

        print(f"✅ Файл загружен: {len(text.split())} слов")
        print(f"\n📄 Первые 500 символов:")
        print("-" * 80)
        print(text[:500] + "..." if len(text) > 500 else text)
        print("-" * 80)

        try:
            num_theses = int(
                input("\nСколько тезисов извлечь? (3-15, по умолчанию 7): ") or "7"
            )
            num_theses = max(3, min(20, num_theses))
        except:
            num_theses = 7

        print("\n🤖 Инициализация модели...")
        extractor = RobustThesisExtractor()

        print("⏳ Обрабатываю текст...")
        theses = extractor.extract_theses(text, num_theses)

        analyze_theses(theses, text)

        save_choice = input("\n💾 Сохранить результаты? (да/нет): ").lower()
        if save_choice in ["да", "д", "y", "yes"]:
            save_name = input("Имя файла (оставьте пустым для автоимени): ").strip()
            save_results(theses, save_name if save_name else None)

    except FileNotFoundError:
        print(f"❌ Файл не найден: {filename}")
    except Exception as e:
        print(f"❌ Ошибка при чтении файла: {e}")


def main():
    """Главная функция с улучшенным интерфейсом"""
    print("=" * 80)
    print("🚀 УЛУЧШЕННЫЙ ИЗВЛЕКАТЕЛЬ ТЕЗИСОВ ДЛЯ ТЕКСТОВ ОБ ИИ")
    print("=" * 80)

    while True:
        print("\n📋 ГЛАВНОЕ МЕНЮ:")
        print("1. 🎯 Демонстрация (встроенный текст об ИИ)")
        print("2. 📝 Ввести текст вручную")
        print("3. 📁 Загрузить текст из файла")
        print("4. ❌ Выход")

        choice = input("\nВыберите опцию (1-4): ").strip()

        if choice == "1":
            demo_mode()
            input("\nНажмите Enter для возврата в меню...")
        elif choice == "2":
            manual_input_mode()
            input("\nНажмите Enter для возврата в меню...")
        elif choice == "3":
            file_input_mode()
            input("\nНажмите Enter для возврата в меню...")
        elif choice == "4":
            print("\n👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор, попробуйте снова")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Программа прервана пользователем")
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        traceback.print_exc()
