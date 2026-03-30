import os
import re
from datetime import datetime
from typing import Optional

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


def is_supported_file(filename: str) -> bool:
    """
    Проверяет, поддерживается ли файл по расширению.
    
    Args:
        filename: Имя файла для проверки
        
    Returns:
        True если расширение файла в списке поддерживаемых, иначе False
    """
    return filename.lower().endswith(SUPPORTED_EXTENSIONS)


def extract_date_from_name(filename: str) -> Optional[datetime]:
    """
    Извлекает дату из имени файла по паттерну YYYYMMDD_HHMMSS.
    
    Args:
        filename: Имя файла для анализа
        
    Returns:
        datetime объект если дата найдена, иначе None
    """
    match = re.search(r'(\d{8})[_-]?(\d{6})', filename)
    if match:
        try:
            return datetime.strptime(match.group(1) + match.group(2), "%Y%m%d%H%M%S")
        except ValueError:
            return None
    return None


def get_file_date(filepath: str) -> datetime:
    """
    Определяет дату файла: сначала из имени, затем fallback на mtime.
    
    Args:
        filepath: Полный путь к файлу
        
    Returns:
        datetime объект даты файла
    """
    filename = os.path.basename(filepath)
    date = extract_date_from_name(filename)
    if date:
        return date

    timestamp = os.path.getmtime(filepath)
    return datetime.fromtimestamp(timestamp)


def build_path(base_dir: str, date: datetime, mode: str = "hierarchical") -> str:
    """
    Строит путь назначения для файла на основе даты.
    
    Args:
        base_dir: Базовая директория для сортировки
        date: Дата файла для построения пути
        mode: Режим сортировки ("hierarchical" или "flat")
        
    Returns:
        Полный путь к целевой директории
    """
    if mode == "hierarchical":
        return os.path.join(
            base_dir,
            str(date.year),
            f"{date.month:02}",
            f"{date.day:02}"
        )
    else:
        return os.path.join(
            base_dir,
            f"{date.year}-{date.month:02}-{date.day:02}"
        )


def make_unique_path(filepath: str) -> str:
    """
    Создаёт уникальный путь файла, добавляя счётчик при конфликте имён.
    
    Args:
        filepath: Исходный путь файла
        
    Returns:
        Уникальный путь (оригинальный или с добавленным счётчиком)
    """
    base, ext = os.path.splitext(filepath)
    counter = 1
    new_path = filepath
    
    while os.path.exists(new_path):
        new_path = f"{base}_{counter}{ext}"
        counter += 1

    return new_path