# Viết chương trình nhập vào một chuỗi ký tự. Xuất tất cả các ký tự ở vị trí chẵn.
def main():
    chuoi = input("Nhập chuỗi: ")
    print("Các ký tự ở vị trí chẵn:", chuoi[::2])

if __name__ == "__main__":
    main()
