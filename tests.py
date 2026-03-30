import os
import tempfile
from datetime import datetime
from utils import (
    extract_date_from_name,
    is_supported_file,
    build_path,
    make_unique_path,
    get_file_date
)
from sorter import sort_files


def unit_tests():
    """Запускает все unit-тесты проекта."""
    print("=== ТЕСТЫ ===")
    
    # ===== extract_date =====
    print("Тест: extract_date_from_name...")
    assert extract_date_from_name("IMG_20240101_123045.jpg") is not None
    assert extract_date_from_name("file.jpg") is None
    assert extract_date_from_name("IMG-20230510-180000.png") is not None
    print("  ✓ extract_date_from_name")
    
    # ===== supported =====
    print("Тест: is_supported_file...")
    assert is_supported_file("a.jpg")
    assert is_supported_file("a.HEIC")
    assert is_supported_file("video.mp4")
    assert not is_supported_file("a.txt")
    assert not is_supported_file("document.pdf")
    print("  ✓ is_supported_file")
    
    # ===== build_path =====
    print("Тест: build_path...")
    d = datetime(2023, 5, 10)
    
    path_h = build_path("out", d, mode="hierarchical")
    assert "2023" in path_h
    assert "05" in path_h
    assert "10" in path_h
    
    path_f = build_path("out", d, mode="flat")
    assert "2023-05-10" in path_f
    print("  ✓ build_path")
    
    # ===== unique path =====
    print("Тест: make_unique_path...")
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "file.jpg")
        open(path, "w").close()

        new_path = make_unique_path(path)
        assert new_path != path
        assert new_path.endswith("_1.jpg")
        
        open(new_path, "w").close()
        new_path2 = make_unique_path(path)
        assert new_path2.endswith("_2.jpg")
    print("  ✓ make_unique_path")
    
    # ===== sort_files: basic =====
    print("Тест: sort_files (basic)...")
    with tempfile.TemporaryDirectory() as input_dir, \
         tempfile.TemporaryDirectory() as output_dir:
        
        open(os.path.join(input_dir, "IMG_20240101_123045.jpg"), "w").close()
        open(os.path.join(input_dir, "file.txt"), "w").close()

        stats = sort_files(input_dir, output_dir)

        assert stats["processed"] == 1
        assert stats["skipped"] == 1
        assert len(stats["errors"]) == 0
    print("  ✓ sort_files (basic)")
    
    # ===== sort_files: nested folders =====
    print("Тест: sort_files (nested folders)...")
    with tempfile.TemporaryDirectory() as input_dir, \
         tempfile.TemporaryDirectory() as output_dir:
        
        nested = os.path.join(input_dir, "subfolder", "deep")
        os.makedirs(nested)
        
        open(os.path.join(input_dir, "IMG_20240101_123045.jpg"), "w").close()
        open(os.path.join(nested, "IMG_20240202_100000.jpg"), "w").close()
        open(os.path.join(nested, "doc.txt"), "w").close()

        stats = sort_files(input_dir, output_dir)

        assert stats["processed"] == 2
        assert stats["skipped"] == 1
    print("  ✓ sort_files (nested folders)")
    
    # ===== sort_files: empty directory =====
    print("Тест: sort_files (empty directory)...")
    with tempfile.TemporaryDirectory() as input_dir, \
         tempfile.TemporaryDirectory() as output_dir:
        
        stats = sort_files(input_dir, output_dir)

        assert stats["processed"] == 0
        assert stats["skipped"] == 0
        assert len(stats["errors"]) == 0
    print("  ✓ sort_files (empty directory)")
    
    # ===== sort_files: flat mode =====
    print("Тест: sort_files (flat mode)...")
    with tempfile.TemporaryDirectory() as input_dir, \
         tempfile.TemporaryDirectory() as output_dir:
        
        open(os.path.join(input_dir, "IMG_20240101_123045.jpg"), "w").close()

        stats = sort_files(input_dir, output_dir, mode="flat")

        assert stats["processed"] == 1
        
        flat_dir = os.path.join(output_dir, "2024-01-01")
        assert os.path.exists(flat_dir)
    print("  ✓ sort_files (flat mode)")
    
    # ===== sort_files: move mode =====
    print("Тест: sort_files (move mode)...")
    with tempfile.TemporaryDirectory() as input_dir, \
         tempfile.TemporaryDirectory() as output_dir:
        
        src_file = os.path.join(input_dir, "IMG_20240101_123045.jpg")
        open(src_file, "w").close()

        stats = sort_files(input_dir, output_dir, move=True)

        assert stats["processed"] == 1
        assert not os.path.exists(src_file)
    print("  ✓ sort_files (move mode)")
    
    # ===== sort_files: _unsorted lazy creation =====
    print("Тест: sort_files (_unsorted lazy creation)...")
    with tempfile.TemporaryDirectory() as input_dir, \
         tempfile.TemporaryDirectory() as output_dir:
        
        open(os.path.join(input_dir, "IMG_20240101_123045.jpg"), "w").close()
        
        stats = sort_files(input_dir, output_dir)
        
        unsorted_path = os.path.join(output_dir, "_unsorted")
        assert not os.path.exists(unsorted_path)
    print("  ✓ sort_files (_unsorted lazy creation - no need)")
    
    # ===== sort_files: _unsorted created on skip =====
    print("Тест: sort_files (_unsorted on skipped files)...")
    with tempfile.TemporaryDirectory() as input_dir, \
         tempfile.TemporaryDirectory() as output_dir:
        
        open(os.path.join(input_dir, "IMG_20240101_123045.jpg"), "w").close()
        open(os.path.join(input_dir, "skip.txt"), "w").close()

        stats = sort_files(input_dir, output_dir)
        
        unsorted_path = os.path.join(output_dir, "_unsorted")
        assert os.path.exists(unsorted_path)
        assert os.path.exists(os.path.join(unsorted_path, "skip.txt"))
    print("  ✓ sort_files (_unsorted on skipped files)")
    
    # ===== sort_files: name conflicts =====
    print("Тест: sort_files (name conflicts)...")
    with tempfile.TemporaryDirectory() as input_dir, \
         tempfile.TemporaryDirectory() as output_dir:
        
        sub = os.path.join(input_dir, "sub")
        os.makedirs(sub)
        
        open(os.path.join(input_dir, "IMG_20240101_123045.jpg"), "w").close()
        open(os.path.join(sub, "IMG_20240101_123045.jpg"), "w").close()

        stats = sort_files(input_dir, output_dir)

        assert stats["processed"] == 2
        
        target_dir = os.path.join(output_dir, "2024", "01", "01")
        assert os.path.exists(os.path.join(target_dir, "IMG_20240101_123045.jpg"))
        assert os.path.exists(os.path.join(target_dir, "IMG_20240101_123045_1.jpg"))
    print("  ✓ sort_files (name conflicts)")
    
    # ===== sort_files: unsupported formats =====
    print("Тест: sort_files (unsupported formats)...")
    with tempfile.TemporaryDirectory() as input_dir, \
         tempfile.TemporaryDirectory() as output_dir:
        
        open(os.path.join(input_dir, "doc.pdf"), "w").close()
        open(os.path.join(input_dir, "archive.zip"), "w").close()
        open(os.path.join(input_dir, "IMG_20240101_123045.jpg"), "w").close()

        stats = sort_files(input_dir, output_dir)

        assert stats["skipped"] == 2
        assert stats["processed"] == 1
        
        unsorted_path = os.path.join(output_dir, "_unsorted")
        assert os.path.exists(os.path.join(unsorted_path, "doc.pdf"))
        assert os.path.exists(os.path.join(unsorted_path, "archive.zip"))
    print("  ✓ sort_files (unsupported formats)")
    
    # ===== get_file_date fallback =====
    print("Тест: get_file_date (mtime fallback)...")
    with tempfile.TemporaryDirectory() as tmp:
        filepath = os.path.join(tmp, "no_date_file.jpg")
        open(filepath, "w").close()
        
        date = get_file_date(filepath)
        assert date is not None
        assert isinstance(date, datetime)
    print("  ✓ get_file_date (mtime fallback)")
    
    print("\n✅ Все тесты пройдены!")


if __name__ == "__main__":
    unit_tests()