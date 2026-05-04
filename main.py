import tkinter as tk
from tkinter import messagebox, ttk
import requests
import json
import webbrowser
import os

# --- Конфигурация ---
API_URL = "https://api.github.com/users/"
FAVORITES_FILE = "favorites.json"

# --- Работа с избранным (JSON) ---
def load_favorites():
    """Загружает список избранных пользователей из файла."""
    if os.path.exists(FAVORITES_FILE):
        try:
            with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_favorites(favorites):
    """Сохраняет список избранных пользователей в файл."""
    with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
        json.dump(favorites, f, ensure_ascii=False, indent=4)

# --- Логика приложения ---
def search_user():
    """Выполняет поиск пользователя по введенному логину."""
    username = entry_username.get().strip()
    
    # 5. Проверка корректности ввода
    if not username:
        messagebox.showwarning("Ошибка", "Поле поиска не должно быть пустым.")
        return

    # Очистка предыдущих результатов
    for widget in frame_results.winfo_children():
        widget.destroy()

    try:
        response = requests.get(API_URL + username)
        response.raise_for_status() # Проверка на HTTP-ошибки (например, 404)
        user_data = response.json()
        
        # Отображение аватара
        avatar_response = requests.get(user_data['avatar_url'])
        avatar_label = tk.Label(frame_results)
        avatar_label.image = tk.PhotoImage(data=avatar_response.content)
        avatar_label.config(image=avatar_label.image)
        avatar_label.grid(row=0, column=0, rowspan=4, padx=10, pady=10)

        # Отображение информации о пользователе
        tk.Label(frame_results, text=f"Логин: {user_data['login']}", font=('Arial', 12, 'bold')).grid(row=0, column=1, sticky='w', columnspan=2)
        tk.Label(frame_results, text=f"Имя: {user_data.get('name', 'Не указано')}").grid(row=1, column=1, sticky='w')
        tk.Label(frame_results, text=f"Подписчики: {user_data['followers']} | Репозитории: {user_data['public_repos']}").grid(row=2, column=1, sticky='w')
        
        # Кнопка для открытия профиля в браузере
        btn_open = tk.Button(frame_results, text="Открыть профиль", 
                            command=lambda url=user_data['html_url']: webbrowser.open(url))
        btn_open.grid(row=3, column=1, pady=5)

        # Кнопка добавления в избранное
        btn_fav = tk.Button(frame_results, text="Добавить в избранное", 
                           command=lambda data=user_data: add_to_favorites(data))
        btn_fav.grid(row=3, column=2, pady=5)

    except requests.exceptions.HTTPError as err:
        if response.status_code == 404:
            messagebox.showerror("Ошибка", f"Пользователь '{username}' не найден.")
        else:
            messagebox.showerror("Ошибка API", f"Код ошибки: {err}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")

def add_to_favorites(user_data):
    """Добавляет пользователя в список избранного."""
    favorites = load_favorites()
    
    # Проверка на дубликаты по логину
    if any(user['login'] == user_data['login'] for user in favorites):
        messagebox.showinfo("Информация", f"Пользователь {user_data['login']} уже в избранном.")
        return

    favorites.append(user_data)
    save_favorites(favorites)
    messagebox.showinfo("Успех", f"Пользователь {user_data['login']} добавлен в избранное.")

def show_favorites():
    """Открывает новое окно со списком избранных пользователей."""
    favorites = load_favorites()
    
    if not favorites:
        messagebox.showinfo("Избранное", "В избранном пока нет пользователей.")
        return

    fav_window = tk.Toplevel(root)
    fav_window.title("Избранные пользователи")
    fav_window.geometry("500x400")

    tree = ttk.Treeview(fav_window, columns=('login', 'name'), show='headings')
    tree.heading('login', text='Логин')
    tree.heading('name', text='Имя')
    tree.column('login', width=200)
    tree.column('name', width=280)
    
    for user in favorites:
        tree.insert('', 'end', values=(user['login'], user.get('name', 'Не указано')))
    
    tree.pack(fill='both', expand=True, padx=10, pady=10)

# --- Создание графического интерфейса ---
root = tk.Tk()
root.title("GitHub User Finder")
root.geometry("650x500")
root.resizable(False, False)

# Верхняя панель (Поле ввода и кнопка поиска)
frame_top = tk.Frame(root)
frame_top.pack(pady=10)

tk.Label(frame_top, text="Введите логин пользователя GitHub:").pack(side='left')
entry_username = tk.Entry(frame_top, width=35)
entry_username.pack(side='left', padx=5)
btn_search = tk.Button(frame_top, text="Поиск", command=search_user)
btn_search.pack(side='left')

# Кнопка для просмотра избранного
btn_fav_list = tk.Button(root, text="Показать избранное", command=show_favorites)
btn_fav_list.pack(pady=5)

# Рамка для отображения результатов поиска
frame_results = tk.Frame(root, bg='#f0f0f0')
frame_results.pack(pady=20, fill='x')

# Запуск приложения
root.mainloop()
