import tkinter as tk
from tkinter import ttk
import os
import subprocess
from pathlib import Path
import json

class CheckListApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Чек-лист системы")
        self.root.geometry("800x600")
        
        # Загружаем конфигурацию
        self.load_config()
        
        # Создаем интерфейс
        self.setup_ui()
        
        # Запускаем проверку
        self.check_all()
    
    def load_config(self):
        """Загружаем конфигурацию из файла или используем стандартную"""
        try:
            with open('checklist_config.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except:
            # Стандартная конфигурация
            self.config = {
                "folders": [
                    {"name": "Папка Documents", "path": os.path.expanduser("~/Documents")},
                    {"name": "Папка Downloads", "path": os.path.expanduser("~/Downloads")},
                    {"name": "C:\\Program Files", "path": "C:\\Program Files"},
                    {"name": "C:\\Temp", "path": "C:\\Temp"}
                ],
                "programs": [
                    {"name": "Google Chrome", "exe": "chrome.exe", "paths": [
                        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
                    ]},
                    {"name": "Notepad++", "exe": "notepad++.exe", "paths": [
                        "C:\\Program Files\\Notepad++\\notepad++.exe",
                        "C:\\Program Files (x86)\\Notepad++\\notepad++.exe"
                    ]},
                    {"name": "7-Zip", "exe": "7z.exe", "paths": [
                        "C:\\Program Files\\7-Zip\\7z.exe",
                        "C:\\Program Files (x86)\\7-Zip\\7z.exe"
                    ]},
                    {"name": "Python", "exe": "python.exe", "command": "python --version"},
                    {"name": "Git", "exe": "git.exe", "command": "git --version"}
                ]
            }
            # Сохраняем конфигурацию для возможности редактирования
            self.save_config()
    
    def save_config(self):
        """Сохраняем конфигурацию в файл"""
        with open('checklist_config.json', 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def setup_ui(self):
        """Создаем интерфейс"""
        # Заголовок
        header = tk.Label(self.root, text="Проверка системы", 
                         font=("Arial", 16, "bold"))
        header.pack(pady=10)
        
        # Кнопки управления
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)
        
        refresh_btn = tk.Button(button_frame, text="🔄 Обновить", 
                               command=self.check_all, font=("Arial", 10))
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Создаем таблицу
        self.create_table()
        
        # Статус бар
        self.status_label = tk.Label(self.root, text="Готово", 
                                    relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_table(self):
        """Создаем таблицу с результатами"""
        # Фрейм для таблицы с прокруткой
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Прокрутка
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Создаем Treeview
        self.tree = ttk.Treeview(table_frame, 
                                 columns=("Type", "Name", "Path", "Status"),
                                 show="tree headings",
                                 yscrollcommand=scrollbar.set)
        
        # Настраиваем столбцы
        self.tree.heading("#0", text="№")
        self.tree.heading("Type", text="Тип")
        self.tree.heading("Name", text="Название")
        self.tree.heading("Path", text="Путь/Описание")
        self.tree.heading("Status", text="Статус")
        
        self.tree.column("#0", width=50)
        self.tree.column("Type", width=100)
        self.tree.column("Name", width=200)
        self.tree.column("Path", width=350)
        self.tree.column("Status", width=80)
        
        scrollbar.config(command=self.tree.yview)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Создаем теги для цветов
        self.tree.tag_configure("found", background="#90EE90")  # Светло-зеленый
        self.tree.tag_configure("notfound", background="#FFB6C1")  # Светло-красный
    
    def check_folder(self, folder_path):
        """Проверка существования папки"""
        return os.path.exists(folder_path) and os.path.isdir(folder_path)
    
    def check_program_by_path(self, paths):
        """Проверка программы по списку путей"""
        for path in paths:
            if os.path.exists(path) and os.path.isfile(path):
                return True, path
        return False, ""
    
    def check_program_by_command(self, command):
        """Проверка программы через командную строку"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, 
                                  timeout=2, text=True)
            if result.returncode == 0:
                return True, "Найдено в PATH"
            return False, ""
        except:
            return False, ""
    
    def check_all(self):
        """Выполняем все проверки"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.status_label.config(text="Выполняется проверка...")
        self.root.update()
        
        item_num = 1
        
        # Проверяем папки
        for folder in self.config["folders"]:
            exists = self.check_folder(folder["path"])
            status = "✓ Найдено" if exists else "✗ Не найдено"
            tag = "found" if exists else "notfound"
            
            self.tree.insert("", tk.END, text=str(item_num),
                           values=("Папка", folder["name"], folder["path"], status),
                           tags=(tag,))
            item_num += 1
        
        # Проверяем программы
        for program in self.config["programs"]:
            found = False
            found_path = ""
            
            # Проверяем по путям
            if "paths" in program:
                found, found_path = self.check_program_by_path(program["paths"])
            
            # Проверяем через команду
            if not found and "command" in program:
                found, found_path = self.check_program_by_command(program["command"])
            
            status = "✓ Найдено" if found else "✗ Не найдено"
            tag = "found" if found else "notfound"
            path_display = found_path if found_path else "Не установлено"
            
            self.tree.insert("", tk.END, text=str(item_num),
                           values=("Программа", program["name"], path_display, status),
                           tags=(tag,))
            item_num += 1
        
        self.status_label.config(text="Проверка завершена")

def main():
    root = tk.Tk()
    app = CheckListApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
