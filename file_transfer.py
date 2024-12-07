#v1.1.0

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import socket
from threading import *
import pickle
from os import path
from sys import exit
from plyer import notification

def exit_program():
    root.destroy()
    exit()

def acpt():
    def acpt_func():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind(("0.0.0.0", 9999))
                server_socket.listen(1)
                root.after(0, lambda: acpt_curr_task.configure(text="Waiting for connection"))
                conn, addr = server_socket.accept()
                root.after(0, lambda: acpt_curr_task.configure(text=f"Connected to {addr}"))
                with conn:
                    filename = conn.recv(256).strip().decode()
                    root.after(0, lambda: acpt_curr_task.configure(text=f"File name ({filename}) received"))
                    file_size = int.from_bytes(conn.recv(8), 'big')
                    received_size = 0
                    acpt_progressbar["value"] = 0
                    with open(filename, 'wb') as f:
                        while True:
                            data = conn.recv(65536)
                            if not data:
                                break
                            f.write(data)
                            received_size += len(data)
                            progress_value = (received_size / file_size) * 100
                            root.after(0, acpt_progressbar.configure, {"value": progress_value})
                    root.after(0, lambda: acpt_curr_task.configure(text=f'The file "{filename}" has been saved successfully'))
                    notification.notify("Maya4ok's File Transfer", f'The file "{filename}" has been saved successfully')
        except Exception as e:
            root.after(0, lambda: acpt_curr_task.configure(text=f"Server error: {e}"))
    accept_thr = Thread(target=acpt_func, daemon=True)
    accept_thr.start()

def set_placeholder(entry, placeholder_text):
    def on_entry_click(event):
        if entry.get() == placeholder_text:
            entry.delete(0, tk.END)
            entry.config(fg='#D3D3D3')

    def on_focusout(event):
        if entry.get() == '':
            entry.insert(0, placeholder_text)
            entry.config(fg='grey')

    entry.insert(0, placeholder_text)
    entry.config(fg='grey')
    entry.bind('<FocusIn>', on_entry_click)
    entry.bind('<FocusOut>', on_focusout)

def send():
    global file_path
    try:
        print(file_path)
    except NameError:
        messagebox.showerror("Maya4ok's File Transfer", "First you need to open the file")
        return
    host = address_entry.get()
    try:
        with open("C:\\ProgramData\\file_transfer.dat", "wb") as file:
            pickle.dump(host, file)
    except Exception as e:
        messagebox.showerror("Maya4ok's File Transfer", f"Error saving IP: {e}")
        return

    def send_func():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((host, 9999))
                notification.notify("Maya4ok's File Transfer", f"Connected to {host}")
                root.after(0, lambda: send_curr_task.configure(text="Sending the file name"))
                filename = path.basename(file_path)
                filename = filename.encode().ljust(256)
                client_socket.sendall(filename)
                root.after(0, lambda: send_curr_task.configure(text="Sending a file"))
                size = path.getsize(file_path)
                client_socket.sendall(size.to_bytes(8, 'big'))
                sent_size = 0
                send_progressbar["value"] = 0
                with open(file_path, 'rb') as f:
                    while chunk := f.read(65536):
                        client_socket.sendall(chunk)
                        sent_size += len(chunk)
                        progress_value = (sent_size / size) * 100
                        root.after(0, lambda v=progress_value: send_progressbar.configure(value=v))
                root.after(0, lambda: send_curr_task.configure(text="The file has been sent successfully"))
                notification.notify("Maya4ok's File Transfer", "The file has been sent successfully")
        except Exception as e:
            messagebox.showerror("Maya4ok's File Transfer", f"Error: {e}")
    try:
        send_thr = Thread(target=send_func, daemon=True)
        send_thr.start()
    except Exception as e:
        messagebox.showerror("Maya4ok's File Transfer", f"Error: {e}")

def get_filename():
    global file_path
    file_path = filedialog.askopenfilename()
    if file_path:
        path_lbl.config(text=file_path)

def goto_menu():
    acpt_frame.pack_forget()
    send_frame.pack_forget()
    menu_frame.pack(fill="both", expand=True)

def goto_acpt_scene():
    acpt_frame.pack(fill="both", expand=True)
    send_frame.pack_forget()
    menu_frame.pack_forget()

def goto_send_scene():
    send_frame.pack(fill="both", expand=True)
    acpt_frame.pack_forget()
    menu_frame.pack_forget()

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

root = tk.Tk()
root.title("Maya4ok's File Transfer")
root.geometry("400x400")
root.resizable(False, False)

menu_frame = tk.Frame(root)
menu_label = tk.Label(menu_frame, text="Maya4ok's File Transfer", font=("Bahnschrift", 24))
menu_label.pack(pady=30)
goto_accept_btn = tk.Button(menu_frame, text="Accept", font=("Bahnschrift", 18), command=goto_acpt_scene, width=16, relief="flat")
goto_accept_btn.place(relx=0.5, rely=0.4, anchor="center")
goto_send_btn  = tk.Button(menu_frame, text="Send", font=("Bahnschrift", 18), command=goto_send_scene, width=16, relief="flat")
goto_send_btn .place(relx=0.5, rely=0.6, anchor="center")
exit_button = tk.Button(menu_frame, text="Exit", font=("Bahnschrift", 18), command=exit_program, relief="flat")
exit_button.pack(pady=10, padx=10, fill=tk.X, side="bottom")
menu_frame.pack(fill="both", expand=True)

