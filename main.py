import os
import sys
import ctypes
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from sorter import sort_files
import threading

# DPI-awareness только для Windows
if os.name == "nt":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

# ===== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ =====

settings_window = None
progress_window = None
progress_label = None
progress_bar = None
root_widgets_state = {}
root_close_handler = None
border_frame = None

operation_var = None
mode_var = None
input_entry = None
output_entry = None
root = None

# ФЛАГ ОСТАНОВКИ СОРТИРОВКИ
stop_sorting = False
sort_thread = None


# ===== ЛОГИКА =====

def choose_input():
    """Открывает диалог выбора входной директории."""
    if settings_window and settings_window.winfo_exists():
        bring_settings_to_front()
        return
    path = filedialog.askdirectory()
    if path:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, path)


def choose_output():
    """Открывает диалог выбора выходной директории."""
    if settings_window and settings_window.winfo_exists():
        bring_settings_to_front()
        return
    path = filedialog.askdirectory()
    if path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, path)


def run_sort():
    """Запускает процесс сортировки в отдельном потоке."""
    global stop_sorting, sort_thread
    
    if stop_sorting and sort_thread and sort_thread.is_alive():
        messagebox.showwarning("Подождите", "Предыдущая сортировка ещё завершается!")
        return
    
    if settings_window and settings_window.winfo_exists():
        bring_settings_to_front()
        return
    
    input_dir = input_entry.get()
    output_dir = output_entry.get()

    if not input_dir or not output_dir:
        messagebox.showerror("Ошибка", "Выберите обе папки!")
        return

    # СБРАСЫВАЕМ ФЛАГ ОСТАНОВКИ
    stop_sorting = False
    disable_root_widgets()
    root.config(cursor="watch")

    show_progress()

    def task():
        global stop_sorting
        
        def update_progress(current, total):
            """Обновляет прогресс-бар (вызывается из потока сортировки)."""
            percentage = int((current / total) * 100) if total > 0 else 0
            root.after(0, lambda: set_progress(current, total, percentage))
        
        try:
            stats = sort_files(
                input_dir,
                output_dir,
                mode=mode_var.get(),
                move=(operation_var.get() == "move"),
                progress_callback=update_progress,
                stop_flag=lambda: stop_sorting  # ПЕРЕДАЁМ ФЛАГ ОСТАНОВКИ
            )

            # ПОКАЗЫВАЕМ РЕЗУЛЬТАТ ТОЛЬКО ЕСЛИ НЕ ПРЕРВАЛИ
            if not stop_sorting:
                result_text = (
                    f"✅ Обработано: {stats['processed']}\n"
                    f"⏭️ Пропущено: {stats['skipped']}\n"
                    f"⚠️ Ошибки: {len(stats['errors'])}"
                )

                if stats['errors']:
                    result_text += "\n\nФайлы с ошибками сохранены в _unsorted"

                root.after(0, lambda: finish(result_text, output_dir))

        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Ошибка", str(e)))
        finally:
            root.after(0, reset_ui)

    sort_thread = threading.Thread(target=task, daemon=True)
    sort_thread.start()


def set_progress(current, total, percentage):
    """Обновляет текст и значение прогресс-бара."""
    global progress_label, progress_bar
    if progress_label and progress_label.winfo_exists():
        progress_label.config(text=f"Обработка: {current} из {total} файлов ({percentage}%)")
    if progress_bar and progress_bar.winfo_exists():
        progress_bar.config(value=percentage)


def finish(result_text, output_dir):
    """Показывает результат и предлагает открыть папку."""
    if messagebox.askyesno("Готово!", result_text + "\n\nОткрыть папку результата?"):
        open_folder(output_dir)


def show_progress():
    """Показывает окно прогресса обработки."""
    global progress_window, progress_label, progress_bar
    progress_window = tk.Toplevel(root)
    progress_window.title("Выполнение...")
    progress_window.resizable(False, False)
    progress_window.withdraw()

    tk.Label(progress_window, text="📁 Сортировка файлов...", font=("Arial", 10, "bold")).pack(pady=10)

    progress_label = tk.Label(progress_window, text="Обработка: 0 из 0 файлов (0%)", font=("Consolas", 9))
    progress_label.pack(pady=5)

    progress_bar = ttk.Progressbar(progress_window, mode="determinate", length=250)
    progress_bar.pack(fill="x", padx=20, pady=10)
    progress_bar.config(value=0)

    progress_window.update_idletasks()
    progress_window.geometry("350x120")

    center_window(progress_window, root)

    progress_window.deiconify()
    progress_window.lift()
    progress_window.transient(root)
    
    progress_window.protocol("WM_DELETE_WINDOW", on_progress_close)


