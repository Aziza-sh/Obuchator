import re
import warnings
from typing import List, Tuple, Optional, Dict, Any
import logging
import sys
import traceback
from datetime import datetime

warnings.filterwarnings("ignore")

logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RobustThesisExtractor:

    def __init__(self, model_name: str = "IlyaGusev/rut5_base_sum_gazeta"):
        print(f"Загрузка модели {model_name}...")

        self.model_loaded = False
        self.model_name = model_name
        self.summarizer = None
        self.backup_mode = False

        self._init_backup_keywords()

        try:
            import torch
            from transformers import pipeline

            print("Проверка наличия CUDA...")
            has_cuda = torch.cuda.is_available()
            device = 0 if has_cuda else -1
            if has_cuda:
                print("CUDA доступна, используется GPU")
            else:
                print("CUDA не найдена, используется CPU")

            self.summarizer = pipeline(
                "summarization",
                model=model_name,
                device=device,
                tokenizer=model_name,
                framework="pt",
                trust_remote_code=True,
            )

            self.generation_params = {
                "max_length": 200,
                "min_length": 30,
                "do_sample": False,
                "temperature": 1.0,
                "repetition_penalty": 1.5,
                "length_penalty": 1.0,
                "num_beams": 2,
                "no_repeat_ngram_size": 2,
                "early_stopping": True,
            }

            self.model_loaded = True
            print(f"Модель {model_name} успешно загружена")

        except ImportError as e:
            print(f"Ошибка импорта: {e}")
            print("Переход в резервный режим (без ИИ-модели)...")
            self.backup_mode = True
            self.model_loaded = False

        except Exception as e:
            print(f"Ошибка при загрузке модели: {e}")
            print("Переход в резервный режим (без ИИ-модели)...")
            self.backup_mode = True
            self.model_loaded = False

    def _init_backup_keywords(self):
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
        print(f"\nИзвлечение {num_theses} ключевых тезисов...")

        if not text or len(text.strip()) < 100:
            return ["Текст слишком короткий для анализа."]

        if self.backup_mode or not self.model_loaded:
            print("Используется резервный алгоритм...")
            return self._extract_theses_backup(text, num_theses)

        try:
            clean_text = self._clean_text(text)

            sentences = self._split_into_sentences(clean_text)
            print(f"   Найдено предложений: {len(sentences)}")

            if len(sentences) < num_theses:
                print("Мало предложений, возвращаются лучшие...")
                return self._get_best_sentences(sentences, num_theses)

            key_sentences = self._select_key_sentences(sentences, num_theses * 2)

            text_for_summary = " ".join(key_sentences)

            if len(text_for_summary.split()) < 100:
                text_for_summary = clean_text

            print("   Генерация пересказа с помощью ИИ...")
            summary = self._generate_summary(text_for_summary, num_theses)

            result_sentences = self._split_into_sentences(summary)

            if len(result_sentences) < num_theses:
                additional = self._get_best_sentences(
                    key_sentences, num_theses - len(result_sentences)
                )
                result_sentences.extend(additional)

            final_theses = self._format_theses(result_sentences[:num_theses])

            return final_theses

        except Exception as e:
            print(f"Ошибка при извлечении тезисов: {e}")
            print("Используется резервный алгоритм...")
            return self._extract_theses_backup(text, num_theses)

    def _extract_theses_backup(self, text: str, num_theses: int) -> List[str]:
        print("Используется алгоритм на основе ключевых слов...")

        clean_text = self._clean_text(text)

        sentences = self._split_into_sentences(clean_text)

        if not sentences:
            return ["Не удалось разбить текст на предложения."]

        print(f"   Обрабатывается {len(sentences)} предложений...")

        scored_sentences = []

        for i, sentence in enumerate(sentences):
            score = self._score_sentence(sentence, i, len(sentences))
            if score > 0:
                scored_sentences.append((sentence, score))

        scored_sentences.sort(key=lambda x: x[1], reverse=True)

        best_sentences = [s for s, _ in scored_sentences[:num_theses]]

        formatted = []
        for sentence in best_sentences:
            formatted_sentence = self._format_sentence(sentence)
            if formatted_sentence:
                formatted.append(formatted_sentence)

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
        if not text:
            return ""

        text = re.sub(r"\s+", " ", text)

        text = re.sub(r'[^\w\s.,!?;:\-—()\[\]"\']', "", text)

        text = re.sub(r"\.{3,}", "...", text)

        text = re.sub(r"\s+([.,!?;:])", r"\1", text)

        return text.strip()

    def _split_into_sentences(self, text: str) -> List[str]:
        if not text:
            return []

        import nltk

        try:
            nltk.data.find("tokenizers/punkt")
        except:
            nltk.download("punkt", quiet=True)

        try:
            sentences = nltk.sent_tokenize(text, language="russian")
        except:
            sentences = []
            current = []
            words = text.split()

            for i, word in enumerate(words):
                current.append(word)

                if word.endswith((".", "!", "?", "...")):
                    if i + 1 < len(words):
                        next_word = words[i + 1]
                        if next_word and next_word[0].isupper():
                            sentence = " ".join(current)
                            if len(sentence.split()) >= 3:
                                sentences.append(sentence)
                            current = []

            if current:
                sentence = " ".join(current)
                if len(sentence.split()) >= 3:
                    sentences.append(sentence)

            if not sentences:
                parts = [p.strip() + "." for p in text.split(".") if p.strip()]
                sentences = [p for p in parts if len(p.split()) >= 3]

        clean_sentences = []
        for s in sentences:
            s = s.strip()
            if len(s.split()) >= 3:
                if s and s[-1] not in ".!?":
                    s += "."
                clean_sentences.append(s)

        return clean_sentences

    def _select_key_sentences(self, sentences: List[str], max_count: int) -> List[str]:
        if not sentences:
            return []

        scored = []
        for i, sentence in enumerate(sentences):
            score = self._score_sentence(sentence, i, len(sentences))
            scored.append((sentence, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        return [s for s, _ in scored[:max_count]]

    def _score_sentence(self, sentence: str, position: int, total: int) -> float:
        score = 0.0
        s_lower = sentence.lower()

        for keyword, weight in self.backup_keywords.items():
            if keyword in s_lower:
                score += weight

        word_count = len(sentence.split())
        if 10 <= word_count <= 25:
            score += 3.0
        elif 5 <= word_count <= 40:
            score += 1.0

        if position < 3:
            score += 2.0
        elif position > total - 3:
            score += 1.5

        if any(
            word in s_lower for word in ["это", "означает", "определение", "является"]
        ):
            score += 2.0

        if any(
            word in s_lower
            for word in ["например", "в частности", "таких как", "следующий"]
        ):
            score += 1.5

        if re.search(r"\d+", sentence):
            score += 1.0

        return score

    def _get_best_sentences(self, sentences: List[str], count: int) -> List[str]:
        if not sentences:
            return ["Нет данных для анализа."]

        if len(sentences) <= count:
            return [self._format_sentence(s) for s in sentences]

        scored = []
        for i, s in enumerate(sentences):
            score = self._score_sentence(s, i, len(sentences))
            scored.append((s, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        return [self._format_sentence(s) for s, _ in scored[:count]]

    def _generate_summary(self, text: str, num_sentences: int) -> str:
        try:
            words = text.split()
            if len(words) > 1000:
                text = " ".join(words[:1000])
                print(f"   Ограничение текста до {len(text.split())} слов")

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

            if num_sentences <= 3:
                params["max_length"] = 100
                params["min_length"] = 40
            elif num_sentences <= 5:
                params["max_length"] = 120
                params["min_length"] = 60

            if word_count < 200:
                params["max_length"] = min(
                    params["max_length"], max(60, word_count // 2)
                )
                params["min_length"] = min(
                    params["min_length"], max(30, word_count // 4)
                )

            result = self.summarizer(text, **params)

            if result and len(result) > 0:
                summary = result[0]["summary_text"]
                summary = self._clean_summary(summary)
                print(f"   Сгенерирован пересказ: {len(summary.split())} слов")
                return summary
            else:
                raise ValueError("Пустой результат от модели")

        except Exception as e:
            print(f"Ошибка генерации ИИ: {e}")
            sentences = self._split_into_sentences(text)[:num_sentences]
            return " ".join(sentences)

    def _clean_summary(self, text: str) -> str:
        if not text:
            return ""

        text = re.sub(r"\s+", " ", text).strip()

        text = text.strip("\"'")

        text = re.sub(r"\s([.,!?;:])", r"\1", text)
        text = re.sub(r"\.{2,}", ".", text)

        if text and text[0].islower():
            text = text[0].upper() + text[1:]

        if text and text[-1] not in ".!?":
            text += "."

        return text

    def _format_theses(self, sentences: List[str]) -> List[str]:
        formatted = []

        for sentence in sentences:
            if not sentence:
                continue

            formatted_sentence = self._format_sentence(sentence)
            if formatted_sentence:
                if formatted_sentence not in formatted:
                    formatted.append(formatted_sentence)

        return formatted if formatted else ["Не удалось сформулировать тезисы."]

    def _format_sentence(self, sentence: str) -> str:
        if not sentence:
            return ""

        sentence = sentence.strip()

        sentence = re.sub(r"\s+", " ", sentence)

        if sentence and sentence[0].islower():
            sentence = sentence[0].upper() + sentence[1:]

        if sentence and sentence[-1] not in ".!?":
            sentence += "."

        if len(sentence.split()) < 3:
            return ""

        return sentence


def analyze_theses(theses: List[str], original_text: str = None):
    print("\n" + "-" * 60)
    print("АНАЛИЗ РЕЗУЛЬТАТОВ")
    print("-" * 60)

    if not theses or (len(theses) == 1 and theses[0].startswith("Не удалось")):
        print("Тезисы не извлечены или произошла ошибка")
        return

    print(f"Извлечено тезисов: {len(theses)}")

    if theses:
        lengths = [len(t.split()) for t in theses]
        print("Статистика длины:")
        print(f"   Средняя: {sum(lengths)/len(lengths):.1f} слов")
        print(f"   Минимум: {min(lengths)} слов")
        print(f"   Максимум: {max(lengths)} слов")
        print(f"   Общий объем: {sum(lengths)} слов")

    print("\nКОНТРОЛЬ КАЧЕСТВА:")

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
        status = "выполнено" if passed else "не выполнено"
        print(f"   {check_name}: {status}")

    if original_text:
        coverage = check_themes_coverage(theses, original_text)
        if coverage:
            print("\nПОКРЫТИЕ ТЕМ:")
            covered_count = sum(1 for v in coverage.values() if v)
            print(f"   Покрыто тем: {covered_count}/{len(coverage)}")
            for theme, covered in coverage.items():
                status = "да" if covered else "нет"
                print(f"   {theme}: {status}")

    print("\nИЗВЛЕЧЕННЫЕ ТЕЗИСЫ:")
    print("-" * 60)

    for i, thesis in enumerate(theses, 1):
        words = len(thesis.split())
        print(f"{i:2d}. {thesis}")
        print(f"    [слов: {words}]")
        if i < len(theses):
            print()


def check_themes_coverage(theses: List[str], original_text: str) -> Dict[str, bool]:
    if not theses or not original_text:
        return {}

    all_theses = " ".join(theses).lower()
    original = original_text.lower()

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
        in_original = any(keyword in original for keyword in keywords)
        in_theses = any(keyword in all_theses for keyword in keywords)

        coverage[theme] = in_original and in_theses

    return coverage


def save_results(theses: List[str], filename: str = None):
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"theses_{timestamp}.txt"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("-" * 60 + "\n")
            f.write("ИЗВЛЕЧЕННЫЕ ТЕЗИСЫ\n")
            f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Количество: {len(theses)}\n")
            f.write("-" * 60 + "\n\n")

            for i, thesis in enumerate(theses, 1):
                words = len(thesis.split())
                f.write(f"{i}. {thesis}\n")
                f.write(f"   [слов: {words}]\n\n")

        print(f"Результаты сохранены в файл: {filename}")
        return filename
    except Exception as e:
        print(f"Ошибка при сохранении: {e}")
        return None


def demo_mode():
    print("\n" + "-" * 60)
    print("ДЕМОНСТРАЦИОННЫЙ РЕЖИМ")
    print("-" * 60)

    demo_text = """Искусственный интеллект (ИИ) представляет собой область компьютерных наук, которая занимается созданием интеллектуальных машин, способных выполнять задачи, требующие человеческого интеллекта. Машинное обучение — это подраздел ИИ, который позволяет системам автоматически обучаться и совершенствоваться на основе опыта. Глубокое обучение, в свою очередь, является подразделом машинного обучения, использующим многослойные нейронные сети. Нейронные сети имитируют работу человеческого мозга и состоят из взаимосвязанных узлов (нейронов). Алгоритмы глубокого обучения достигли значительных успехов в таких областях, как компьютерное зрение и обработка естественного языка. Компьютерное зрение позволяет машинам интерпретировать и понимать визуальную информацию из окружающего мира. Обработка естественного языка (NLP) дает компьютерам возможность понимать, интерпретировать и генерировать человеческий язык. Этические вопросы, связанные с ИИ, включают проблему смещения в данных, приватность информации и влияние на занятость. Развитие ИИ обещает революционизировать многие отрасли, включая медицину, финансы, транспорт и образование."""

    print(f"Демонстрационный текст ({len(demo_text.split())} слов):")
    print("-" * 60)
    print(demo_text[:300] + "..." if len(demo_text) > 300 else demo_text)
    print("-" * 60)

    try:
        num_theses = int(
            input("\nСколько тезисов извлечь? (5-10, по умолчанию 7): ") or "7"
        )
        num_theses = max(3, min(15, num_theses))
    except:
        num_theses = 7

    print("\nИнициализация модели...")
    extractor = RobustThesisExtractor()

    print("Обработка текста...")
    theses = extractor.extract_theses(demo_text, num_theses)

    analyze_theses(theses, demo_text)

    save_choice = input("\nСохранить результаты? (да/нет): ").lower()
    if save_choice in ["да", "д", "y", "yes"]:
        save_results(theses)


def manual_input_mode():
    print("\n" + "-" * 60)
    print("РУЧНОЙ ВВОД ТЕКСТА")
    print("-" * 60)

    print("\nВведите текст (две пустые строки для завершения):")
    print("-" * 60)

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
            print("\nПрервано пользователем")
            return

    text = "\n".join(lines).strip()

    if not text or len(text.split()) < 30:
        print("Текст слишком короткий. Минимум 30 слов.")
        return

    print(f"\nТекст получен: {len(text.split())} слов")

    try:
        num_theses = int(
            input("\nСколько тезисов извлечь? (3-15, по умолчанию 7): ") or "7"
        )
        num_theses = max(3, min(20, num_theses))
    except:
        num_theses = 7

    print("\nИнициализация модели...")
    extractor = RobustThesisExtractor()

    print("Обработка текста...")
    theses = extractor.extract_theses(text, num_theses)

    analyze_theses(theses, text)

    save_choice = input("\nСохранить результаты? (да/нет): ").lower()
    if save_choice in ["да", "д", "y", "yes"]:
        filename = input("Имя файла (оставьте пустым для автоимени): ").strip()
        save_results(theses, filename if filename else None)


def file_input_mode():
    print("\n" + "-" * 60)
    print("ЗАГРУЗКА ИЗ ФАЙЛА")
    print("-" * 60)

    filename = input("\nВведите путь к файлу: ").strip()

    if not filename:
        print("Не указан файл")
        return

    try:
        with open(filename, "r", encoding="utf-8") as f:
            text = f.read()

        if not text or len(text.split()) < 30:
            print("Файл пуст или слишком короткий")
            return

        print(f"Файл загружен: {len(text.split())} слов")
        print(f"\nПервые 500 символов:")
        print("-" * 60)
        print(text[:500] + "..." if len(text) > 500 else text)
        print("-" * 60)

        try:
            num_theses = int(
                input("\nСколько тезисов извлечь? (3-15, по умолчанию 7): ") or "7"
            )
            num_theses = max(3, min(20, num_theses))
        except:
            num_theses = 7

        print("\nИнициализация модели...")
        extractor = RobustThesisExtractor()

        print("Обработка текста...")
        theses = extractor.extract_theses(text, num_theses)

        analyze_theses(theses, text)

        save_choice = input("\nСохранить результаты? (да/нет): ").lower()
        if save_choice in ["да", "д", "y", "yes"]:
            save_name = input("Имя файла (оставьте пустым для автоимени): ").strip()
            save_results(theses, save_name if save_name else None)

    except FileNotFoundError:
        print(f"Файл не найден: {filename}")
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")


def main():
    print("-" * 60)
    print("ИЗВЛЕКАТЕЛЬ ТЕЗИСОВ ДЛЯ ТЕКСТОВ ОБ ИСКУССТВЕННОМ ИНТЕЛЛЕКТЕ")
    print("-" * 60)

    while True:
        print("\nГЛАВНОЕ МЕНЮ:")
        print("1. Демонстрация (встроенный текст об ИИ)")
        print("2. Ввести текст вручную")
        print("3. Загрузить текст из файла")
        print("4. Выход")

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
            print("\nДо свидания!")
            break
        else:
            print("Неверный выбор, попробуйте снова")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем")
    except Exception as e:
        print(f"\nНеожиданная ошибка: {e}")
        traceback.print_exc()
