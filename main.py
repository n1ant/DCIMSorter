from sorter import sort_files
from tests import unit_tests


def main():
    print("=== DCIM SORTER ===")

    input_dir = input("Введите путь к папке DCIM: ").strip()
    output_dir = input("Введите путь для сохранения: ").strip()

    mode = input("Формат (1 - YYYY/MM/DD, 2 - YYYY-MM-DD): ").strip()
    mode = "hierarchical" if mode == "1" else "linear"

    action = input("Копировать или перемещать? (c/m): ").strip().lower()
    move = True if action == "m" else False

    unit_tests()
    sort_files(input_dir, output_dir, mode, move)

    print("Готово!")


if __name__ == "__main__":
    main()