"""
Movie Library - Личная кинотека
GUI-приложение для хранения информации о фильмах с фильтрацией

Автор: Гайсар Исмагилов (GaisarNurminskiy)
GitHub: https://github.com/GaisarNurminskiy/Movie-Library-
Лицензия: MIT
Версия: 2.0
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# Константа для имени файла с данными
MOVIES_FILE = 'movies.json'


class MovieLibrary:
    """
    Основной класс приложения Movie Library.
    Управляет интерфейсом, данными, фильтрацией и валидацией.
    """
    
    def __init__(self, root):
        """
        Инициализация приложения.
        
        Args:
            root: корневое окно tkinter
        """
        self.root = root
        self.root.title("Movie Library - Личная кинотека")
        self.root.geometry("900x650")
        self.root.resizable(True, True)
        
        # Центрирование окна на экране
        self.center_window()
        
        # Загрузка данных из JSON
        self.movies = self.load_movies()
        
        # Создание всех элементов интерфейса
        self.create_menu()
        self.create_input_frame()
        self.create_table_frame()
        self.create_filter_frame()
        self.create_status_bar()
        
        # Обновление отображения таблицы
        self.refresh_table()
    
    def center_window(self):
        """Центрирует окно приложения на экране."""
        self.root.update_idletasks()
        width = 900
        height = 650
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def load_movies(self):
        """
        Загружает список фильмов из JSON-файла.
        
        Returns:
            list: Список фильмов или пустой список при ошибке
        """
        try:
            with open(MOVIES_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            # Файл не существует - возвращаем пустой список
            return []
        except json.JSONDecodeError:
            # Файл повреждён
            messagebox.showerror("Ошибка", "Файл movies.json повреждён. Будет создан новый файл.")
            return []
    
    def save_movies(self):
        """
        Сохраняет текущий список фильмов в JSON-файл.
        
        Returns:
            bool: True при успешном сохранении, False при ошибке
        """
        try:
            with open(MOVIES_FILE, 'w', encoding='utf-8') as file:
                json.dump(self.movies, file, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
            return False
    
    def validate_input(self):
        """
        Проверяет корректность введённых данных.
        
        Returns:
            bool: True если все данные валидны, иначе False
        """
        title = self.entry_title.get().strip()
        genre = self.entry_genre.get().strip()
        year = self.entry_year.get().strip()
        rating = self.entry_rating.get().strip()
        
        # Проверка на пустые обязательные поля
        if not title:
            messagebox.showerror("Ошибка", "Название фильма не может быть пустым!")
            return False
        
        if not genre:
            messagebox.showerror("Ошибка", "Жанр не может быть пустым!")
            return False
        
        # Проверка года (должен быть числом)
        if not year:
            messagebox.showerror("Ошибка", "Год выпуска не может быть пустым!")
            return False
        
        if not year.isdigit():
            messagebox.showerror("Ошибка", "Год должен быть целым числом!")
            return False
        
        year_num = int(year)
        current_year = 2026
        if not (1800 <= year_num <= current_year):
            messagebox.showerror("Ошибка", f"Год должен быть от 1800 до {current_year}!")
            return False
        
        # Проверка рейтинга
        if not rating:
            messagebox.showerror("Ошибка", "Рейтинг не может быть пустым!")
            return False
        
        try:
            rating_num = float(rating)
            if not (0 <= rating_num <= 10):
                messagebox.showerror("Ошибка", "Рейтинг должен быть от 0 до 10!")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Рейтинг должен быть числом (например, 8.5)!")
            return False
        
        return True
    
    def add_movie(self):
        """
        Добавляет новый фильм в библиотеку.
        Выполняет валидацию, проверку на дубликаты, сохраняет и обновляет таблицу.
        """
        if not self.validate_input():
            return
        
        title = self.entry_title.get().strip()
        genre = self.entry_genre.get().strip()
        year = int(self.entry_year.get().strip())
        rating = float(self.entry_rating.get().strip())
        
        # Проверка на дубликат (одинаковое название и год)
        for movie in self.movies:
            if movie["title"].lower() == title.lower() and movie["year"] == year:
                if not messagebox.askyesno("Дубликат", 
                    f"Фильм '{title}' ({year}) уже существует.\nДобавить всё равно?"):
                    return
                break
        
        # Создание записи о фильме
        movie = {
            "title": title,
            "genre": genre,
            "year": year,
            "rating": rating
        }
        
        self.movies.append(movie)
        
        if self.save_movies():
            self.refresh_table()
            self.clear_fields()
            self.update_filter_lists()
            self.update_status_bar()
            messagebox.showinfo("Успех", f"Фильм '{title}' успешно добавлен!")
    
    def delete_movie(self):
        """Удаляет выбранный фильм из библиотеки."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите фильм для удаления!")
            return
        
        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот фильм?"):
            return
        
        # Получение данных выбранного фильма
        item = self.tree.item(selected[0])
        movie_title = item['values'][0]
        movie_year = item['values'][2]
        
        # Поиск и удаление фильма
        for i, movie in enumerate(self.movies):
            if movie["title"] == movie_title and movie["year"] == movie_year:
                del self.movies[i]
                break
        
        if self.save_movies():
            self.refresh_table()
            self.update_filter_lists()
            self.update_status_bar()
            messagebox.showinfo("Успех", f"Фильм '{movie_title}' удалён!")
    
    def refresh_table(self, filter_genre=None, filter_year=None):
        """
        Обновляет таблицу с учётом активных фильтров.
        
        Args:
            filter_genre (str, optional): Фильтр по жанру
            filter_year (str, optional): Фильтр по году
        """
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Применение фильтров
        filtered_movies = self.movies.copy()
        
        if filter_genre and filter_genre != "Все":
            filtered_movies = [m for m in filtered_movies 
                              if m["genre"].lower() == filter_genre.lower()]
        
        if filter_year and filter_year != "Все":
            try:
                year_int = int(filter_year)
                filtered_movies = [m for m in filtered_movies 
                                  if m["year"] == year_int]
            except ValueError:
                pass
        
        # Заполнение таблицы
        for movie in filtered_movies:
            self.tree.insert("", "end", values=(
                movie["title"],
                movie["genre"],
                movie["year"],
                f"{movie['rating']:.1f}"
            ))
        
        # Обновление счётчика
        self.update_status_bar(len(filtered_movies))
    
    def apply_filters(self):
        """Применяет выбранные фильтры к таблице."""
        genre = self.filter_genre_var.get()
        year = self.filter_year_var.get()
        self.refresh_table(genre, year)
    
    def reset_filters(self):
        """Сбрасывает все фильтры и показывает все фильмы."""
        self.filter_genre_var.set("Все")
        self.filter_year_var.set("Все")
        self.refresh_table()
    
    def search_movie(self):
        """Выполняет поиск фильма по названию."""
        search_term = self.search_entry.get().strip().lower()
        
        if not search_term:
            self.refresh_table()
            return
        
        # Поиск совпадений
        filtered_movies = [m for m in self.movies 
                          if search_term in m["title"].lower()]
        
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Отображение результатов
        for movie in filtered_movies:
            self.tree.insert("", "end", values=(
                movie["title"],
                movie["genre"],
                movie["year"],
                f"{movie['rating']:.1f}"
            ))
        
        self.update_status_bar(len(filtered_movies))
    
    def clear_search(self):
        """Очищает поле поиска и показывает все фильмы."""
        self.search_entry.delete(0, tk.END)
        self.refresh_table()
    
    def clear_fields(self):
        """Очищает все поля ввода на форме добавления."""
        self.entry_title.delete(0, tk.END)
        self.entry_genre.delete(0, tk.END)
        self.entry_year.delete(0, tk.END)
        self.entry_rating.delete(0, tk.END)
        # Установка фокуса на поле названия
        self.entry_title.focus()
    
    def update_filter_lists(self):
        """Обновляет выпадающие списки для фильтров (жанры и годы)."""
        # Уникальные жанры
        genres = sorted(set([m["genre"] for m in self.movies]))
        genres.insert(0, "Все")
        self.filter_genre_combo['values'] = genres
        
        # Уникальные годы (от новых к старым)
        years = sorted(set([m["year"] for m in self.movies]), reverse=True)
        years.insert(0, "Все")
        self.filter_year_combo['values'] = years
    
    def update_status_bar(self, count=None):
        """Обновляет текст в строке состояния."""
        if count is None:
            count = len(self.movies)
        self.status_label.config(text=f"📊 Всего фильмов в библиотеке: {count}")
    
    def show_about(self):
        """Показывает информацию о программе."""
        about_text = """Movie Library v2.0
Личная кинотека

Автор: Гайсар Исмагилов
GitHub: GaisarNurminskiy

Программа для управления коллекцией фильмов
с возможностью фильтрации и сохранения данных.

Особенности:
• Добавление, удаление фильмов
• Фильтрация по жанру и году
• Поиск по названию
• Автосохранение в JSON
• Валидация ввода данных

Лицензия: MIT"""
        messagebox.showinfo("О программе", about_text)
    
    def create_menu(self):
        """Создаёт главное меню приложения."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Очистить все поля", command=self.clear_fields)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Меню "Помощь"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
    
    def create_input_frame(self):
        """Создаёт форму для ввода данных о фильме."""
        input_frame = tk.LabelFrame(self.root, text="➕ Добавление нового фильма", 
                                     font=("Arial", 10, "bold"), padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Поле Название
        tk.Label(input_frame, text="Название:", width=12, anchor="w", 
                font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5)
        self.entry_title = tk.Entry(input_frame, width=40, font=("Arial", 10))
        self.entry_title.grid(row=0, column=1, padx=5, pady=5)
        self.entry_title.focus()
        
        # Поле Жанр
        tk.Label(input_frame, text="Жанр:", width=12, anchor="w",
                font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5)
        self.entry_genre = tk.Entry(input_frame, width=25, font=("Arial", 10))
        self.entry_genre.grid(row=0, column=3, padx=5, pady=5)
        
        # Поле Год выпуска
        tk.Label(input_frame, text="Год выпуска:", width=12, anchor="w",
                font=("Arial", 10)).grid(row=1, column=0, padx=5, pady=5)
        self.entry_year = tk.Entry(input_frame, width=15, font=("Arial", 10))
        self.entry_year.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Поле Рейтинг
        tk.Label(input_frame, text="Рейтинг (0-10):", width=12, anchor="w",
                font=("Arial", 10)).grid(row=1, column=2, padx=5, pady=5)
        self.entry_rating = tk.Entry(input_frame, width=15, font=("Arial", 10))
        self.entry_rating.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        
        # Кнопки действий
        btn_frame = tk.Frame(input_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        tk.Button(btn_frame, text="➕ Добавить фильм", command=self.add_movie,
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), 
                 padx=15, pady=3).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🗑️ Удалить выбранный", command=self.delete_movie,
                 bg="#F44336", fg="white", font=("Arial", 10, "bold"),
                 padx=15, pady=3).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🧹 Очистить поля", command=self.clear_fields,
                 bg="#FF9800", fg="white", font=("Arial", 10, "bold"),
                 padx=15, pady=3).pack(side="left", padx=5)
    
    def create_table_frame(self):
        """Создаёт таблицу для отображения списка фильмов."""
        table_frame = tk.LabelFrame(self.root, text="📋 Список фильмов", 
                                     font=("Arial", 10, "bold"), padx=10, pady=5)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Строка поиска
        search_frame = tk.Frame(table_frame)
        search_frame.pack(fill="x", pady=5)
        
        tk.Label(search_frame, text="🔍 Поиск по названию:", font=("Arial", 10)).pack(side="left", padx=5)
        self.search_entry = tk.Entry(search_frame, width=30, font=("Arial", 10))
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_movie())
        tk.Button(search_frame, text="Искать", command=self.search_movie,
                 bg="#2196F3", fg="white").pack(side="left", padx=2)
        tk.Button(search_frame, text="Сброс", command=self.clear_search,
                 bg="#9E9E9E", fg="white").pack(side="left", padx=2)
        
        # Таблица
        columns = ("Название", "Жанр", "Год", "Рейтинг")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Настройка заголовков
        self.tree.heading("Название", text="Название")
        self.tree.heading("Жанр", text="Жанр")
        self.tree.heading("Год", text="Год")
        self.tree.heading("Рейтинг", text="Рейтинг")
        
        # Настройка ширины колонок
        self.tree.column("Название", width=350)
        self.tree.column("Жанр", width=180)
        self.tree.column("Год", width=100)
        self.tree.column("Рейтинг", width=100)
        
        # Скроллбары
        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Размещение
        self.tree.pack(fill="both", expand=True, pady=5)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        
        # Двойной клик для редактирования (опционально)
        # self.tree.bind("<Double-Button-1>", lambda e: self.edit_movie())
    
    def create_filter_frame(self):
        """Создаёт панель фильтрации."""
        filter_frame = tk.LabelFrame(self.root, text="🔍 Фильтрация", 
                                      font=("Arial", 10, "bold"), padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтр по жанру
        tk.Label(filter_frame, text="Фильтр по жанру:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        genres = ["Все"]
        if self.movies:
            genres.extend(sorted(set([m["genre"] for m in self.movies])))
        
        self.filter_genre_var = tk.StringVar(value="Все")
        self.filter_genre_combo = ttk.Combobox(filter_frame, textvariable=self.filter_genre_var,
                                               values=genres, width=20, state="readonly")
        self.filter_genre_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Фильтр по году
        tk.Label(filter_frame, text="Фильтр по году:", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        
        years = ["Все"]
        if self.movies:
            years.extend(sorted(set([m["year"] for m in self.movies]), reverse=True))
        
        self.filter_year_var = tk.StringVar(value="Все")
        self.filter_year_combo = ttk.Combobox(filter_frame, textvariable=self.filter_year_var,
                                              values=years, width=15, state="readonly")
        self.filter_year_combo.grid(row=0, column=3, padx=5, pady=5)
        
        # Кнопки фильтрации
        tk.Button(filter_frame, text="✅ Применить фильтр", command=self.apply_filters,
                 bg="#2196F3", fg="white", font=("Arial", 10, "bold")).grid(row=0, column=4, padx=10, pady=5)
        tk.Button(filter_frame, text="🔄 Сбросить фильтры", command=self.reset_filters,
                 bg="#9E9E9E", fg="white", font=("Arial", 10, "bold")).grid(row=0, column=5, padx=5, pady=5)
    
    def create_status_bar(self):
        """Создаёт строку состояния внизу окна."""
        self.status_label = tk.Label(self.root, text="📊 Всего фильмов в библиотеке: 0",
                                     relief="sunken", anchor="w", font=("Arial", 9))
        self.status_label.pack(side="bottom", fill="x")


def main():
    """
    Главная функция запуска приложения.
    Создаёт корневое окно, инициализирует приложение и запускает главный цикл.
    """
    # Создание корневого окна
    root = tk.Tk()
    
    # Инициализация приложения
    app = MovieLibrary(root)
    
    # Запуск главного цикла обработки событий
    root.mainloop()


# Точка входа в программу
if __name__ == "__main__":
    main()
