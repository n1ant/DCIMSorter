import os
import tempfile
from datetime import datetime
from utils import *
from sorter import sort_files


def unit_tests():
    print("=== ТЕСТЫ ===")

    # extract_date
    assert extract_date_from_name("IMG_20240101_123045.jpg")
    assert extract_date_from_name("file.jpg") is None

    # supported
    assert is_supported_file("a.jpg")
    assert not is_supported_file("a.txt")

    # build_path
    d = datetime(2023, 5, 10)
    assert "2023" in build_path("out", d)

    # unique path
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "file.jpg")
        open(path, "w").close()

        new_path = make_unique_path(path)
        assert new_path != path

    # sort_files
    with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
        # создаём тестовые файлы
        open(os.path.join(input_dir, "IMG_20240101_123045.jpg"), "w").close()
        open(os.path.join(input_dir, "file.txt"), "w").close()

        stats = sort_files(input_dir, output_dir)

        assert stats["processed"] == 1
        assert stats["skipped"] == 1

    print("Все тесты пройдены!")


if __name__ == "__main__":
    unit_tests()