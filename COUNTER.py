import os

def count_code_lines(root_dir="."):
    total_code_lines = 0
    file_counts = []

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        code_lines = 0
                        for line in f:
                            stripped = line.strip()
                            if stripped and not stripped.startswith("#"):
                                code_lines += 1
                        total_code_lines += code_lines
                        file_counts.append((filename, code_lines))
                except Exception as e:
                    print(f"Hiba a(z) {filename} fájl olvasásakor: {e}")

    print("\n--- Kódsorok fájlonként ---")
    for name, count in sorted(file_counts, key=lambda x: -x[1]):
        print(f"{name.ljust(25)} : {count} sor")

    print("\nÖsszesen:", total_code_lines, "kódsor")

if __name__ == "__main__":
    count_code_lines()
