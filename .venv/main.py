import sys
import json
import random
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class QuizApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.questions = []
        self.filtered_questions = []
        self.current_question = 0
        self.score = 0
        self.total_questions = 0
        self.user_answer = None
        self.correct_answers = 0
        self.skipped_questions = 0
        self.difficulty = "all"
        self.time_limit = 0
        self.current_time = 0
        self.timer = QTimer()

        self.load_questions()
        self.show_difficulty_selection()

    def load_questions(self):
        """Загрузка вопросов из JSON файлов в директории"""
        self.questions = []

        try:
            questions_dir = "questions"

            if not os.path.exists(questions_dir):
                QMessageBox.critical(None, "Ошибка",
                                     f"Директория '{questions_dir}' не найдена!")
                sys.exit(1)

            json_files = [f for f in os.listdir(questions_dir) if f.endswith('.json')]

            if not json_files:
                QMessageBox.critical(None, "Ошибка",
                                     f"В директории '{questions_dir}' нет JSON файлов!")
                sys.exit(1)

            for json_file in json_files:
                file_path = os.path.join(questions_dir, json_file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        questions_from_file = json.load(f)

                        category_name = json_file.replace('.json', '').capitalize()
                        for question in questions_from_file:
                            if 'category' not in question:
                                question['category'] = category_name
                            if 'difficulty' not in question:
                                question['difficulty'] = 'medium'

                        self.questions.extend(questions_from_file)

                except json.JSONDecodeError as e:
                    print(f"Ошибка JSON в файле {json_file}: {e}")
                    continue
                except Exception as e:
                    print(f"Ошибка загрузки {json_file}: {e}")
                    continue

            if not self.questions:
                QMessageBox.critical(None, "Ошибка", "Не удалось загрузить ни одного вопроса!")
                sys.exit(1)

            # Сортируем вопросы по сложности
            self.questions.sort(key=lambda x: x.get('difficulty', 'medium'))
            print(f"Загружено {len(self.questions)} вопросов")

        except Exception as e:
            QMessageBox.critical(None, "Ошибка", f"Ошибка загрузки вопросов: {str(e)}")
            sys.exit(1)

    def show_difficulty_selection(self):
        """Показ окна выбора уровня сложности"""
        self.difficulty_dialog = QDialog(self)
        self.difficulty_dialog.setWindowTitle("Выбор уровня сложности")
        self.difficulty_dialog.setFixedSize(500, 400)
        self.difficulty_dialog.setStyleSheet("""
            QDialog {
                background-color: #2c3e50;
            }
            QLabel {
                color: white;
                font-size: 18px;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Заголовок
        title_label = QLabel("🎮 ВИКТОРИНА")
        title_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 36px;
                font-weight: bold;
                text-align: center;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        subtitle_label = QLabel("Выберите уровень сложности:")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 20px;
                text-align: center;
            }
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)

        layout.addSpacing(20)

        # Кнопки выбора сложности
        difficulties = [
            ("easy", "🍰 ПРОСТОЙ", "#2ecc71",
             "• 30 секунд на ответ\n• Простые вопросы\n• Подсказки доступны"),
            ("medium", "⚖️ СРЕДНИЙ", "#f39c12",
             "• 20 секунд на ответ\n• Вопросы средней сложности\n• Без подсказок"),
            ("hard", "🔥 СЛОЖНЫЙ", "#e74c3c",
             "• 10 секунд на ответ\n• Сложные вопросы\n• Штраф за неправильные ответы")
        ]

        for diff_id, diff_name, color, description in difficulties:
            diff_btn = QPushButton(diff_name)
            diff_btn.setMinimumHeight(70)
            diff_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                    border: none;
                    border-radius: 10px;
                    padding: 15px;
                    text-align: left;
                    padding-left: 30px;
                }}
                QPushButton:hover {{
                    background-color: {'#27ae60' if diff_id == 'easy' else '#e67e22' if diff_id == 'medium' else '#c0392b'};
                    border: 3px solid white;
                }}
            """)

            # Создаем виджет с описанием
            desc_widget = QWidget()
            desc_layout = QVBoxLayout()
            desc_label = QLabel(description)
            desc_label.setStyleSheet("""
                QLabel {
                    color: #bdc3c7;
                    font-size: 14px;
                    padding: 5px;
                }
            """)
            desc_label.setWordWrap(True)
            desc_layout.addWidget(desc_label)
            desc_widget.setLayout(desc_layout)

            # Используем lambda с сохранением значения
            diff_btn.clicked.connect(lambda checked, d=diff_id: self.set_difficulty_and_start(d))

            layout.addWidget(diff_btn)
            layout.addWidget(desc_widget)

        # Кнопка "Все уровни"
        all_btn = QPushButton("🌈 ВСЕ УРОВНИ")
        all_btn.setMinimumHeight(60)
        all_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #9b59b6, stop:0.5 #3498db, stop:1 #2ecc71);
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:hover {
                border: 3px solid white;
            }
        """)
        all_btn.clicked.connect(lambda: self.set_difficulty_and_start("all"))

        layout.addSpacing(20)
        layout.addWidget(all_btn)

        self.difficulty_dialog.setLayout(layout)
        self.difficulty_dialog.exec_()

    def set_difficulty_and_start(self, difficulty):
        """Установка уровня сложности и начало игры"""
        self.difficulty = difficulty

        # Устанавливаем параметры в зависимости от сложности
        if difficulty == "easy":
            self.time_limit = 30
            # Берем только простые вопросы
            self.filtered_questions = [q for q in self.questions
                                       if q.get('difficulty', 'medium') in ['easy']]
        elif difficulty == "medium":
            self.time_limit = 20
            # Берем вопросы средней сложности
            self.filtered_questions = [q for q in self.questions
                                       if q.get('difficulty', 'medium') == 'medium']
        elif difficulty == "hard":
            self.time_limit = 10
            # Берем только сложные вопросы
            self.filtered_questions = [q for q in self.questions
                                       if q.get('difficulty', 'medium') == 'hard']
        else:  # all
            self.time_limit = 25
            self.filtered_questions = self.questions.copy()

        # Проверяем, есть ли вопросы для выбранного уровня
        if not self.filtered_questions:
            QMessageBox.warning(self.difficulty_dialog, "Внимание",
                                f"Для уровня '{self.get_difficulty_name(difficulty)}' нет вопросов!\n"
                                f"Выберите другой уровень или добавьте вопросы с нужной сложностью.")
            return

        # Перемешиваем вопросы
        random.shuffle(self.filtered_questions)
        self.total_questions = len(self.filtered_questions)

        print(f"Выбран уровень: {difficulty}, вопросов: {self.total_questions}")

        # Закрываем диалог выбора сложности
        self.difficulty_dialog.close()

        # Инициализируем и показываем главное окно
        self.init_ui()
        self.show()
        self.show_question()

    def get_difficulty_name(self, difficulty=None):
        """Получение названия уровня сложности"""
        if difficulty is None:
            difficulty = self.difficulty

        names = {
            "easy": "ПРОСТОЙ",
            "medium": "СРЕДНИЙ",
            "hard": "СЛОЖНЫЙ",
            "all": "ВСЕ УРОВНИ"
        }
        return names.get(difficulty, "СРЕДНИЙ")

    def init_ui(self):
        """Инициализация интерфейса главного окна"""
        self.setWindowTitle(f"Викторина - Уровень: {self.get_difficulty_name()}")
        self.setGeometry(300, 100, 850, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)

        # Верхняя панель
        top_panel = QHBoxLayout()

        # Уровень сложности
        self.difficulty_label = QLabel(f"Уровень: {self.get_difficulty_name()}")
        self.difficulty_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {self.get_difficulty_color()};
            padding: 8px 15px;
            background-color: {self.get_difficulty_bg_color()};
            border-radius: 15px;
        """)
        top_panel.addWidget(self.difficulty_label)

        top_panel.addStretch()

        # Таймер
        self.timer_label = QLabel(f"⏱️ {self.time_limit} сек")
        self.timer_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 8px 15px;
            background-color: #ecf0f1;
            border-radius: 15px;
            border: 2px solid #3498db;
        """)
        top_panel.addWidget(self.timer_label)

        top_panel.addStretch()

        # Счет
        self.score_label = QLabel(f"🏆 Счет: {self.score}")
        self.score_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 8px 15px;
            background-color: #fffacd;
            border-radius: 15px;
            border: 2px solid #f39c12;
        """)
        top_panel.addWidget(self.score_label)

        main_layout.addLayout(top_panel)

        # Панель прогресса
        progress_panel = QHBoxLayout()

        self.progress_label = QLabel(f"Вопрос {self.current_question + 1}/{self.total_questions}")
        self.progress_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        progress_panel.addWidget(self.progress_label)

        progress_panel.addStretch()

        self.skipped_label = QLabel(f"⏭️ Пропущено: {self.skipped_questions}")
        self.skipped_label.setStyleSheet("font-size: 14px; color: #e74c3c;")
        progress_panel.addWidget(self.skipped_label)

        main_layout.addLayout(progress_panel)

        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(self.total_questions)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3498db;
                border-radius: 5px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        main_layout.addWidget(self.progress_bar)

        # Индикатор сложности текущего вопроса
        self.question_difficulty_label = QLabel()
        self.question_difficulty_label.setAlignment(Qt.AlignCenter)
        self.question_difficulty_label.setMaximumHeight(30)
        main_layout.addWidget(self.question_difficulty_label)

        # Категория вопроса
        self.category_label = QLabel()
        self.category_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #3498db;
            padding: 10px;
            background-color: #ebf5fb;
            border-radius: 8px;
            border: 1px solid #3498db;
        """)
        self.category_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.category_label)

        # Вопрос
        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #2c3e50;
                padding: 25px;
                background-color: #f8f9fa;
                border-radius: 15px;
                border: 3px solid #dfe6e9;
                margin: 10px;
            }
        """)
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setMinimumHeight(180)
        main_layout.addWidget(self.question_label)

        # Кнопки с вариантами ответов
        self.option_buttons = []
        button_styles = [
            "background-color: #3498db;",  # синий
            "background-color: #2ecc71;",  # зеленый
            "background-color: #e74c3c;",  # красный
            "background-color: #9b59b6;",  # фиолетовый
        ]

        for i in range(4):
            btn = QPushButton()
            btn.setMinimumHeight(65)
            btn.setStyleSheet(f"""
                QPushButton {{
                    {button_styles[i]}
                    color: white;
                    font-size: 16px;
                    border: none;
                    border-radius: 10px;
                    padding: 15px;
                    text-align: left;
                    padding-left: 30px;
                }}
                QPushButton:hover {{
                    border: 3px solid white;
                    font-weight: bold;
                }}
                QPushButton:disabled {{
                    background-color: #bdc3c7;
                }}
            """)
            btn.clicked.connect(lambda checked, idx=i: self.check_answer(idx))
            self.option_buttons.append(btn)
            main_layout.addWidget(btn)

        # Нижняя панель с кнопками
        bottom_panel = QHBoxLayout()

        # Кнопка "Подсказка" (только для простого уровня)
        self.hint_btn = QPushButton("💡 Подсказка")
        self.hint_btn.setMinimumHeight(45)
        self.hint_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 10px;
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.hint_btn.clicked.connect(self.show_hint)
        self.hint_btn.setEnabled(self.difficulty == "easy")  # только для простого уровня
        bottom_panel.addWidget(self.hint_btn)

        bottom_panel.addStretch()

        # Кнопка "Пропустить вопрос"
        self.skip_btn = QPushButton("⏭️ Пропустить")
        self.skip_btn.setMinimumHeight(45)
        self.skip_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 10px;
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.skip_btn.clicked.connect(self.skip_question)
        bottom_panel.addWidget(self.skip_btn)

        # Кнопка "Следующий вопрос"
        self.next_btn = QPushButton("Далее →")
        self.next_btn.setMinimumHeight(45)
        self.next_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.next_btn.clicked.connect(self.next_question)
        self.next_btn.setEnabled(False)
        bottom_panel.addWidget(self.next_btn)

        main_layout.addLayout(bottom_panel)

        # Кнопка "Сменить уровень"
        self.change_difficulty_btn = QPushButton("🔄 Сменить уровень сложности")
        self.change_difficulty_btn.setMinimumHeight(40)
        self.change_difficulty_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 8px;
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        self.change_difficulty_btn.clicked.connect(self.restart_with_difficulty)
        main_layout.addWidget(self.change_difficulty_btn)

        central_widget.setLayout(main_layout)

    def get_difficulty_color(self):
        """Получение цвета для уровня сложности"""
        colors = {
            "easy": "#27ae60",
            "medium": "#e67e22",
            "hard": "#c0392b",
            "all": "#9b59b6"
        }
        return colors.get(self.difficulty, "#3498db")

    def get_difficulty_bg_color(self):
        """Получение фонового цвета для уровня сложности"""
        colors = {
            "easy": "#d5f4e6",
            "medium": "#fdebd0",
            "hard": "#fadbd8",
            "all": "#ebdef0"
        }
        return colors.get(self.difficulty, "#ebf5fb")

    def start_timer(self):
        """Запуск таймера для вопроса"""
        self.current_time = self.time_limit
        self.timer_label.setText(f"⏱️ {self.current_time} сек")

        # Останавливаем предыдущий таймер если был
        if self.timer.isActive():
            self.timer.stop()

        # Создаем новый таймер
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)  # обновление каждую секунду

    def update_timer(self):
        """Обновление таймера"""
        if self.current_time > 0:
            self.current_time -= 1
            self.timer_label.setText(f"⏱️ {self.current_time} сек")

            # Меняем цвет при малом времени
            if self.current_time <= 5:
                self.timer_label.setStyleSheet("""
                    font-size: 16px;
                    font-weight: bold;
                    color: white;
                    padding: 8px 15px;
                    background-color: #e74c3c;
                    border-radius: 15px;
                    border: 2px solid #c0392b;
                """)
            elif self.current_time <= 10:
                self.timer_label.setStyleSheet("""
                    font-size: 16px;
                    font-weight: bold;
                    color: white;
                    padding: 8px 15px;
                    background-color: #f39c12;
                    border-radius: 15px;
                    border: 2px solid #e67e22;
                """)
        else:
            # Время вышло
            self.timer.stop()
            self.time_out()

    def time_out(self):
        """Действия при истечении времени"""
        self.timer_label.setText("⏱️ ВРЕМЯ!")

        # Автоматически считаем ответ неправильным
        self.skipped_questions += 1
        self.skipped_label.setText(f"⏭️ Пропущено: {self.skipped_questions}")

        # Показываем правильный ответ
        correct_answer = self.filtered_questions[self.current_question]['answer']
        for i in range(4):
            self.option_buttons[i].setEnabled(False)
            if i == correct_answer:
                self.option_buttons[i].setStyleSheet(f"""
                    QPushButton {{
                        background-color: #2ecc71;
                        color: white;
                        font-size: 16px;
                        border: 3px solid #27ae60;
                        border-radius: 10px;
                        padding: 15px;
                        text-align: left;
                        padding-left: 30px;
                        font-weight: bold;
                    }}
                """)
            else:
                self.option_buttons[i].setStyleSheet(f"""
                    QPushButton {{
                        background-color: #bdc3c7;
                        color: white;
                        font-size: 16px;
                        border: none;
                        border-radius: 10px;
                        padding: 15px;
                        text-align: left;
                        padding-left: 30px;
                    }}
                """)

        self.next_btn.setEnabled(True)
        self.skip_btn.setEnabled(False)
        self.hint_btn.setEnabled(False)

    def show_question(self):
        """Отображение текущего вопроса"""
        if self.current_question >= self.total_questions:
            self.show_results()
            return

        # Обновляем прогресс-бар
        self.progress_bar.setValue(self.current_question)

        question_data = self.filtered_questions[self.current_question]

        # Обновляем интерфейс
        self.question_label.setText(question_data['question'])
        self.category_label.setText(f"📁 Категория: {question_data.get('category', 'Общие знания')}")
        self.progress_label.setText(f"Вопрос {self.current_question + 1}/{self.total_questions}")

        # Отображаем сложность вопроса
        difficulty = question_data.get('difficulty', 'medium')
        diff_text = {
            'easy': '🍰 Легкий вопрос',
            'medium': '⚖️ Средний вопрос',
            'hard': '🔥 Сложный вопрос'
        }.get(difficulty, '⚖️ Средний вопрос')

        diff_color = {
            'easy': '#27ae60',
            'medium': '#f39c12',
            'hard': '#e74c3c'
        }.get(difficulty, '#f39c12')

        self.question_difficulty_label.setText(diff_text)
        self.question_difficulty_label.setStyleSheet(f"""
            color: {diff_color};
            font-size: 14px;
            font-weight: bold;
            background-color: {'#d5f4e6' if difficulty == 'easy' else '#fdebd0' if difficulty == 'medium' else '#fadbd8'};
            border-radius: 5px;
            padding: 3px;
        """)

        # Отображаем варианты ответов
        options = question_data['options']
        for i in range(4):
            if i < len(options):
                self.option_buttons[i].setText(f"{chr(65 + i)}) {options[i]}")
                self.option_buttons[i].setVisible(True)
                self.option_buttons[i].setEnabled(True)

                # Восстанавливаем оригинальный цвет кнопки
                button_styles = [
                    "background-color: #3498db;",
                    "background-color: #2ecc71;",
                    "background-color: #e74c3c;",
                    "background-color: #9b59b6;",
                ]
                self.option_buttons[i].setStyleSheet(f"""
                    QPushButton {{
                        {button_styles[i]}
                        color: white;
                        font-size: 16px;
                        border: none;
                        border-radius: 10px;
                        padding: 15px;
                        text-align: left;
                        padding-left: 30px;
                    }}
                    QPushButton:hover {{
                        border: 3px solid white;
                        font-weight: bold;
                    }}
                """)
            else:
                self.option_buttons[i].setVisible(False)

        # Сбрасываем состояние кнопок
        self.next_btn.setEnabled(False)
        self.skip_btn.setEnabled(True)
        self.hint_btn.setEnabled(self.difficulty == "easy")
        self.user_answer = None

        # Запускаем таймер
        if self.time_limit > 0:
            self.start_timer()

    def check_answer(self, option_index):
        """Проверка выбранного ответа"""
        if self.user_answer is not None:
            return

        # Останавливаем таймер
        if self.timer.isActive():
            self.timer.stop()

        self.user_answer = option_index
        correct_answer = self.filtered_questions[self.current_question]['answer']

        # Блокируем все кнопки
        for btn in self.option_buttons:
            btn.setEnabled(False)

        # Подсвечиваем ответы
        for i in range(4):
            if i == correct_answer:
                self.option_buttons[i].setStyleSheet(f"""
                    QPushButton {{
                        background-color: #2ecc71;
                        color: white;
                        font-size: 16px;
                        border: 3px solid #27ae60;
                        border-radius: 10px;
                        padding: 15px;
                        text-align: left;
                        padding-left: 30px;
                        font-weight: bold;
                    }}
                """)
            elif i == option_index and i != correct_answer:
                self.option_buttons[i].setStyleSheet(f"""
                    QPushButton {{
                        background-color: #e74c3c;
                        color: white;
                        font-size: 16px;
                        border: 3px solid #c0392b;
                        border-radius: 10px;
                        padding: 15px;
                        text-align: left;
                        padding-left: 30px;
                        font-weight: bold;
                    }}
                """)
            else:
                self.option_buttons[i].setStyleSheet(f"""
                    QPushButton {{
                        background-color: #bdc3c7;
                        color: white;
                        font-size: 16px;
                        border: none;
                        border-radius: 10px;
                        padding: 15px;
                        text-align: left;
                        padding-left: 30px;
                    }}
                """)

        # Проверяем ответ и обновляем счет
        if option_index == correct_answer:
            # Начисляем очки в зависимости от сложности
            points = {
                'easy': 1,
                'medium': 2,
                'hard': 3
            }.get(self.filtered_questions[self.current_question].get('difficulty', 'medium'), 1)

            self.score += points
            self.correct_answers += 1
            self.score_label.setText(f"🏆 Счет: {self.score} (+{points}!)")
            self.score_label.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 8px 15px;
                background-color: #d5f4e6;
                border-radius: 15px;
                border: 2px solid #27ae60;
            """)
        else:
            # Штраф за неправильный ответ на сложном уровне
            if self.difficulty == "hard":
                self.score = max(0, self.score - 1)  # не уходим в минус
                self.score_label.setText(f"🏆 Счет: {self.score} (-1!)")

            self.score_label.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 8px 15px;
                background-color: #fadbd8;
                border-radius: 15px;
                border: 2px solid #e74c3c;
            """)

        self.next_btn.setEnabled(True)
        self.skip_btn.setEnabled(False)
        self.hint_btn.setEnabled(False)

    def show_hint(self):
        """Показать подсказку (только для простого уровня)"""
        if self.difficulty != "easy":
            return

        question_data = self.filtered_questions[self.current_question]
        correct_answer = question_data['answer']
        options = question_data['options']

        # Убираем два неправильных варианта
        wrong_indices = [i for i in range(len(options)) if i != correct_answer]
        random.shuffle(wrong_indices)
        indices_to_disable = wrong_indices[:2]  # отключаем 2 неправильных ответа

        for i in indices_to_disable:
            self.option_buttons[i].setEnabled(False)
            self.option_buttons[i].setStyleSheet(f"""
                QPushButton {{
                    background-color: #95a5a6;
                    color: white;
                    font-size: 16px;
                    border: none;
                    border-radius: 10px;
                    padding: 15px;
                    text-align: left;
                    padding-left: 30px;
                }}
            """)

        self.hint_btn.setEnabled(False)
        QMessageBox.information(self, "Подсказка",
                                "Два неправильных варианта были скрыты!\nУ вас осталось 2 варианта на выбор.")

    def skip_question(self):
        """Пропуск текущего вопроса"""
        # Останавливаем таймер
        if self.timer.isActive():
            self.timer.stop()

        self.skipped_questions += 1
        self.skipped_label.setText(f"⏭️ Пропущено: {self.skipped_questions}")

        # Штраф за пропуск на сложном уровне
        if self.difficulty == "hard":
            self.score = max(0, self.score - 1)
            self.score_label.setText(f"🏆 Счет: {self.score} (-1 за пропуск!)")

        # Показываем правильный ответ
        correct_answer = self.filtered_questions[self.current_question]['answer']
        for i in range(4):
            self.option_buttons[i].setEnabled(False)
            if i == correct_answer:
                self.option_buttons[i].setStyleSheet(f"""
                    QPushButton {{
                        background-color: #f39c12;
                        color: white;
                        font-size: 16px;
                        border: 3px solid #e67e22;
                        border-radius: 10px;
                        padding: 15px;
                        text-align: left;
                        padding-left: 30px;
                        font-weight: bold;
                    }}
                """)
            else:
                self.option_buttons[i].setStyleSheet(f"""
                    QPushButton {{
                        background-color: #bdc3c7;
                        color: white;
                        font-size: 16px;
                        border: none;
                        border-radius: 10px;
                        padding: 15px;
                        text-align: left;
                        padding-left: 30px;
                    }}
                """)

        self.next_btn.setEnabled(True)
        self.skip_btn.setEnabled(False)
        self.hint_btn.setEnabled(False)
        self.user_answer = None

    def next_question(self):
        """Переход к следующему вопросу"""
        self.current_question += 1

        if self.current_question < self.total_questions:
            self.show_question()
            # Возвращаем обычный стиль счету
            self.score_label.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 8px 15px;
                background-color: #fffacd;
                border-radius: 15px;
                border: 2px solid #f39c12;
            """)
        else:
            self.show_results()

    def show_results(self):
        """Показ результатов викторины"""
        # Останавливаем таймер
        if self.timer.isActive():
            self.timer.stop()

        total_answered = self.current_question
        total_skipped = self.skipped_questions
        total_correct = self.correct_answers

        # Расчет процента правильных ответов
        if total_answered > 0:
            max_possible_score = sum(
                3 if q.get('difficulty', 'medium') == 'hard' else
                2 if q.get('difficulty', 'medium') == 'medium' else 1
                for q in self.filtered_questions[:total_answered]
            )
            percentage = (self.score / max_possible_score * 100) if max_possible_score > 0 else 0
        else:
            percentage = 0

        # Обновляем прогресс-бар
        self.progress_bar.setValue(self.total_questions)

        # Скрываем ненужные элементы
        for btn in self.option_buttons:
            btn.setVisible(False)
        self.next_btn.setVisible(False)
        self.skip_btn.setVisible(False)
        self.hint_btn.setVisible(False)
        self.question_difficulty_label.setVisible(False)

        # Определяем результат
        if total_answered == 0:
            result_text = self.get_game_over_text(total_answered, total_skipped, total_correct, percentage)
        elif total_correct == 0 and total_answered > 0:
            result_text = self.get_lost_text(total_answered, total_skipped, total_correct, percentage)
        else:
            result_text = self.get_regular_results_text(total_answered, total_skipped, total_correct, percentage)

        self.question_label.setText(result_text)
        self.category_label.setText("🎮 ИТОГИ ВИКТОРИНЫ")
        self.progress_label.setText("Викторина завершена!")

        # Меняем цвет в зависимости от результата
        if total_correct == 0:
            self.score_label.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 8px 15px;
                background-color: #fadbd8;
                border-radius: 15px;
                border: 2px solid #e74c3c;
            """)
        else:
            self.score_label.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 8px 15px;
                background-color: #d5f4e6;
                border-radius: 15px;
                border: 2px solid #27ae60;
            """)

    def get_game_over_text(self, answered, skipped, correct, percentage):
        """Текст для полного проигрыша"""
        return f"""
        <div style='text-align: center;'>
            <h1 style='color: #e74c3c;'>🎮 ВИКТОРИНА ЗАВЕРШЕНА 🎮</h1>
            <div style='font-size: 80px; margin: 20px; color: #e74c3c;'>💀</div>
            <h2 style='color: #e74c3c; font-size: 24px;'>ВЫ НЕ ОТВЕТИЛИ НИ НА ОДИН ВОПРОС!</h2>

            <div style='background-color: #ffebee; padding: 20px; border-radius: 10px; margin: 20px; border: 2px solid #ffcdd2;'>
                <p style='font-size: 20px;'><b>Статистика уровня "{self.get_difficulty_name()}":</b></p>
                <p style='font-size: 18px;'>Всего вопросов: <b>{self.total_questions}</b></p>
                <p style='font-size: 18px; color: #e74c3c;'>Отвечено: <b>0</b></p>
                <p style='font-size: 18px; color: #e74c3c;'>Пропущено: <b>{skipped}</b></p>
                <p style='font-size: 18px; color: #e74c3c;'>Итоговый счет: <b>{self.score}</b></p>
            </div>

            <p style='font-size: 18px; color: #7f8c8d; margin-top: 20px;'>
                Попробуйте выбрать более простой уровень<br>
                или отвечать на вопросы, а не пропускать их!
            </p>
        </div>
        """

    def get_lost_text(self, answered, skipped, correct, percentage):
        """Текст для проигрыша (есть ответы, но все неправильные)"""
        return f"""
        <div style='text-align: center;'>
            <h1 style='color: #e74c3c;'>😔 ВЫ ПРОИГРАЛИ НА УРОВНЕ "{self.get_difficulty_name()}"</h1>
            <div style='font-size: 80px; margin: 20px;'>😟</div>

            <div style='background-color: #fff3e0; padding: 20px; border-radius: 10px; margin: 20px; border: 2px solid #ffe0b2;'>
                <p style='font-size: 20px;'><b>Результаты уровня "{self.get_difficulty_name()}":</b></p>
                <p style='font-size: 18px;'>Всего вопросов: <b>{self.total_questions}</b></p>
                <p style='font-size: 18px;'>Отвечено: <b>{answered}</b></p>
                <p style='font-size: 18px; color: #e74c3c;'>Правильных ответов: <b>0/{answered}</b></p>
                <p style='font-size: 18px;'>Пропущено: <b>{skipped}</b></p>
                <p style='font-size: 18px;'>Итоговый счет: <b>{self.score}</b></p>
                <p style='font-size: 18px;'>Процент правильных: <b>{percentage:.1f}%</b></p>
            </div>

            <p style='font-size: 18px; color: #7f8c8d; margin-top: 20px;'>
                Уровень <span style='color: {self.get_difficulty_color()}; font-weight: bold;'>{self.get_difficulty_name()}</span> оказался слишком сложным.<br>
                Попробуйте уровень <span style='color: #27ae60; font-weight: bold;'>ПРОСТОЙ</span> для начала!
            </p>
        </div>
        """

    def get_regular_results_text(self, answered, skipped, correct, percentage):
        """Текст для обычных результатов"""
        # Определяем оценку
        if percentage >= 90:
            grade = "ОТЛИЧНО"
            grade_color = "#27ae60"
            emoji = "🏆"
            message = "ВЫ ГЕНИЙ! БЛЕСТЯЩИЙ РЕЗУЛЬТАТ!"
        elif percentage >= 70:
            grade = "ХОРОШО"
            grade_color = "#f39c12"
            emoji = "👍"
            message = "ОТЛИЧНАЯ РАБОТА! ВЫ МОЛОДЕЦ!"
        elif percentage >= 50:
            grade = "УДОВЛЕТВОРИТЕЛЬНО"
            grade_color = "#3498db"
            emoji = "😊"
            message = "НЕПЛОХО! ТАК ДЕРЖАТЬ!"
        else:
            grade = "НУЖНО ПОДУЧИТЬ"
            grade_color = "#e74c3c"
            emoji = "📚"
            message = "ЕСТЬ КУДА СТРЕМИТЬСЯ!"

        return f"""
        <div style='text-align: center;'>
            <h1 style='color: {grade_color};'>{emoji} {message} {emoji}</h1>
            <div style='font-size: 60px; margin: 20px;'>{emoji}</div>

            <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px; border: 2px solid {grade_color};'>
                <p style='font-size: 22px; color: {grade_color};'><b>ОЦЕНКА: {grade}</b></p>
                <p style='font-size: 20px;'>Уровень сложности: <b style='color: {self.get_difficulty_color()};'>{self.get_difficulty_name()}</b></p>

                <div style='display: flex; justify-content: center; gap: 30px; margin: 20px 0; flex-wrap: wrap;'>
                    <div style='text-align: center; min-width: 120px;'>
                        <div style='font-size: 32px; font-weight: bold; color: {grade_color};'>{self.score}</div>
                        <div style='font-size: 14px; color: #7f8c8d;'>Итоговый счет</div>
                    </div>

                    <div style='text-align: center; min-width: 120px;'>
                        <div style='font-size: 32px; font-weight: bold; color: #3498db;'>{correct}/{answered}</div>
                        <div style='font-size: 14px; color: #7f8c8d;'>Правильные ответы</div>
                    </div>

                    <div style='text-align: center; min-width: 120px;'>
                        <div style='font-size: 32px; font-weight: bold; color: #9b59b6;'>{percentage:.1f}%</div>
                        <div style='font-size: 14px; color: #7f8c8d;'>Эффективность</div>
                    </div>

                    <div style='text-align: center; min-width: 120px;'>
                        <div style='font-size: 32px; font-weight: bold; color: #{'2ecc71' if skipped == 0 else 'f39c12' if skipped < 3 else 'e74c3c'};'>{skipped}</div>
                        <div style='font-size: 14px; color: #7f8c8d;'>Пропущено</div>
                    </div>
                </div>

                <p style='font-size: 16px; color: #7f8c8d; margin-top: 10px;'>
                    Всего вопросов: <b>{self.total_questions}</b> | 
                    Отвечено: <b>{answered}</b> | 
                    Уровень: <b style='color: {self.get_difficulty_color()};'>{self.get_difficulty_name()}</b>
                </p>
            </div>

            <div style='font-size: 18px; color: #7f8c8d; margin-top: 20px; padding: 15px; background-color: #f0f8ff; border-radius: 8px;'>
                {'🎯 Вы мастер этой викторины! Можете попробовать уровень СЛОЖНЫЙ!' if percentage >= 90 else
        '👍 Отличный результат! Можете попробовать уровень СРЕДНИЙ!' if percentage >= 70 else
        '💪 Хорошая попытка! Продолжайте тренироваться!' if percentage >= 50 else
        '📚 Рекомендуем начать с уровня ПРОСТОЙ для лучшего результата!'}
            </div>
        </div>
        """

    def restart_with_difficulty(self):
        """Перезапуск с выбором уровня сложности"""
        # Закрываем текущее окно
        self.close()

        # Создаем новое приложение
        new_app = QuizApp()
        new_app.show()

    def restart_quiz(self):
        """Перезапуск викторины с тем же уровнем сложности"""
        random.shuffle(self.filtered_questions)
        self.current_question = 0
        self.score = 0
        self.correct_answers = 0
        self.skipped_questions = 0
        self.user_answer = None

        self.score_label.setText(f"🏆 Счет: {self.score}")
        self.score_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 8px 15px;
            background-color: #fffacd;
            border-radius: 15px;
            border: 2px solid #f39c12;
        """)
        self.skipped_label.setText(f"⏭️ Пропущено: {self.skipped_questions}")

        # Восстанавливаем видимость элементов
        for btn in self.option_buttons:
            btn.setVisible(True)
        self.next_btn.setVisible(True)
        self.skip_btn.setVisible(True)
        self.hint_btn.setVisible(self.difficulty == "easy")
        self.hint_btn.setEnabled(self.difficulty == "easy")
        self.question_difficulty_label.setVisible(True)

        self.show_question()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    palette.setColor(QPalette.WindowText, QColor(44, 62, 80))
    app.setPalette(palette)

    window = QuizApp()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()