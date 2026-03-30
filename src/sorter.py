import os
import shutil
import time
from typing import Dict, Callable, Optional
from utils import is_supported_file, get_file_date, build_path, make_unique_path


def sort_files(
    input_dir: str,
    output_dir: str,
    mode: str = "hierarchical",
    move: bool = False,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    stop_flag: Optional[Callable[[], bool]] = None
) -> Dict:
    """
    Сортирует файлы из входной директории в выходную по дате.
    
    Args:
        input_dir: Путь к исходной директории с файлами
        output_dir: Путь к целевой директории для сортировки
        mode: Режим сортировки ("hierarchical" или "flat")
        move: Если True, файлы перемещаются, иначе копируются
        progress_callback: Функция обратного вызова (current, total) для обновления прогресса
        stop_flag: Функция, возвращающая True если нужно остановить сортировку
        
    Returns:
        Словарь статистики:
            - processed: количество успешно обработанных файлов
            - skipped: количество неподдерживаемых файлов
            - errors: список ошибок с полными путями файлов
    """
    unsorted_dir = os.path.join(output_dir, "_unsorted")
    
    stats = {
        "processed": 0,
        "skipped": 0,
        "errors": []
    }
    
    unsorted_created = False
    action: Callable = shutil.move if move else shutil.copy2
    
    # Считаем общее количество файлов заранее
    total_files = 0
    for _, _, files in os.walk(input_dir):
        total_files += len(files)
    
    if total_files == 0:
        return stats
    
    processed_count = 0
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for dir_root, _, files in os.walk(input_dir):
        for file in files:
            # ПРОВЕРЯЕМ ФЛАГ ОСТАНОВКИ ПЕРЕД КАЖДЫМ ФАЙЛОМ
            if stop_flag and stop_flag():
                return stats  # НЕМЕДЛЕННО ВОЗВРАЩАЕМ
            
            full_path = os.path.join(dir_root, file)
            processed_count += 1

            if progress_callback:
                progress_callback(processed_count, total_files)

            if not is_supported_file(file):
                stats["skipped"] += 1
                
                if not unsorted_created:
                    os.makedirs(unsorted_dir, exist_ok=True)
                    unsorted_created = True

                try:
                    target_path = os.path.join(unsorted_dir, file)
                    target_path = make_unique_path(target_path)
                    shutil.copy2(full_path, target_path)
                except Exception as e:
                    stats["errors"].append(f"{full_path}: {str(e)}")

                continue

            try:
                date = get_file_date(full_path)
                target_dir = build_path(output_dir, date, mode)

                os.makedirs(target_dir, exist_ok=True)

                target_path = os.path.join(target_dir, file)
                target_path = make_unique_path(target_path)

                action(full_path, target_path)
                stats["processed"] += 1

            except Exception as e:
                stats["errors"].append(f"{full_path}: {str(e)}")

                if not unsorted_created:
                    os.makedirs(unsorted_dir, exist_ok=True)
                    unsorted_created = True
                    
                try:
                    fallback_path = os.path.join(unsorted_dir, file)
                    fallback_path = make_unique_path(fallback_path)
                    shutil.copy2(full_path, fallback_path)
                except Exception:
                    pass

    return stats