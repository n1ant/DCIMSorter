import os
import shutil
from utils import is_supported_file, get_file_date, build_path, make_unique_path


def sort_files(input_dir, output_dir, mode="hierarchical", move=False):
    unsorted_dir = os.path.join(output_dir, "_unsorted")
    os.makedirs(unsorted_dir, exist_ok=True)
    
    """
    Сортирует файлы и возвращает статистику
    """
    stats = {
        "processed": 0,
        "skipped": 0,
        "errors": []
    }

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for root, _, files in os.walk(input_dir):
        for file in files:
            full_path = os.path.join(root, file)

            if not is_supported_file(file):
                stats["skipped"] += 1

                try:
                    target_path = os.path.join(unsorted_dir, file)
                    target_path = make_unique_path(target_path)

                    if move:
                        shutil.move(full_path, target_path)
                    else:
                        shutil.copy2(full_path, target_path)

                except Exception as e:
                    stats["errors"].append(f"{file}: {str(e)}")

                continue

            try:
                date = get_file_date(full_path)
                target_dir = build_path(output_dir, date, mode)

                os.makedirs(target_dir, exist_ok=True)

                target_path = os.path.join(target_dir, file)
                target_path = make_unique_path(target_path)

                if move:
                    shutil.move(full_path, target_path)
                else:
                    shutil.copy2(full_path, target_path)

                stats["processed"] += 1

            except Exception as e:
                stats["errors"].append(f"{file}: {str(e)}")

                try:
                    fallback_path = os.path.join(unsorted_dir, file)
                    fallback_path = make_unique_path(fallback_path)
                    shutil.copy2(full_path, fallback_path)
                except:
                    pass

    return stats