import tkinter as tk
from tkinter import filedialog, messagebox
from plyer import notification
import socket
from threading import *
FONT = ("Roboto Medium", 16)

def accept_wrapper():
    def accept_thr():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.settimeout(60)
                server_socket.bind(("0.0.0.0", 9999))
                server_socket.listen(1)
                root.after(0, lambda: current_task2.configure(text="Сервер запущен."))
                
                conn, addr = server_socket.accept()
                root.after(0, lambda: current_task2.configure(text=f"Подключение от {addr}"))
                
                with conn, open(file_entry.get(), 'wb') as f:
                    while True:
                        data = conn.recv(4096)
                        if not data:
                            break
                        f.write(data)
                root.after(0, lambda: current_task2.configure(text="Файл сохранён"))
        except Exception as e:
            root.after(0, lambda: current_task2.configure(text=f"Ошибка сервера: {e}"))
    
    accept_thread = Thread(target=accept_thr, daemon=True)
    accept_thread.start()


def set_placeholder(entry, placeholder_text):
    def on_entry_click(event):
        if entry.get() == placeholder_text:
            entry.delete(0, tk.END)
            entry.config(fg='black')

    def on_focusout(event):
        if entry.get() == '':
            entry.insert(0, placeholder_text)
            entry.config(fg='grey')

    entry.insert(0, placeholder_text)
    entry.config(fg='grey')
    entry.bind('<FocusIn>', on_entry_click)
    entry.bind('<FocusOut>', on_focusout)

def send():
    def send_thr():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((host, 9999))
                root.after(0, lambda: current_task1.configure(text=f"Подключено к {host}:9999"))
                with open(file_path, 'rb') as f:
                    while chunk := f.read(4096):
                        client_socket.sendall(chunk)
                root.after(0, lambda: current_task1.configure(text="Файл успешно отправлен"))
        except Exception as e:
            root.after(0, lambda: current_task1.configure(text=f"Ошибка клиента: {e}"))
    
    global file_path
    if not file_path:
        current_task1.configure(text="Ошибка: файл не выбран!")
        return
    host = ip_entry.get()
    if not host:
        current_task1.configure(text="Ошибка: IP адрес не указан!")
        return
    try:
        send_thread = Thread(target=send_thr, daemon=True)
        send_thread.start()
    except Exception as e:
        current_task1.configure(text=f"Ошибка клиента: {e}")

        
def filename():
    global file_path
    file_path = filedialog.askopenfilename()
    if file_path:
        label_file.config(text=file_path)

def show_menu():
    accept_frame.pack_forget()
    send_frame.pack_forget()
    menu_frame.pack(fill="both", expand=True)

# Функция для отображения сцены 1
def show_accept():
    accept_frame.pack(fill="both", expand=True)
    send_frame.pack_forget()
    menu_frame.pack_forget()

# Функция для отображения сцены 2
def show_send():
    send_frame.pack(fill="both", expand=True)
    accept_frame.pack_forget()
    menu_frame.pack_forget()

# Функция для выхода из игры
def exit_game():
    root.quit()

# функция для центрирования окна
def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

root = tk.Tk()  # главное окно с поддержкой drag-and-drop
root.title("Maya4ok's File Transfer")
root.geometry("400x400")
root.resizable(False, False)

# Создание фрейма меню
menu_frame = tk.Frame(root)
menu_label = tk.Label(menu_frame, text="Maya4ok's File Transfer", font=("Roboto Medium", 24))
menu_label.pack(pady=30)
accept_scene_button = tk.Button(menu_frame, text="Принять", font=("Roboto Medium", 18), command=show_accept)
accept_scene_button.pack(pady=10, padx=10, fill="x")
send_button = tk.Button(menu_frame, text="Отправить", font=("Roboto Medium", 18), command=show_send)
send_button.pack(pady=10, padx=10, fill="x")
exit_button = tk.Button(menu_frame, text="Выход", font=("Roboto Medium", 18), command=exit_game)
exit_button.pack(pady=10, padx=10, fill="x", side="bottom")
menu_frame.pack(fill="both", expand=True)

# Создание фрейма получения файла
accept_frame = tk.Frame(root)
back_button1 = tk.Button(accept_frame, text="Назад", font=("Roboto Medium", 18), command=show_menu)
back_button1.pack(padx=10, pady=10, fill="both", side="bottom")
accept_button = tk.Button(accept_frame, text="Принять файл", command=accept_wrapper, font=("Roboto Medium", 18))
accept_button.pack(padx=10, pady=10, fill="both", side="bottom")
file_entry = tk.Entry(accept_frame, font=("Roboto Medium", 18))
file_entry.pack(padx=10, pady=5, fill="x")
current_task2 = tk.Label(accept_frame, wraplength=380, font=("Roboto Medium", 12), text="")
current_task2.pack(padx=10, pady=5, fill="x")
set_placeholder(file_entry, "Название файла")

# Создание фрейма отправки файла
send_frame = tk.Frame(root)
ip_entry = tk.Entry(send_frame, font=("Roboto Medium", 18))
ip_entry.pack(padx=10, pady=5, fill="x")
set_placeholder(ip_entry, "Адрес сети компьютера клиента")
current_task1 = tk.Label(send_frame, font=("Roboto Medium", 16), text="")
current_task1.pack(padx=10, pady=5, fill="x")
back_button2 = tk.Button(send_frame, text="Назад", font=("Roboto Medium", 18), command=show_menu)
back_button2.pack(padx=10, pady=10, fill="x", side="bottom")
send_button = tk.Button(send_frame, text="Отправить", font=("Roboto Medium", 18), command=send)
send_button.pack(padx=10, pady=10, fill="x", side="bottom")
filename_button = tk.Button(send_frame, text="Выбрать файл", font=("Roboto Medium", 18), command=filename)
filename_button.pack(padx=10, pady=10, fill="x", side="bottom")
label_file = tk.Label(send_frame, wraplength=380, text="", font=("Roboto Medium", 12))
label_file.pack(fill="x", side="bottom")

center_window(root)
root.mainloop()
