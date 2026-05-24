# Đọc và xuất file trong Python.
import os

def read_write_file():
    filename = "test_file.txt"
    # Ghi file
    with open(filename, "w", encoding="utf-8") as f:
        f.write("Xin chào Python!\nĐây là dòng thứ 2.")
    
    # Đọc file
    print("Nội dung file:")
    with open(filename, "r", encoding="utf-8") as f:
        print(f.read())
        
if __name__ == "__main__":
    read_write_file()
