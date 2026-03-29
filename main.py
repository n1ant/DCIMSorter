import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

import tkinter as tk
from tkinter import filedialog, messagebox
from sorter import sort_files

import threading
from tkinter import ttk


# ===== ЛОГИКА =====

def choose_input():
    if settings_window and settings_window.winfo_exists():
        bring_settings_to_front()
        return
    
    path = filedialog.askdirectory()
    if path:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, path)


def choose_output():
    if settings_window and settings_window.winfo_exists():
        bring_settings_to_front()
        return
    
    path = filedialog.askdirectory()
    if path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, path)


def run_sort():
    if settings_window and settings_window.winfo_exists():
        bring_settings_to_front()
        return
    
    input_dir = input_entry.get()
    output_dir = output_entry.get()

    if not input_dir or not output_dir:
        messagebox.showerror("Ошибка", "Выберите обе папки!")
        return

    show_progress()
    root.config(cursor="watch")

    def task():
        try:
            stats = sort_files(
                input_dir,
                output_dir,
                mode=mode_var.get(),
                move=(operation_var.get() == "move")
            )

            result_text = (
                f"Обработано: {stats['processed']}\n"
                f"Пропущено: {stats['skipped']}\n"
                f"Ошибки: {len(stats['errors'])}"
            )

            root.after(0, lambda: finish(result_text, output_dir))

        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Ошибка", str(e)))
        finally:
            root.after(0, reset_ui)

    threading.Thread(target=task, daemon=True).start()


def finish(result_text, output_dir):
    if messagebox.askyesno("Готово", result_text + "\n\nОткрыть папку результата?"):
        open_folder(output_dir)


progress_window = None


def show_progress():
    global progress_window

    progress_window = tk.Toplevel(root)
    progress_window.title("Выполнение...")
    progress_window.resizable(False, False)
    progress_window.withdraw()

    tk.Label(progress_window, text="Идёт обработка файлов...").pack(pady=10)

    bar = ttk.Progressbar(progress_window, mode="indeterminate")
    bar.pack(fill="x", padx=20, pady=10)
    bar.start()

    progress_window.update_idletasks()
    progress_window.geometry("300x100")

    center_window(progress_window, root)

    progress_window.deiconify()
    progress_window.lift()

    progress_window.grab_set()
    progress_window.transient(root)


def hide_progress():
    global progress_window
    if progress_window and progress_window.winfo_exists():
        progress_window.destroy()
        progress_window = None


def open_folder(path):
    import os
    os.startfile(path)


def reset_ui():
    hide_progress()
    root.config(cursor="")


# ===== НАСТРОЙКИ =====

settings_window = None
root_widgets_state = {}
root_close_handler = None
border_frame = None  # Рамка для подсветки


def disable_root_widgets():
    global root_widgets_state
    
    for widget in root.winfo_children():
        widget_type = widget.winfo_class()
        if widget_type in ("Button", "Entry", "Label"):
            root_widgets_state[widget] = widget.cget("state")
            try:
                widget.config(state="disabled")
            except:
                pass


def enable_root_widgets():
    global root_widgets_state
    
    for widget, state in root_widgets_state.items():
        if widget.winfo_exists():
            try:
                widget.config(state=state)
            except:
                pass
    
    root_widgets_state.clear()


def set_window_style_no_minmax(window):
    """Убирает кнопки сворачивания и разворачивания через Windows API"""
    try:
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        GWL_STYLE = -16
        WS_MINIMIZEBOX = 0x00020000
        WS_MAXIMIZEBOX = 0x00010000
        
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
        style &= ~WS_MINIMIZEBOX
        style &= ~WS_MAXIMIZEBOX
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)
        
        ctypes.windll.user32.SetWindowPos(
            hwnd, 0, 0, 0, 0, 0,
            0x0027
        )
    except:
        pass


def flash_window_border():
    if not settings_window or not settings_window.winfo_exists(): return
    
    t = 2
    c = "#0078D4"
    b = [tk.Frame(settings_window, bg=c) for _ in range(4)]
    b[0].place(x=0, y=0, relwidth=1, height=t)
    b[1].place(x=0, rely=1, anchor="sw", relwidth=1, height=t)
    b[2].place(x=0, y=0, relheight=1, width=t)
    b[3].place(relx=1, y=0, anchor="ne", relheight=1, width=t)
    
    def flash(n):
        if n >= 6: [x.destroy() for x in b]; return
        [x.config(bg=c if n%2==0 else settings_window.cget("bg")) for x in b]
        settings_window.after(100, lambda: flash(n+1))
    flash(0)


