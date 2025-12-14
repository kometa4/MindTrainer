import tkinter as tk
from tkinter import ttk
import json #использовали, чтобы сэкономить время, у нас тесты хранились в словарях было проще переформатировать
import os
import csv
import datetime
from pathlib import Path

# Класс для хранения одного вопроса теста
class Question:

    def __init__(self, text, variants, correct_answer, hint, user_answer = None):
        self.text = text
        self.variants = variants
        self.correct_answer = correct_answer
        self.user_answer = user_answer

    # Ответ пользователя храним в атрибуте класса
    def add_answer(self, answer):
        self.user_answer = answer

    # Проверка правильности ответа
    def check_answer(self):
        return self.user_answer == self.correct_answer

class Test:

    def __init__(self, name, is_recovered=False, questions=None):
        self.name = name
        self.correct_count = 0
        self.is_recovered = is_recovered

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

    def get_correct_count(self):
        return self.correct_count
    
# Классы для сохранения/загрузки файлов сохранения

class RecoveryObjectAnswer:
        
        def __init__(self, question="", user_answer=""):
            self.question = question
            self.user_answer = user_answer

        def to_dict(self):
            return {
                "question": self.question,
                "user_answer": self.user_answer
            }

class RecoveryObject:

    def __init__(self, test_name, correct_count=0, answers=[]):
        self.test_name = test_name
        self.correct_count = correct_count
        self.answers = answers

    def to_dict(self):
        return {
            "test_name": self.test_name,
            "correct_count": self.correct_count,
            "answers": [answer.to_dict() for answer in self.answers]
        }

    def add_answer(self, recovery_object_answer):
        self.answers.append(recovery_object_answer)

