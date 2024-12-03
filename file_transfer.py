import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import socket
from threading import *
import pickle
from os import path
from sys import exit

def exit_program():
    root.destroy()
    exit()

# функция принятия файла
# не разбираюсь в этом вашем сокете, так что коменты внутри функции делать особо не собираюсь
def accept_wrapper():
    def accept_thr():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind(("0.0.0.0", 9999))
                server_socket.listen(1)
                root.after(0, lambda: current_task2.configure(text="Ожидание подключения"))
                conn, addr = server_socket.accept()
                root.after(0, lambda: current_task2.configure(text=f"Подключено к {addr}"))
                with conn:
                    # получение имени файла
                    file_name = conn.recv(256).strip().decode()
                    root.after(0, lambda: current_task2.configure(text=f"Название файла ({file_name}) получено"))
                    # получение размера файла
                    file_size = int.from_bytes(conn.recv(8), 'big')
                    received_size = 0
                    progress["value"] = 0  # сбросить прогресс
                    with open(file_name, 'wb') as f:
                        while True:
                            data = conn.recv(4096)
                            if not data:
                                break
                            f.write(data)
                            received_size += len(data)
                            progress_value = (received_size / file_size) * 100
                            root.after(0, progress.configure, {"value": progress_value})
                    root.after(0, lambda: current_task2.configure(text=f"Файл '{file_name}' успешно сохранён"))
        except Exception as e:
            root.after(0, lambda: current_task2.configure(text=f"Ошибка сервера: {e}"))
    accept_thread = Thread(target=accept_thr, daemon=True)
    accept_thread.start()

# функция подсказок в Entry, 
# нужно для того, чтобы новый пользователь сразу понял как пользоваться
def set_placeholder(entry, placeholder_text):
    # сделать текст обычным, если в фокусе
    def on_entry_click(event):
        if entry.get() == placeholder_text:
            entry.delete(0, tk.END)
            entry.config(fg='black')

    # сделать текст серым и установить подсказку если не в фокусе
    def on_focusout(event):
        if entry.get() == '':
            entry.insert(0, placeholder_text)
            entry.config(fg='grey')
    
    # текст по умолчанию
    entry.insert(0, placeholder_text)
    entry.config(fg='grey')
    # привязка функций к фокусу и расфокусу
    entry.bind('<FocusIn>', on_entry_click)
    entry.bind('<FocusOut>', on_focusout)

def send():
    global file_path
    try:
        print(file_path)  # Проверка, что file_path определён
    except NameError:
        messagebox.showerror("Maya4ok's File Transfer", "Сначала нужно открыть файл (просто нажать по кнопке)")
        return

    host = ip_entry.get()

    # Сохранение IP-адреса в файл
    try:
        with open(path.expanduser("~\\appdata\\roaming\\file_transfer.dat"), "wb") as file:
            pickle.dump(host, file)
    except Exception as e:
        messagebox.showerror("Maya4ok's File Transfer", f"Ошибка сохранения IP: {e}")
        return

    def send_thr():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((host, 9999))
                root.after(0, lambda: current_task1.configure(text=f"Подключено к {host}"))
                # Отправка имени файла
                file_name = path.basename(file_path)
                file_name = file_name.encode().ljust(256)
                client_socket.sendall(file_name)
                root.after(0, lambda: current_task1.configure(text="Отправлено название файла"))
                # Отправка размера файла
                file_size = path.getsize(file_path)
                client_socket.sendall(file_size.to_bytes(8, 'big'))
                root.after(0, lambda: current_task1.configure(text="Отправлен размер файла, отправление файла"))
                # Отправка содержимого файла
                sent_size = 0
                progress_send["value"] = 0  # Сбросить прогресс
                with open(file_path, 'rb') as f:
                    while chunk := f.read(4096):
                        client_socket.sendall(chunk)
                        sent_size += len(chunk)
                        progress_value = (sent_size / file_size) * 100
                        root.after(0, lambda v=progress_value: progress_send.configure(value=v))
                root.after(0, lambda: current_task1.configure(text="Файл успешно отправлен"))
        except Exception as e:
            messagebox.showerror("Maya4ok's File Transfer", f"Ошибка: {e}")
    try:
        send_thread = Thread(target=send_thr, daemon=True)
        send_thread.start()
    except Exception as e:
        messagebox.showerror("Maya4ok's File Transfer", f"Ошибка: {e}")


# выбор файла для получения пути
# кстати, сначала был обычный ввод, и это неудобно
def filename():
    global file_path
    file_path = filedialog.askopenfilename()
    if file_path:
        label_file.config(text=file_path)

# показать главное меню
def show_menu():
    accept_frame.pack_forget()
    send_frame.pack_forget()
    menu_frame.pack(fill="both", expand=True)

# показать меню принятия файла
def show_accept():
    accept_frame.pack(fill="both", expand=True)
    send_frame.pack_forget()
    menu_frame.pack_forget()

# показать меню отправки файла
def show_send():
    send_frame.pack(fill="both", expand=True)
    accept_frame.pack_forget()
    menu_frame.pack_forget()

# функция центрирования окна
def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

# создать окно, в этом нету ничего сложного
root = tk.Tk()
root.title("Maya4ok's File Transfer")
root.geometry("400x400")
root.resizable(False, False)

