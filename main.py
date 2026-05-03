```python
import tkinter as tk
from tkinter import ttk, messagebox
import json

MOVIES_FILE = 'movies.json'

def load_movies():
    try:
        with open(MOVIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_movies(data):
    with open(MOVIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def validate_input():
    title = entry_title.get().strip()
    genre = entry_genre.get().strip()
    year = entry_year.get().strip()
    rating = entry_rating.get().strip()

    if not title or not genre:
        messagebox.showerror("Ошибка", "Название и жанр не должны быть пустыми.")
        return False

    if not year.isdigit() or not (1800 <= int(year) <= 2100):
        messagebox.showerror("Ошибка", "Год должен быть числом от 1800 до 2100.")
        return False

    if not (rating.replace('.', '', 1).isdigit() and 0 <= float(rating) <= 10):
        messagebox.showerror("Ошибка", "Рейтинг должен быть числом от 0 до 10.")
        return False

    return True

def add_movie():
    if validate_input():
        movie = {
            "title": entry_title.get(),
            "genre": entry_genre.get(),
            "year": int(entry_year.get()),
            "rating": float(entry_rating.get())
        }
        movies.append(movie)
        save_movies(movies)
        refresh_table()
        clear_fields()

def refresh_table(filter_genre=None, filter_year=None):
    for item in tree.get_children():
        tree.delete(item)
    for movie in movies:
        if filter_genre and movie["genre"].lower() != filter_genre.lower():
            continue
        if filter_year and movie["year"] != int(filter_year):
            continue
        tree.insert("", "end", values=(movie["title"], movie["genre"], movie["year"], movie["rating"]))

def apply_filters():
    genre = entry_filter_genre.get().strip() if entry_filter_genre.get().strip() else None
    year = entry_filter_year.get().strip() if entry_filter_year.get().strip() else None
    refresh_table(genre, year)

def clear_fields():
    entry_title.delete(0, tk.END)
    entry_genre.delete(0, tk.END)
    entry_year.delete(0, tk.END)
    entry_rating.delete(0, tk.END)

movies = load_movies()

root = tk.Tk()
root.title("Movie Library")
root.geometry("800x500")

tab_control = ttk.Notebook(root)
tab_main = ttk.Frame(tab_control)
tab_filter = ttk.Frame(tab_control)
tab_control.add(tab_main, text="Добавить фильм")
tab_control.add(tab_filter, text="Фильтр")
tab_control.pack(expand=1, fill="both")

# Вкладка "Добавить фильм"
tk.Label(tab_main, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_title = tk.Entry(tab_main, width=40)
entry_title.grid(row=0, column=1, padx=5, pady=5)

tk.Label(tab_main, text="Жанр:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_genre = tk.Entry(tab_main, width=40)
entry_genre.grid(row=1, column=1, padx=5, pady=5)

tk.Label(tab_main, text="Год выпуска:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
entry_year = tk.Entry(tab_main, width=40)
entry_year.grid(row=2, column=1, padx=5, pady=5)

tk.Label(tab_main, text="Рейтинг (0-10):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
entry_rating = tk.Entry(tab_main, width=40)
entry_rating.grid(row=3, column=1, padx=5, pady=5)

btn_add = ttk.Button(tab_main, text="Добавить фильм", command=add_movie)
btn_add.grid(row=4, column=0, columnspan=2, pady=10)

tree = ttk.Treeview(tab_main, columns=("Название", "Жанр", "Год", "Рейтинг"), show="headings")
for col in ("Название", "Жанр", "Год", "Рейтинг"):
    tree.heading(col, text=col)
tree.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
scrollbar = ttk.Scrollbar(tab_main, orient="vertical", command=tree.yview)
scrollbar.grid(row=5, column=2, sticky="ns")
tree.configure(yscrollcommand=scrollbar.set)

# Вкладка "Фильтр"
tk.Label(tab_filter, text="Жанр:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_filter_genre = tk.Entry(tab_filter)
entry_filter_genre.grid(row=0, column=1, padx=5, pady=5)

tk.Label(tab_filter, text="Год выпуска:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_filter_year = tk.Entry(tab_filter)
entry_filter_year.grid(row=1, column=1, padx=5, pady=5)

btn_apply = ttk.Button(tab_filter, text="Применить фильтр", command=apply_filters)
btn_apply.grid(row=2, column=0, columnspan=2, pady=10)

refresh_table()
root.mainloop()
```
