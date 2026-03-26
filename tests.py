import os
from datetime import datetime
from utils import extract_date_from_name, is_supported_file, build_path


def unit_tests():
    print("Запуск unit-тестов...")

    assert extract_date_from_name("IMG_20240101_123045.jpg") is not None
    assert extract_date_from_name("file.jpg") is None

    assert is_supported_file("photo.jpg")
    assert not is_supported_file("doc.txt")

    d = datetime(2023, 5, 10)
    assert "2023" in build_path("out", d)

    print("Все тесты пройдены!")

if __name__ == "__main__":
    unit_tests()