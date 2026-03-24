import os
import shutil
from utils import (
    is_supported_file,
    get_file_date,
    build_path,
    make_unique_path
)


def sort_files(input_dir, output_dir, mode="hierarchical", move=False):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # ВАЖНО: os.walk проходит ВСЕ подпапки DCIM
    for root, _, files in os.walk(input_dir):
        for file in files:
            if not is_supported_file(file):
                continue

            full_path = os.path.join(root, file)

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

            except Exception as e:
                print(f"Ошибка: {file} -> {e}")