import tkinter as tk
from tkinter import ttk
import json #использовали, чтобы сэкономить время, у нас тесты хранились в словарях было проще переформатировать
import os


# Класс для хранения одного вопроса теста
class Question:
    def __init__(self, text, variants, correct_answer):
        self.text = text
        self.variants = variants
        self.correct_answer = correct_answer

    # Проверка правильности ответа
    def check_answer(self, answer):
        return answer == self.correct_answer


# Класс для хранения целого теста (набора вопросов)
class Test:
    def __init__(self, name, questions=None):
        self.name = name
        if questions is None:
            self.questions = []
        else:
            self.questions = questions

    # Добавить вопрос в тест
    def add_question(self, question):
        self.questions.append(question)

    # Получить вопрос по номеру
    def get_question(self, index):
        if 0 <= index < len(self.questions):
            return self.questions[index]
        return None

    # Узнать общее количество вопросов
    def get_total_questions(self):
        return len(self.questions)


# Класс для хранения результатов прохождения теста
class TestResult:
    def __init__(self, test_name):
        self.test_name = test_name
        self.answers = []
        self.correct_count = 0
    # Добавить ответ пользователя
    def add_answer(self, question, user_answer):
        is_correct = question.check_answer(user_answer)
        answer_dict = {
            "question": question.text,
            "user_answer": user_answer,
            "correct_answer": question.correct_answer,
            "is_correct": is_correct
        }
        self.answers.append(answer_dict)
        if is_correct:
            self.correct_count += 1


# Главный класс приложения
class TestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Тестирование")
        self.root.geometry("500x400")

        self.tests_file = "tests.json"

        self.tests = []
        self.current_test = None
        self.current_question_index = 0
        self.current_result = None
        self.selected_answer = tk.StringVar()

        self.load_tests_from_file()
        self.show_menu()

    # Загрузка тестов из JSON файла
    def load_tests_from_file(self):
        if os.path.exists(self.tests_file):
            f = open(self.tests_file, "r", encoding="utf-8")
            data = json.load(f)
            f.close()

            for test_data in data:
                test = Test(test_data["name"])
                for q in test_data["questions"]:
                    question = Question(q["question"], q["variants"], q["correct_answer"])
                    test.add_question(question)
                self.tests.append(test)

    # Очистка экрана от всех элементов
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # Показать главное меню с выбором теста
    def show_menu(self):
        self.clear_screen()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text="Выберите тест").pack(pady=20)

        # Создаем кнопку для каждого теста
        for i in range(len(self.tests)):
            test = self.tests[i]
            btn = ttk.Button(frame, text=f"{i + 1}. {test.name}", width=30, command=lambda t=test: self.begin_test(t))
            btn.pack(pady=5)

        ttk.Label(frame, text="").pack(pady=10)
        ttk.Button(frame, text="Выход", width=30, command=self.root.quit).pack(pady=5)

    # Начать прохождение выбранного теста
    def begin_test(self, test):
        self.current_test = test
        self.current_question_index = 0
        self.current_result = TestResult(test.name)
        self.display_question()


    def display_question(self):
        self.clear_screen()

        question = self.current_test.get_question(self.current_question_index)

        # Если вопросов больше нет, показываем результаты
        if question is None:
            self.show_results()
            return

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)

        # Заголовок с информацией о тесте и номере вопроса
        header = "Тест: " + self.current_test.name + " | Вопрос " + str(self.current_question_index + 1) + " из " + str(
            self.current_test.get_total_questions())
        ttk.Label(frame, text=header).pack(pady=10)


        ttk.Label(frame, text=question.text).pack(pady=20)

        # Радиокнопки с вариантами ответов, чтобы пользователь мог выбрать только один вариант
        self.selected_answer.set("")
        for variant in question.variants:
            rb = ttk.Radiobutton(frame, text=variant, value=variant, variable=self.selected_answer)
            rb.pack(pady=5)

        # Метка для сообщений об ошибках
        self.error_label = ttk.Label(frame, text="")
        self.error_label.pack(pady=5)

        ttk.Button(frame, text="Ответить", command=self.check_answer).pack(pady=20)

    # Проверка ответа пользователя
    def check_answer(self):
        answer = self.selected_answer.get()

        if not answer:
            self.error_label.config(text="Выберите вариант ответа")
            return

        question = self.current_test.get_question(self.current_question_index)
        self.current_result.add_answer(question, answer)
        self.current_question_index = self.current_question_index + 1
        self.display_question()

    def show_results(self):
        self.clear_screen()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text="Тест завершён").pack(pady=10)


        result_text = "Правильных ответов: " + str(self.current_result.correct_count) + " из " + str(
            len(self.current_result.answers))
        ttk.Label(frame, text=result_text).pack(pady=10)

        ttk.Label(frame, text="Подробности:").pack(pady=10)

        # Детальная информация по каждому вопросу
        details_frame = ttk.Frame(frame)
        details_frame.pack()

        for ans in self.current_result.answers:
            if ans["is_correct"]:
                text = "+ " + ans['question']
            else:
                text = "- " + ans['question']
            lbl = ttk.Label(details_frame, text=text)
            lbl.pack(anchor="w")

        ttk.Button(frame, text="В главное меню", command=self.show_menu).pack(pady=20)

root = tk.Tk()
app = TestApp(root)
root.mainloop()