acpt_frame = tk.Frame(root)
acpt_back_btn = tk.Button(acpt_frame, text="Back", font=("Bahnschrift", 18), command=goto_menu, relief="flat")
acpt_back_btn.pack(padx=10, pady=10, fill="both", side="bottom")
acpt_btn = tk.Button(acpt_frame, text="Accept file", command=acpt, font=("Bahnschrift", 18), relief="flat")
acpt_btn.pack(padx=10, pady=10, fill="both", side="bottom")
acpt_progressbar = ttk.Progressbar(acpt_frame, orient="horizontal", length=280, mode="determinate")
acpt_progressbar.pack(padx=10, pady=10, fill=tk.X)
acpt_curr_task = tk.Label(acpt_frame, wraplength=380, font=("Roboto", 16))
acpt_curr_task.pack(padx=10, pady=5, fill=tk.X)

send_frame = tk.Frame(root)
address_entry = tk.Entry(send_frame, font=("Bahnschrift", 18))
address_entry.pack(padx=10, pady=5, fill=tk.X)
try:
    with open ("C:\\ProgramData\\file_transfer.dat", "rb") as file:
        IP = pickle.load(file)
        address_entry.insert(0, IP)
except FileNotFoundError:
    set_placeholder(address_entry, "Recipient's IP address")
send_curr_task = tk.Label(send_frame, wraplength=380, font=("Bahnschrift", 16))
send_curr_task.pack(padx=10, pady=5, fill=tk.X)
send_back_btn = tk.Button(send_frame, text="Back", font=("Bahnschrift", 18), command=goto_menu, relief="flat")
send_back_btn.pack(padx=10, pady=10, fill=tk.X, side="bottom")
send_btn = tk.Button(send_frame, text="Send", font=("Bahnschrift", 18), command=send, relief="flat")
send_btn.pack(padx=10, pady=10, fill=tk.X, side="bottom")
filename_btn = tk.Button(send_frame, text="Open file", font=("Bahnschrift", 18), command=get_filename, relief="flat")
filename_btn.pack(padx=10, pady=10, fill=tk.X, side="bottom")
send_progressbar = ttk.Progressbar(send_frame, orient="horizontal", length=280, mode="determinate")
send_progressbar.pack(padx=10, pady=10, fill=tk.X, side="bottom")
path_lbl = tk.Label(send_frame, wraplength=380, font=("Bahnschrift", 12))
path_lbl.pack(fill=tk.X, side="bottom")

menu_label.configure(fg='#D3D3D3', bg='#2E2E2E')
send_curr_task.configure(fg='#D3D3D3', bg='#2E2E2E')
acpt_curr_task.configure(fg='#D3D3D3', bg='#2E2E2E')
path_lbl.configure(fg='#D3D3D3', bg='#2E2E2E')
send_curr_task.configure(fg='#D3D3D3', bg='#2E2E2E')
acpt_curr_task.configure(fg='#D3D3D3', bg='#2E2E2E')

root.configure(bg='#2E2E2E')
send_frame.configure(bg='#2E2E2E')
menu_frame.configure(bg='#2E2E2E')
acpt_frame.configure(bg='#2E2E2E')

goto_accept_btn.configure(bg='#3B5B73', fg='#FFFFFF', activebackground='#4A6C87', activeforeground='#FFFFFF')
send_btn.configure(bg='#3B5B73', fg='#FFFFFF', activebackground='#4A6C87', activeforeground='#FFFFFF')
exit_button.configure(bg='#B33D3D', fg='#FFFFFF', activebackground='#FF4C4C', activeforeground='#FFFFFF')
acpt_btn.configure(bg='#3B5B73', fg='#FFFFFF', activebackground='#4A6C87', activeforeground='#FFFFFF')
acpt_back_btn.configure(bg='#3B5B73', fg='#FFFFFF', activebackground='#4A6C87', activeforeground='#FFFFFF')
send_back_btn.configure(bg='#3B5B73', fg='#FFFFFF', activebackground='#4A6C87', activeforeground='#FFFFFF')
filename_btn.configure(bg='#3B5B73', fg='#FFFFFF', activebackground='#4A6C87', activeforeground='#FFFFFF')
goto_send_btn .configure(bg='#3B5B73', fg='#FFFFFF', activebackground='#4A6C87', activeforeground='#FFFFFF')

acpt_progressbar.configure(style="TProgressbar")
send_progressbar.configure(style="TProgressbar")
style = ttk.Style()
style.configure("TProgressbar", thickness=20, length=280, background="#3B5B73", troughcolor="#4A6C87")

address_entry.configure(bg='#333333', fg='#D3D3D3', insertbackground='white', relief="flat", justify="center")

center_window(root)
root.mainloop()