def bring_settings_to_front():
    """Поднимает окно настроек поверх всех + звук + фокус + подсветка"""
    if settings_window and settings_window.winfo_exists():
        root.bell()
        
        if settings_window.state() == "iconic":
            settings_window.deiconify()
        
        settings_window.lift()
        settings_window.focus_force()
        settings_window.attributes("-topmost", True)
        root.after(200, lambda: settings_window.attributes("-topmost", False))
        
        # Цветная подсветка рамки
        flash_window_border()


def on_root_focus(event):
    """При фокусе на главное окно — поднимаем настройки"""
    if settings_window and settings_window.winfo_exists():
        bring_settings_to_front()


def open_settings():
    global settings_window, root_close_handler

    if settings_window is not None and settings_window.winfo_exists():
        bring_settings_to_front()
        return

    root_close_handler = root.protocol("WM_DELETE_WINDOW")

    disable_root_widgets()
    root.protocol("WM_DELETE_WINDOW", lambda: root.bell())

    settings_window = tk.Toplevel(root)
    settings_window.title("Настройки")
    settings_window.resizable(False, False)
    settings_window.configure(bg="#F0F0F0")  # Светлый фон для контраста рамки
    
    root.after(100, lambda: set_window_style_no_minmax(settings_window))
    
    settings_window.withdraw()

    tk.Label(settings_window, text="Режим сортировки:", bg="#F0F0F0").pack(pady=5)

    tk.Radiobutton(
        settings_window,
        text="Иерархический",
        variable=mode_var,
        value="hierarchical",
        bg="#F0F0F0"
    ).pack(anchor="w", padx=20)

    tk.Radiobutton(
        settings_window,
        text="Плоский",
        variable=mode_var,
        value="flat",
        bg="#F0F0F0"
    ).pack(anchor="w", padx=20)

    tk.Label(settings_window, text="Способ обработки:", bg="#F0F0F0").pack(pady=5)

    tk.Radiobutton(
        settings_window,
        text="Копирование файлов",
        variable=operation_var,
        value="copy",
        bg="#F0F0F0"
    ).pack(anchor="w", padx=20)

    tk.Radiobutton(
        settings_window,
        text="Перемещение файлов",
        variable=operation_var,
        value="move",
        bg="#F0F0F0"
    ).pack(anchor="w", padx=20)

    settings_window.update_idletasks()
    settings_window.geometry("300x240")

    center_window(settings_window, root)

    settings_window.deiconify()
    settings_window.lift()
    settings_window.attributes("-topmost", True)
    root.after(200, lambda: settings_window.attributes("-topmost", False))

    root.bind("<FocusIn>", on_root_focus)

    def on_close():
        global settings_window, border_frame
        
        root.unbind("<FocusIn>")
        
        if border_frame and border_frame.winfo_exists():
            border_frame.destroy()
        
        if root_close_handler:
            root.protocol("WM_DELETE_WINDOW", root_close_handler)
        
        enable_root_widgets()
        
        settings_window.destroy()
        settings_window = None

    settings_window.protocol("WM_DELETE_WINDOW", on_close)


def center_window(child, parent):
    parent.update_idletasks()

    parent_x = parent.winfo_x()
    parent_y = parent.winfo_y()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()

    child_width = child.winfo_width()
    child_height = child.winfo_height()

    x = parent_x + (parent_width - child_width) // 2
    y = parent_y + (parent_height - child_height) // 2

    child.geometry(f"+{x}+{y}")


# ===== GUI =====

root = tk.Tk()
root.title("DCIM Sorter")
root.geometry("500x300")
root.minsize(500, 300)
root.resizable(True, True)

tk.Label(root, text="Папка DCIM:").pack()
input_entry = tk.Entry(root, width=50)
input_entry.pack()
tk.Button(root, text="Выбрать...", command=choose_input).pack()

tk.Label(root, text="Куда сохранить:").pack()
output_entry = tk.Entry(root, width=50)
output_entry.pack()
tk.Button(root, text="Выбрать...", command=choose_output).pack()

tk.Button(root, text="⚙ Настройки", command=open_settings).pack(pady=15)

operation_var = tk.StringVar(value="copy")
mode_var = tk.StringVar(value="hierarchical")

tk.Button(root, text="Запустить", command=run_sort, bg="green", fg="white").pack(pady=10)

root.mainloop()