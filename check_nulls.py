
import os

def check_for_null_bytes(start_path):
    corrupted_files = []
    for root, dirs, files in os.walk(start_path):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, 'rb') as f:
                        content = f.read()
                        if b'\x00' in content:
                            print(f"FOUND NULL BYTES: {path}")
                            corrupted_files.append(path)
                except Exception as e:
                    print(f"Error reading {path}: {e}")
    
    if not corrupted_files:
        print("No null bytes found in any .py files.")

if __name__ == "__main__":
    check_for_null_bytes("src")
