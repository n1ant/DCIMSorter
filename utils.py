import os
import re
from datetime import datetime

SUPPORTED_EXTENSIONS = (
    # фото
    '.jpg', '.jpeg', '.png', '.webp',
    '.heic', '.heif',
    '.bmp', '.tiff', '.tif',
    '.dng', '.raw', '.arw', '.cr2', '.nef',

    # видео
    '.mp4', '.mov', '.avi',
    '.mkv', '.wmv',
    '.flv', '.webm',
    '.3gp', '.m4v'
)


def is_supported_file(filename):
    """Проверяет, поддерживается ли файл по расширению"""
    return filename.lower().endswith(SUPPORTED_EXTENSIONS)


def extract_date_from_name(filename):
    """Извлекает дату из имени файла"""
    match = re.search(r'(\d{8})[_-]?(\d{6})', filename)
    if match:
        try:
            return datetime.strptime(match.group(1) + match.group(2), "%Y%m%d%H%M%S")
        except ValueError:
            return None
    return None


def get_file_date(filepath):
    """Определяет дату файла (имя -> fallback на mtime)"""
    filename = os.path.basename(filepath)

    date = extract_date_from_name(filename)
    if date:
        return date

    timestamp = os.path.getmtime(filepath)
    return datetime.fromtimestamp(timestamp)


def build_path(base_dir, date, mode="hierarchical"):
    """Строит путь назначения"""
    if mode == "hierarchical":
        return os.path.join(base_dir, str(date.year), f"{date.month:02}", f"{date.day:02}")
    else:
        return os.path.join(base_dir, f"{date.year}-{date.month:02}-{date.day:02}")


def make_unique_path(filepath):
    """Избегает конфликтов имён"""
    base, ext = os.path.splitext(filepath)
    counter = 1

    new_path = filepath
    while os.path.exists(new_path):
        new_path = f"{base}_{counter}{ext}"
        counter += 1

    return new_path