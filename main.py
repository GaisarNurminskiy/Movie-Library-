"""
Movie Library - Личная кинотека
GUI-приложение для хранения информации о фильмах с фильтрацией
Автор: Иван Иванов
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# Константы
MOVIES_FILE = 'movies.json'

class MovieLibrary:
    """Основной класс приложения Movie Library"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library - Личная кинотека")
        self.root.geometry("850x600")
        self.root.resizable(True, True)
        
        # Загрузка данных
        self.movies = self.load_movies()
        
        # Создание интерфейса
        self.create_input_frame()
        self.create_table_frame()
        self.create_filter_frame()
        
        # Обновление таблицы
        self.refresh_table()
    
    def load_movies(self):
        """Загрузка фильмов из JSON файла"""
        try:
            with open(MOVIES_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка", "Файл movies.json поврежден")
            return []
    
    def save_movies(self):
        """Сохранение фильмов в JSON файл"""
        try:
            with open(MOVIES_FILE, 'w', encoding='utf-8') as file:
                json.dump(self.movies, file, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")
            return False
    
    def validate_input(self):
        """Проверка корректности ввода данных"""
        title = self.entry_title.get().strip()
        genre = self.entry_genre.get().strip()
        year = self.entry_year.get().strip()
        rating = self.entry_rating.get().strip()
        
        # Проверка обязательных полей
        if not title or not genre:
            messagebox.showerror("Ошибка", "Название и жанр не должны быть пустыми!")
            return False
        
        # Проверка года (должен быть числом)
        if not year.isdigit():
            messagebox.showerror("Ошибка", "Год должен быть числом!")
            return False
        
        year_num = int(year)
        if not (1800 <= year_num <= 2026):
            messagebox.showerror("Ошибка", "Год должен быть от 1800 до 2026!")
            return False
        
        # Проверка рейтинга (от 0 до 10)
        try:
            rating_num = float(rating)
            if not (0 <= rating_num <= 10):
                messagebox.showerror("Ошибка", "Рейтинг должен быть от 0 до 10!")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Рейтинг должен быть числом!")
            return False
        
        return True
    
    def add_movie(self):
        """Добавление нового фильма"""
        if not self.validate_input():
            return
        
        movie = {
            "title": self.entry_title.get().strip(),
            "genre": self.entry_genre.get().strip(),
            "year": int(self.entry_year.get().strip()),
            "rating": float(self.entry_rating.get().strip())
        }
        
        # Проверка на дубликат
        for existing in self.movies:
            if existing["title"].lower() == movie["title"].lower() and existing["year"] == movie["year"]:
                if not messagebox.askyesno("Дубликат", "Такой фильм уже существует. Добавить все равно?"):
                    return
        
        self.movies.append(movie)
        if self.save_movies():
            self.refresh_table()
            self.clear_fields()
            messagebox.showinfo("Успех", f"Фильм '{movie['title']}' добавлен!")
    
    def delete_movie(self):
        """Удаление выбранного фильма"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите фильм для удаления!")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот фильм?"):
            item = self.tree.item(selected[0])
            movie_title = item['values'][0]
            movie_year = item['values'][2]
            
            # Поиск и удаление
            for i, movie in enumerate(self.movies):
                if movie["title"] == movie_title and movie["year"] == movie_year:
                    del self.movies[i]
                    break
            
            if self.save_movies():
                self.refresh_table()
                messagebox.showinfo("Успех", f"Фильм '{movie_title}' удален!")
    
    def refresh_table(self, filter_genre=None, filter_year=None):
        """Обновление таблицы с применением фильтров"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Применение фильтров
        filtered_movies = self.movies.copy()
        
        if filter_genre and filter_genre != "Все":
            filtered_movies = [m for m in filtered_movies if m["genre"].lower() == filter_genre.lower()]
        
        if filter_year and filter_year != "Все":
            try:
                year_int = int(filter_year)
                filtered_movies = [m for m in filtered_movies if m["year"] == year_int]
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
        
        # Обновление счетчика
        self.lbl_count.config(text=f"Всего фильмов: {len(filtered_movies)}")
    
    def apply_filters(self):
        """Применение фильтров"""
        genre = self.filter_genre_var.get()
        year = self.filter_year_var.get()
        self.refresh_table(genre, year)
    
    def reset_filters(self):
        """Сброс фильтров"""
        self.filter_genre_var.set("Все")
        self.filter_year_var.set("Все")
        self.refresh_table()
    
    def clear_fields(self):
        """Очистка полей ввода"""
        self.entry_title.delete(0, tk.END)
        self.entry_genre.delete(0, tk.END)
        self.entry_year.delete(0, tk.END)
        self.entry_rating.delete(0, tk.END)
    
    def create_input_frame(self):
        """Создание формы для ввода данных"""
        input_frame = tk.LabelFrame(self.root, text="Добавление фильма", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Поле Название
        tk.Label(input_frame, text="Название:", width=15, anchor="w").grid(row=0, column=0, padx=5, pady=5)
        self.entry_title = tk.Entry(input_frame, width=40)
        self.entry_title.grid(row=0, column=1, padx=5, pady=5)
        
        # Поле Жанр
        tk.Label(input_frame, text="Жанр:", width=15, anchor="w").grid(row=0, column=2, padx=5, pady=5)
        self.entry_genre = tk.Entry(input_frame, width=30)
        self.entry_genre.grid(row=0, column=3, padx=5, pady=5)
        
        # Поле Год выпуска
        tk.Label(input_frame, text="Год выпуска:", width=15, anchor="w").grid(row=1, column=0, padx=5, pady=5)
        self.entry_year = tk.Entry(input_frame, width=20)
        self.entry_year.grid(row=1, column=1, padx=5, pady=5)
        
        # Поле Рейтинг
        tk.Label(input_frame, text="Рейтинг (0-10):", width=15, anchor="w").grid(row=1, column=2, padx=5, pady=5)
        self.entry_rating = tk.Entry(input_frame, width=20)
        self.entry_rating.grid(row=1, column=3, padx=5, pady=5)
        
        # Кнопки
        btn_frame = tk.Frame(input_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        tk.Button(btn_frame, text="Добавить фильм", command=self.add_movie, 
                 bg="#4CAF50", fg="white", padx=20).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Удалить выбранный", command=self.delete_movie,
                 bg="#F44336", fg="white", padx=20).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Очистить поля", command=self.clear_fields,
                 bg="#FF9800", fg="white", padx=20).pack(side="left", padx=5)
    
    def create_table_frame(self):
        """Создание таблицы для отображения фильмов"""
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Счетчик фильмов
        self.lbl_count = tk.Label(table_frame, text="Всего фильмов: 0", font=("Arial", 10, "bold"))
        self.lbl_count.pack(anchor="w", pady=5)
        
        # Таблица
        columns = ("Название", "Жанр", "Год", "Рейтинг")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Настройка колонок
        self.tree.heading("Название", text="Название")
        self.tree.heading("Жанр", text="Жанр")
        self.tree.heading("Год", text="Год")
        self.tree.heading("Рейтинг", text="Рейтинг")
        
        self.tree.column("Название", width=300)
        self.tree.column("Жанр", width=150)
        self.tree.column("Год", width=100)
        self.tree.column("Рейтинг", width=100)
        
        # Скроллбары
        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Размещение
        self.tree.grid(row=1, column=0, sticky="nsew")
        scrollbar_y.grid(row=1, column=1, sticky="ns")
        scrollbar_x.grid(row=2, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(1, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
    
    def create_filter_frame(self):
        """Создание панели фильтрации"""
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтр по жанру
        tk.Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, padx=5, pady=5)
        
        # Получение уникальных жанров
        genres = sorted(set([movie["genre"] for movie in self.movies]))
        genres.insert(0, "Все")
        
        self.filter_genre_var = tk.StringVar(value="Все")
        self.filter_genre_combo = ttk.Combobox(filter_frame, textvariable=self.filter_genre_var, 
                                               values=genres, width=20, state="readonly")
        self.filter_genre_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Фильтр по году
        tk.Label(filter_frame, text="Фильтр по году:").grid(row=0, column=2, padx=5, pady=5)
        
        # Получение уникальных годов
        years = sorted(set([movie["year"] for movie in self.movies]), reverse=True)
        years.insert(0, "Все")
        
        self.filter_year_var = tk.StringVar(value="Все")
        self.filter_year_combo = ttk.Combobox(filter_frame, textvariable=self.filter_year_var,
                                             values=years, width=15, state="readonly")
        self.filter_year_combo.grid(row=0, column=3, padx=5, pady=5)
        
        # Кнопки фильтрации
        tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filters,
                 bg="#2196F3", fg="white").grid(row=0, column=4, padx=5, pady=5)
        tk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters,
                 bg="#9E9E9E", fg="white").grid(row=0, column=5, padx=5, pady=5)
        
        # Обновление списков при добавлении новых фильмов
        self.update_filter_lists()
    
    def update_filter_lists(self):
        """Обновление списков для фильтров"""
        genres = sorted(set([movie["genre"] for movie in self.movies]))
        genres.insert(0, "Все")
        self.filter_genre_combo['values'] = genres
        
        years = sorted(set([movie["year"] for movie in self.movies]), reverse=True)
        years.insert(0, "Все")
        self.filter_year_combo['values'] = years

def main():
    """Запуск приложения"""
    root = tk.Tk()
    app = MovieLibrary(root)
    root.mainloop()

if __name__ == "__main__":
    main()
