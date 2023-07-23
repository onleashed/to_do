import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel
from tkcalendar import DateEntry
import json
from datetime import datetime
from operator import itemgetter
from collections import defaultdict


class App:
    def __init__(self, root):
        self.root = root
        root.title("Задачник")
        root.state('zoomed')
        root.iconbitmap('icon.ico')
        root.grid_rowconfigure(0, weight=1)

        self.task_label = tk.Label(root, text="Задача")
        self.task_label.grid(row=0, column=0)

        self.task_entry = tk.Entry(root, width=50)
        self.task_entry.grid(row=1, column=0)

        self.description_label = tk.Label(root, text="Описание задачи")
        self.description_label.grid(row=2, column=0)

        self.description_entry = tk.Entry(root, width=50)
        self.description_entry.grid(row=3, column=0)

        self.assignee_label = tk.Label(root, text="Исполнитель")
        self.assignee_label.grid(row=4, column=0)

        self.assignee_var = tk.StringVar()
        self.assignee_entry = tk.OptionMenu(root, self.assignee_var, "")
        self.assignee_entry.grid(row=5, column=0)

        self.deadline_label = tk.Label(root, text="Срок выполнения")
        self.deadline_label.grid(row=6, column=0)

        self.deadline_entry = DateEntry(root, width=50)
        self.deadline_entry.grid(row=7, column=0)

        self.add_task_button = tk.Button(root, text="Добавить задачу", command=self.add_task)
        self.add_task_button.grid(row=8, column=0)

        self.filter_label = tk.Label(root, text="Фильтр по исполнителю")
        self.filter_label.grid(row=0, column=1)

        self.filter_entry = tk.Entry(root, width=40)
        self.filter_entry.grid(row=1, column=1, sticky='w')

        self.filter_button = tk.Button(root, text="Применить фильтр", command=self.update_tasks_listbox)
        self.filter_button.grid(row=1, column=1)

        self.clear_filter_button = tk.Button(root, text="Сбросить фильтр", command=self.clear_filter)
        self.clear_filter_button.grid(row=1, column=1, sticky='e')

        self.tasks_listbox = tk.Listbox(root, width=100, height=30)
        self.tasks_listbox.grid(row=2, column=1, rowspan=8, sticky='ns')
        self.tasks_listbox.bind('<Double-1>', self.edit_task)

        self.tasks = []

    def add_task(self):
        task = self.task_entry.get()
        assignee = self.assignee_var.get()
        deadline = self.deadline_entry.get_date()
        description = self.description_entry.get()

        if task == "" or assignee == "" or not deadline or description == "":
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
            return

        task_data = {
            'task': task,
            'assignee': assignee,
            'deadline': deadline.strftime("%Y-%m-%d"),
            'description': description,
            'time_added': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'completed': False
        }

        with open('tasks.json', 'a') as f:
            json.dump(task_data, f)
            f.write('\n')

        self.task_entry.delete(0, 'end')
        self.description_entry.delete(0, 'end')

        self.update_assignee_options()  # Обновить список исполнителей
        self.update_tasks_listbox()

    def clear_filter(self):
        self.filter_entry.delete(0, 'end')
        self.update_tasks_listbox()

    def edit_task(self, event):
        index = self.tasks_listbox.curselection()[0]
        task_data = self.tasks[index]

        edit_window = Toplevel(self.root)
        edit_window.title("Редактирование задачи")

        tk.Label(edit_window, text="Задача").grid(row=0, column=0)
        task_entry = tk.Entry(edit_window, width=50)
        task_entry.grid(row=0, column=1)
        task_entry.insert(0, task_data['task'])

        tk.Label(edit_window, text="Описание задачи").grid(row=1, column=0)
        description_entry = tk.Entry(edit_window, width=50)
        description_entry.grid(row=1, column=1)
        description_entry.insert(0, task_data['description'])

        tk.Label(edit_window, text="Исполнитель").grid(row=2, column=0)
        assignee_var = tk.StringVar(edit_window)
        assignee_entry = tk.OptionMenu(edit_window, assignee_var, *self.get_assignee_list())
        assignee_entry.grid(row=2, column=1)
        assignee_var.set(task_data['assignee'])

        tk.Label(edit_window, text="Срок выполнения").grid(row=3, column=0)
        deadline_entry = DateEntry(edit_window, width=50)
        deadline_entry.grid(row=3, column=1)
        deadline_entry.set_date(datetime.strptime(task_data['deadline'], "%Y-%m-%d"))

        def save_changes():
            task_data['task'] = task_entry.get()
            task_data['description'] = description_entry.get()
            task_data['assignee'] = assignee_var.get()
            task_data['deadline'] = deadline_entry.get_date().strftime("%Y-%m-%d")

            self.update_assignee_options()
            self.update_tasks_file()
            self.update_tasks_listbox()
            edit_window.destroy()

        save_button = tk.Button(edit_window, text="Сохранить изменения", command=save_changes)
        save_button.grid(row=4, column=1)

    def update_tasks_listbox(self):
        self.tasks_listbox.delete(0, 'end')

        filter_assignee = self.filter_entry.get()

        try:
            with open('tasks.json', 'r') as f:
                lines = f.readlines()

                self.tasks = [json.loads(line) for line in lines]

                if filter_assignee:
                    self.tasks = [task for task in self.tasks if task['assignee'] == filter_assignee]

                self.tasks.sort(key=itemgetter('deadline', 'assignee'))

                grouped_tasks = defaultdict(list)
                for task in self.tasks:
                    grouped_tasks[task['deadline']].append(task)

                for date, tasks in grouped_tasks.items():
                    self.tasks_listbox.insert('end', date)
                    for task in tasks:
                        self.tasks_listbox.insert('end', f"{task['assignee']} - {task['task']} ({'завершено' if task['completed'] else 'не завершено'})")

        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Нет задач для отображения")

    def update_tasks_file(self):
        with open('tasks.json', 'w') as f:
            for task in self.tasks:
                json.dump(task, f)
                f.write('\n')

    def update_assignee_options(self):
        menu = self.assignee_entry["menu"]
        menu.delete(0, "end")
        assignees = self.get_assignee_list()
        for assignee in assignees:
            menu.add_command(label=assignee, command=tk._setit(self.assignee_var, assignee))
        if assignees:
            self.assignee_var.set(assignees[0])

    def get_assignee_list(self):
        assignees = []
        try:
            with open('tasks.json', 'r') as f:
                lines = f.readlines()
                tasks = [json.loads(line) for line in lines]
                assignees = list(set([task['assignee'] for task in tasks]))
        except FileNotFoundError:
            pass
        return assignees


root = tk.Tk()
app = App(root)
root.mainloop()