# главное меню
menu_frame = tk.Frame(root)
menu_label = tk.Label(menu_frame, text="Maya4ok's File Transfer", font=("Roboto Medium", 24))
menu_label.pack(pady=30)
accept_scene_button = tk.Button(menu_frame, text="Принять", font=("Roboto Medium", 18), command=show_accept, width=16, relief="flat")
accept_scene_button.place(relx=0.5, rely=0.4, anchor="center")
show_send_frame_button = tk.Button(menu_frame, text="Отправить", font=("Roboto Medium", 18), command=show_send, width=16, relief="flat")
show_send_frame_button.place(relx=0.5, rely=0.6, anchor="center")
exit_button = tk.Button(menu_frame, text="Выход", font=("Roboto Medium", 18), command=exit_program, relief="flat")
exit_button.pack(pady=10, padx=10, fill="x", side="bottom")
menu_frame.pack(fill="both", expand=True)

# меню получения
accept_frame = tk.Frame(root)
back_button1 = tk.Button(accept_frame, text="Назад", font=("Roboto Medium", 18), command=show_menu, relief="flat")
back_button1.pack(padx=10, pady=10, fill="both", side="bottom")
accept_button = tk.Button(accept_frame, text="Принять файл", command=accept_wrapper, font=("Roboto Medium", 18), relief="flat")
accept_button.pack(padx=10, pady=10, fill="both", side="bottom")
current_task2 = tk.Label(accept_frame, wraplength=380, font=("Roboto", 16))
current_task2.pack(padx=10, pady=5, fill="x")
progress = ttk.Progressbar(accept_frame, orient="horizontal", length=280, mode="determinate")
progress.pack(padx=10, pady=10, fill="x", side="bottom")

# меню отправки
send_frame = tk.Frame(root)
ip_entry = tk.Entry(send_frame, font=("Roboto Medium", 18))
ip_entry.pack(padx=10, pady=5, fill="x")
with open(path.expanduser("~\\appdata\\roaming\\file_transfer.dat"), "rb") as file:
    try:
        ip_text = pickle.load(file)
        ip_entry.insert(0, ip_text)
    except:
        set_placeholder(ip_entry, "Адрес сети получателя")
current_task1 = tk.Label(send_frame, wraplength=380, font=("Roboto", 16))  # текущий процесс при отправке файла
current_task1.pack(padx=10, pady=5, fill="x")
back_button2 = tk.Button(send_frame, text="Назад", font=("Roboto Medium", 18), command=show_menu, relief="flat")
back_button2.pack(padx=10, pady=10, fill="x", side="bottom")
send_button = tk.Button(send_frame, text="Отправить", font=("Roboto Medium", 18), command=send, relief="flat")
send_button.pack(padx=10, pady=10, fill="x", side="bottom")
filename_button = tk.Button(send_frame, text="Выбрать файл", font=("Roboto Medium", 18), command=filename, relief="flat")
filename_button.pack(padx=10, pady=10, fill="x", side="bottom")
progress_send = ttk.Progressbar(send_frame, orient="horizontal", length=280, mode="determinate")
progress_send.pack(padx=10, pady=10, fill="x", side="bottom")
label_file = tk.Label(send_frame, wraplength=380, font=("Roboto Medium", 12))
label_file.pack(fill="x", side="bottom")

# текст
menu_label.configure(fg='#D3D3D3', bg='#2E2E2E')
current_task1.configure(fg='#D3D3D3', bg='#2E2E2E')
current_task2.configure(fg='#D3D3D3', bg='#2E2E2E')
label_file.configure(fg='#D3D3D3', bg='#2E2E2E')
current_task1.configure(fg='#D3D3D3', bg='#2E2E2E')
current_task2.configure(fg='#D3D3D3', bg='#2E2E2E')

# настройка цветовой схемы
root.configure(bg='#2E2E2E')
send_frame.configure(bg='#2E2E2E')
menu_frame.configure(bg='#2E2E2E')
accept_frame.configure(bg='#2E2E2E')

# кнопки
accept_scene_button.configure(bg='#3B5B73', fg='#FFFFFF', activebackground='#4A6C87')
send_button.configure(bg='#3B5B73', fg='#FFFFFF', activebackground='#4A6C87')
exit_button.configure(bg='#B33D3D', fg='#FFFFFF', activebackground='#FF4C4C')
accept_button.configure(bg='#3B5B73', fg='#FFFFFF', activebackground='#4A6C87')
back_button1.configure(bg='#3B5B73', fg='#FFFFFF', activebackground='#4A6C87')
back_button2.configure(bg='#3B5B73', fg='#FFFFFF', activebackground='#4A6C87')
filename_button.configure(bg='#3B5B73', fg='#FFFFFF', activebackground='#4A6C87')
show_send_frame_button.configure(bg='#3B5B73', fg='#FFFFFF', activebackground='#4A6C87')

# прогресс-бары
progress.configure(style="TProgressbar")
progress_send.configure(style="TProgressbar")
style = ttk.Style()
style.configure("TProgressbar", thickness=20, length=280, background="#3B5B73", troughcolor="#4A6C87")

# Ввод
ip_entry.configure(bg='#333333', fg='#D3D3D3', insertbackground='white', relief="flat", justify="center")  # Фон и текст

center_window(root)
root.mainloop()