# Главный класс приложения
class TestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Тестирование")
        self.root.geometry("500x400")

        self.tests_file = "tests.json"
        self.stats_file = "stats.csv"

        if not os.path.isfile(self.stats_file):
            with open(self.stats_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Имя пользователя", "Категория теста", "Количество баллов"])

        self.recovery_object = None
        self.tests = []
        self.current_test = None
        self.current_question_index = 0
        self.current_result = None
        self.selected_answer = tk.StringVar()

        self.__administrator_username = 'Администратор'
        self.__administrator_password = 'Пароль'

        self.ask_username()

    def load_tests_names_from_file(self):
        with open(self.tests_file, "r", newline="", encoding="utf-8") as f:
            data = json.load(f)

        return [test['name'] for test in data]

    def load_test_by_name(self, test_name):
        with open(self.tests_file, "r", newline="", encoding="utf-8") as f:
            data = json.load(f)

        for test in data:
            if test['name'] == test_name:
                user_test = Test(test['name'])
                for question in test['questions']:
                    user_test.add_question(Question(question['question'], question['variants'],
                                                    question['correct_answer'], question['hint']))

        return user_test

    # Очистка экрана от всех элементов
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # Спросить имя пользователя для статистики
    def ask_username(self):
        self.clear_screen()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)

        label = ttk.Label(frame, text="Введите имя:")
        label.pack()

        self.entry = ttk.Entry(frame)
        self.entry.pack()

        btn = tk.Button(root, text="Подтвердить", command=self.input_username)
        btn.pack()

    # Если имя пользователя Администратор, запрашиваем пароль
    def ask_password(self):
        self.clear_screen()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)

        label = ttk.Label(frame, text="Введите пароль:")
        label.pack()

        self.entry = ttk.Entry(frame, show="*")
        self.entry.pack()

        btn = tk.Button(root, text="Подтвердить", command=self.input_password)
        btn.pack()

    # Проверяем пароль администратора
    def input_password(self):
        self.username = self.entry.get()

        if self.username == self.__administrator_password:
            self.show_admin_menu()

        else:
            self.clear_screen()

            frame = ttk.Frame(self.root, padding=20)
            frame.pack(expand=True)

            ttk.Label(frame, text="Неверный пароль администратора").pack(pady=10)
            ttk.Button(frame, text="В главное меню", command=self.ask_username).pack(pady=20)

    # Проверяем является ли пользователь администратором,
    # а также есть ли незавершенная сессия для этого пользователя иначе двигаемся в следующее меню
    def input_username(self):
        self.username = self.entry.get()

        if self.username == self.__administrator_username:
            self.ask_password()
        else:
            
            if (self.check_recovery_file()):
                print('here')
                self.ask_recovery_session(self.check_recovery_file())  # предлагаем восстановить сессию пользователя
            else:
                self.recovery_file = f'.recovery_{self.username}_{datetime.datetime.now():%d_%m_%Y_%H_%M}.json'
                with open(self.recovery_file, "w", encoding="utf-8") as f:
                    f.write('')
                    # {"test_index": "NAME", "current_index": 0, "correct_count": 0, "answers": [{"index": 0,  "question": "QUESTION",  "user_answer": "ANSWER"  } ] }
                self.show_menu()

    # Показать меню администратора со статистикой
    def show_admin_menu(self):
        self.clear_screen()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)

        ttk.Button(frame, text="В главное меню", width=30, command=self.ask_username).pack(pady=5)

        ttk.Label(frame, text="Статистика").pack(pady=20)

        tree = ttk.Treeview(frame)
        tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        with open(self.stats_file, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            rows = list(reader)

        if not rows:
            return

        header = rows[0]
        data = rows[1:]

        tree["columns"] = header
        tree["show"] = "headings"

        for col in header:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        for row in data:
            tree.insert("", tk.END, values=row)

    # Для того, чтобы из имени файла получить дату
    def date_from_filename(self, filename):
        return filename[-21:-11].replace('_', '.') + ' ' + filename[-10:-5].replace('_', ':')

    # Проверка есть ли незаконченный тест у пользователя
    def check_recovery_file(self):

        files = list(Path("./").glob(f"*{self.username}*.json"))
        print(files)
        return files
    
    def ask_recovery_session(self, recovery_files):
        self.clear_screen()
        print('now here')
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text="У вас есть одна или несколько незаконченных сессий, выберете какую восставновить:").pack(pady=20)

        for rf in recovery_files:
            btn = ttk.Button(frame, text=f"{self.date_from_filename(rf.name)}", width=30,
                             command=lambda rf=rf: print(rf.name))
            btn.pack(pady=5)
        
        btn = ttk.Button(frame, text="Не восстанавливать", width=30,
                             command=lambda rf=rf: self.dont_recovery(recovery_files))
        btn.pack(pady=5)

    #
    def dont_recovery(self, files):

        for file in files:
            Path.unlink(file.resolve())

        self.recovery_file = f'.recovery_{self.username}_{datetime.datetime.now():%d_%m_%Y_%H_%M}.json'
        
        with open(self.recovery_file, "w", encoding="utf-8") as f:
            f.write('')

        self.show_menu()

    # Показать главное меню с выбором теста
    def show_menu(self):
        self.clear_screen()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text="Выберите тест").pack(pady=20)

        # Создаем кнопку для каждого теста
        for test_name in self.load_tests_names_from_file():
            btn = ttk.Button(frame, text=f"{test_name}", width=30,
                             command=lambda t=test_name: self.begin_test(t))
            btn.pack(pady=5)

        ttk.Label(frame, text="").pack(pady=10)
        ttk.Button(frame, text="Выход", width=30, command=self.root.quit).pack(pady=5)

    def begin_test(self, test_name, is_recovered=False, current_question_index=0):
        self.current_test = self.load_test_by_name(test_name)

        if is_recovered:
            pass  # recovery session

        self.recovery_object = RecoveryObject(test_name)
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
        question.add_answer(answer)
        if question.check_answer():
            self.current_test.correct_count += 1

        self.current_question_index = self.current_question_index + 1

        self.recovery_object.add_answer(RecoveryObjectAnswer(self.current_test.get_question(self.current_question_index).text, answer))
        self.recovery_object.correct_count = self.current_test.correct_count

        with open(self.recovery_file, 'w', encoding='utf-8') as f:
            json.dump(self.recovery_object.to_dict(), f, indent=4)

        # add row in recovery file (TODO)
        #
        self.display_question()

    def show_results(self):
        self.clear_screen()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text="Тест завершён").pack(pady=10)

        result_text = "Правильных ответов: " + str(self.current_test.correct_count) + " из " + str(
            len(self.current_test.questions))
        ttk.Label(frame, text=result_text).pack(pady=10)

        self.save_results()

        ttk.Label(frame, text="Подробности:").pack(pady=10)

        # Детальная информация по каждому вопросу
        details_frame = ttk.Frame(frame)
        details_frame.pack()

        for q in self.current_test.questions:
            if q.check_answer():
                text = "+ " + q.text
            else:
                text = "- " + q.text
            lbl = ttk.Label(details_frame, text=text)
            lbl.pack(anchor="w")

        ttk.Button(frame, text="В главное меню", command=self.show_menu).pack(pady=20)

    def save_results(self):

        with open('stats.csv', 'a', newline="", encoding='utf-8') as stat_file:
            writer = csv.writer(stat_file)
            writer.writerow([self.username, self.current_test.name, str(self.current_test.correct_count)])

        os.remove(self.recovery_file)

root = tk.Tk()
app = TestApp(root)
root.mainloop()