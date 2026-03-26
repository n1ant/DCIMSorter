import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

import tkinter as tk
from tkinter import filedialog, messagebox
from sorter import sort_files


def choose_input():
    path = filedialog.askdirectory()
    if path:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, path)


def choose_output():
    path = filedialog.askdirectory()
    if path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, path)


def run_sort():
    input_dir = input_entry.get()
    output_dir = output_entry.get()

    if not input_dir or not output_dir:
        messagebox.showerror("Ошибка", "Выберите обе папки!")
        return

    try:
        sort_files(input_dir, output_dir, mode="hierarchical", move=False)
        messagebox.showinfo("Готово", "Файлы успешно отсортированы!")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))


# === GUI ===
root = tk.Tk()
root.title("DCIM Sorter")
root.geometry("500x250")
root.minsize(500, 250)
root.resizable(True, True)

# INPUT
tk.Label(root, text="Папка DCIM:").pack()
input_entry = tk.Entry(root, width=50)
input_entry.pack()
tk.Button(root, text="Выбрать...", command=choose_input).pack()

# OUTPUT
tk.Label(root, text="Куда сохранить:").pack()
output_entry = tk.Entry(root, width=50)
output_entry.pack()
tk.Button(root, text="Выбрать...", command=choose_output).pack()

# RUN
tk.Button(root, text="Запустить", command=run_sort, bg="green", fg="white").pack(pady=10)

root.mainloop()