def on_progress_close():
    """
    Обработчик закрытия окна прогресса.
    Прерывает сортировку и освобождает файлы.
    """
    global stop_sorting
    
    root.bell()
    
    if messagebox.askyesno(
        "⚠️ Прерывание работы",
        "Сортировка файлов ещё не завершена!\n\n"
        "Прерывание процесса может привести к:\n"
        "   • Частичной обработке файлов\n"
        "   • Файлам в исходной папке (режим move)\n"
        "   • Повреждению данных\n\n"
        "Прервать сортировку и вернуться в главное окно?",
        icon="warning"
    ):
        # УСТАНАВЛИВАЕМ ФЛАГ ОСТАНОВКИ
        stop_sorting = True
        
        # ЖДЁМ ЗАВЕРШЕНИЯ ПОТОКА (максимум 3 секунды)
        if sort_thread and sort_thread.is_alive():
            sort_thread.join(timeout=3.0)
        
        hide_progress()
        enable_root_widgets()
        root.config(cursor="")


def hide_progress():
    """Скрывает окно прогресса."""
    global progress_window, progress_label, progress_bar
    if progress_window and progress_window.winfo_exists():
        progress_window.destroy()
    progress_window = None
    progress_label = None
    progress_bar = None


def open_folder(path):
    """
    Открывает папку в файловом менеджере (кроссплатформенно).
    
    Args:
        path: Путь к папке для открытия
    """
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            os.system(f'open "{path}"')
        else:  # Linux
            os.system(f'xdg-open "{path}"')
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть папку:\n{str(e)}")


def reset_ui():
    """Сбрасывает UI в исходное состояние."""
    hide_progress()
    root.config(cursor="")
    enable_root_widgets()


# ===== НАСТРОЙКИ =====

def disable_root_widgets():
    """Блокирует все виджеты главного окна."""
    global root_widgets_state
    for widget in root.winfo_children():
        widget_type = widget.winfo_class()
        if widget_type in ("Button", "Entry", "Label"):
            root_widgets_state[widget] = widget.cget("state")
            try:
                widget.config(state="disabled")
            except Exception:
                pass


def enable_root_widgets():
    """Разблокирует все виджеты главного окна."""
    global root_widgets_state
    for widget, state in root_widgets_state.items():
        if widget.winfo_exists():
            try:
                widget.config(state=state)
            except Exception:
                pass

    root_widgets_state.clear()


def set_window_style_no_minmax(window):
    """Убирает кнопки сворачивания и разворачивания через Windows API."""
    if os.name != "nt":
        return
        
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
    except Exception:
        pass


def flash_window_border():
    """Эффект подсветки рамки окна настроек."""
    if not settings_window or not settings_window.winfo_exists():
        return
    
    t = 2
    c = "#0078D4"
    b = [tk.Frame(settings_window, bg=c) for _ in range(4)]
    b[0].place(x=0, y=0, relwidth=1, height=t)
    b[1].place(x=0, rely=1, anchor="sw", relwidth=1, height=t)
    b[2].place(x=0, y=0, relheight=1, width=t)
    b[3].place(relx=1, y=0, anchor="ne", relheight=1, width=t)

    def flash(n):
        if n >= 6:
            [x.destroy() for x in b]
            return
        [x.config(bg=c if n % 2 == 0 else settings_window.cget("bg")) for x in b]
        settings_window.after(100, lambda: flash(n + 1))
    
    flash(0)


def bring_settings_to_front():
    """Поднимает окно настроек поверх всех + звук + фокус + подсветка."""
    if settings_window and settings_window.winfo_exists():
        root.bell()
        
        if settings_window.state() == "iconic":
            settings_window.deiconify()
        
        settings_window.lift()
        settings_window.focus_force()
        settings_window.attributes("-topmost", True)
        root.after(200, lambda: settings_window.attributes("-topmost", False))
        
        flash_window_border()


def bring_progress_to_front():
    """Поднимает окно прогресса на передний план + звук."""
    if progress_window and progress_window.winfo_exists():
        root.bell()
        
        if progress_window.state() == "iconic":
            progress_window.deiconify()
        
        progress_window.lift()
        progress_window.focus_force()
        progress_window.attributes("-topmost", True)
        root.after(200, lambda: progress_window.attributes("-topmost", False))


def on_root_focus(event):
    """При фокусе на главное окно — поднимаем настройки."""
    if settings_window and settings_window.winfo_exists():
        bring_settings_to_front()


def open_settings():
    """Открывает окно настроек сортировки."""
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
    settings_window.configure(bg="#F0F0F0")

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
    """Центрирует дочернее окно относительно родительского."""
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

tk.Label(root, text="📂 Папка DCIM:").pack()
input_entry = tk.Entry(root, width=50)
input_entry.pack()
tk.Button(root, text="Выбрать...", command=choose_input).pack()

tk.Label(root, text="📁 Куда сохранить:").pack()
output_entry = tk.Entry(root, width=50)
output_entry.pack()
tk.Button(root, text="Выбрать...", command=choose_output).pack()

tk.Button(root, text="⚙ Настройки", command=open_settings).pack(pady=15)

operation_var = tk.StringVar(value="copy")
mode_var = tk.StringVar(value="hierarchical")

tk.Button(root, text="Запустить", command=run_sort, bg="green", fg="white", font=("Arial", 10, "bold")).pack(pady=10)

def on_root_close():
    if stop_sorting and sort_thread and sort_thread.is_alive():
        bring_progress_to_front()
    else:
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_root_close)

root.mainloop()